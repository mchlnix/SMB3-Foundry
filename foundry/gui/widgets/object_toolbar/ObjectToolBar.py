"""Coordinate the object-placement toolbar for the level editor.

This module owns :class:`ObjectToolBar`, the widget that keeps the recent,
object, and enemy palettes aligned with the larger "current object" preview
used for middle-click placement. The toolbar sits between level-header render
context changes and placement-time object reuse: object-set changes rebuild
tab contents, graphics or palette changes refresh preview art, and palette
clicks update the active placement object without forcing the user to re-open
the catalog flow manually.

See Also
--------
foundry.gui.widgets.object_toolbar.TabbedToolBox
    Hosts the recent, object, and enemy tabs that the toolbar coordinates.
foundry.gui.ObjectDropdown
    Alternative object-selection surface that rebuilds catalogs from the same
    level-header context.
foundry.gui.LevelSelector
    Higher-level editor workflow that eventually drives the level context used
    by the object-placement surfaces.
"""

from PySide6.QtCore import Qt, Signal, SignalInstance
from PySide6.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QWidget

from foundry.game.gfx.objects.in_level.enemy_item import EnemyItem
from foundry.game.gfx.objects.in_level.enemy_item_factory import EnemyItemFactory
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from foundry.game.gfx.objects.in_level.level_object import LevelObject
from foundry.game.gfx.objects.in_level.level_object_factory import LevelObjectFactory
from foundry.game.gfx.objects.object_like import ObjectLike

from .ObjectToolBox import ObjectIcon
from .TabbedToolBox import TabbedToolBox


class ObjectToolBar(QWidget):
    """Coordinate object-palette tabs with the active placement choice.

    The toolbar owns the tabbed object/enemy palettes and the larger preview of
    the object that middle-click placement will use in the level view. Changing
    object set rebuilds incompatible palette contents; changing only graphics
    set refreshes existing object previews. The recent-object tab and preview
    panel preserve the placement workflow humans use while editing: pick from a
    palette once, then place repeatedly from the active-object slot.

    Parameters
    ----------
    parent : QWidget, optional
        Parent Qt widget that owns this object.

    Attributes
    ----------
    _graphic_set_index : int
        Graphics set now used by level-object previews.
    _object_set_index : int
        Object set now loaded into the palette tabs.
    current_object_icon : ObjectIcon
        Preview icon for the active placement object.
    current_object_name : QLabel
        Label showing the active placement object name.
    object_selected : SignalInstance
        Signal emitted with the object selected for placement.
    tabbed_tool_box : TabbedToolBox
        Recent, object, and enemy palette tabs.
    """

    object_selected: SignalInstance = Signal(ObjectLike)

    def __init__(self, parent=None):
        """Create the object toolbar.

        Construction proceeds in three stages: build the active-object preview,
        build the tabbed palette surface, and then connect palette clicks back
        into the toolbar's selection pipeline.
        That staging matters because later level-header updates reuse the same
        preview widgets and tab container instead of rebuilding the entire
        placement surface, while object clicks still need one top-level widget
        to synchronize preview state, recent-object history, and the emitted
        placement choice.

        Parameters
        ----------
        parent : QWidget, optional
            Parent Qt widget that owns this object.
        """
        super(ObjectToolBar, self).__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)

        self.current_object_icon = ObjectIcon()
        self.current_object_icon.max_size = self.current_object_icon.MAX_SIZE

        self.current_object_name = QLabel()
        self.current_object_name.setWordWrap(True)
        self.current_object_name.setAlignment(Qt.AlignCenter)
        self.current_object_name.setContentsMargins(0, 0, 0, 0)

        current_item_widget = QGroupBox()
        current_item_widget.setContentsMargins(5, 10, 5, 5)
        current_item_widget.setFixedWidth(self.current_object_icon.MAX_SIZE.width() * 2)

        current_item_widget.setWhatsThis(
            "<b>Current Object</b><br/>"
            "Shows the currently selected object and its name. It can be placed by "
            "clicking the middle mouse button anywhere in the level."
        )

        current_item_layout = QVBoxLayout(current_item_widget)
        current_item_layout.addWidget(self.current_object_icon, alignment=Qt.AlignCenter)
        current_item_layout.addWidget(self.current_object_name, alignment=Qt.AlignCenter)

        self.tabbed_tool_box = TabbedToolBox()
        self.tabbed_tool_box.object_icon_clicked.connect(self._on_object_icon_selected)

        layout.addWidget(self.tabbed_tool_box, stretch=1)
        layout.addWidget(current_item_widget)

        self._object_set_index = -1
        self._graphic_set_index = -1

    # TODO: Just give level reference?
    def set_object_set(self, object_set_index: int, graphic_set_index: int, palette_group_index: int):
        """Reload toolbar catalogs from one level-header render context.

        A new object set requires rebuilding the object and enemy tabs because
        SMB3 definitions differ by set. A graphics-only change leaves the
        logical objects intact, so the toolbar refreshes icon art in place and
        preserves whichever object is already selected for placement.
        That lets header and palette edits refresh previews without disrupting
        the object a person is in the middle of placing.
        In practice this method is the toolbar's main intake path for level-header
        changes: level settings update render context, this method refreshes
        tabs and preview state, and placement can continue without reselection.

        Parameters
        ----------
        object_set_index : int
            Index of the object set.
        graphic_set_index : int
            Index of the graphic set.
        palette_group_index : int
            Index of the palette group.
        """
        needs_full_update = self._object_set_index != object_set_index

        self._object_set_index = object_set_index
        self._graphic_set_index = graphic_set_index

        if needs_full_update:
            self.tabbed_tool_box.set_object_set(object_set_index, graphic_set_index, palette_group_index)

        else:
            self.tabbed_tool_box.set_graphic_set(graphic_set_index, palette_group_index)

            self._update_currently_selected_object_icon(object_set_index, graphic_set_index, palette_group_index)

    def _update_currently_selected_object_icon(
        self, object_set_index: int, graphic_set_index: int, palette_group_index: int
    ):
        # TODO Could this be put into the level icon class itself?

        """Rebuild the large placement preview from one render context.

        The active object preview is a cached placement object, so it must be
        regenerated through the appropriate factory when graphics or palette
        context changes.
        This keeps the large preview aligned with the same decoded art context
        as the toolbar tabs and the object that would be emitted for placement
        if a person clicked immediately after the header change.

        Parameters
        ----------
        object_set_index : int
            Index of the object set.
        graphic_set_index : int
            Index of the graphic set.
        palette_group_index : int
            Index of the palette group.

        Raises
        ------
        ValueError
            If the preview object is neither a level object nor an
            enemy item.
        """
        current_object = self.current_object_icon.object

        if current_object is None:
            return

        if isinstance(current_object, LevelObject):
            lvl_factory = LevelObjectFactory(
                object_set_index,
                graphic_set_index,
                palette_group_index,
                [],
                vertical_level=False,
                size_minimal=True,
            )

            new_object = lvl_factory.from_properties(current_object.domain, current_object.obj_index, 0, 0, None, 0)

        elif isinstance(current_object, EnemyItem):
            enemy_factory = EnemyItemFactory(object_set_index, palette_group_index)

            new_object = enemy_factory.from_properties(current_object.obj_index, 0, 0)

        else:
            raise ValueError(f"Unknown object type: {type(current_object)}")

        self.current_object_icon.set_object(new_object)

    def _on_object_icon_selected(self, object_icon: ObjectIcon):
        """Select a clicked icon and broadcast it as the placement choice.

        Parameters
        ----------
        object_icon : ObjectIcon
            Clicked icon from a toolbar tab.
        """
        if object_icon.object is None:
            return

        self.select_object(object_icon.object)

        self.object_selected.emit(object_icon.object)

    def select_object(self, level_object: InLevelObject):
        """Make an object the active placement choice when the palette knows it.

        The toolbar resolves the incoming object to the equivalent object owned
        by the loaded tabs so the preview, tab selection, and recent-object list
        all reference the same palette instance.

        Parameters
        ----------
        level_object : InLevelObject
            Level object being displayed or modified.
        """
        if not isinstance(level_object, (LevelObject, EnemyItem)):
            return

        if (level_object := self.tabbed_tool_box.get_equivalent(level_object)) is None:
            return

        self.tabbed_tool_box.select_object(level_object)

        self.current_object_icon.set_object(level_object)
        self.current_object_name.setText(level_object.name)
        self.add_recent_object(level_object)

    def add_recent_object(self, level_object: InLevelObject):
        """Move an object to the front of the recent palette.

        Parameters
        ----------
        level_object : InLevelObject
            Level object being displayed or modified.
        """
        self.tabbed_tool_box.add_recent_object(level_object)
