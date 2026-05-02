"""Coordinate the object-toolbar tabs used by the level editor.

This module owns the tabbed container that presents recently used objects, the
active level-object palette, and the active enemy palette as independent
scrollable pages. It sits between object-toolbar data sources and the editor
surfaces that place objects into a level, so it needs to preserve one click
signal while keeping full palette rebuilds separate from lighter graphics-only
refreshes.

See Also
--------
foundry.gui.widgets.object_toolbar.ObjectToolBox
    Builds each individual palette page that this tab widget hosts.
foundry.gui.ObjectDropdown
    Offers the alternate object-selection workflow for direct lookup.
foundry.gui.visualization.MainView
    Consumes the selected toolbar object during level placement.
"""

from PySide6.QtCore import Qt, Signal, SignalInstance
from PySide6.QtWidgets import QScrollArea, QScrollBar, QTabWidget

from foundry.game.gfx.objects.in_level.enemy_item import EnemyItem
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from foundry.game.gfx.objects.in_level.level_object import LevelObject
from foundry.gui.localization import tr

from .ObjectToolBox import ObjectIcon, ObjectToolBox

_INDEX_RECENTLY_USED = 0
TR_CONTEXT = "TabbedToolBox"


class TabbedToolBox(QTabWidget):
    """Group recent, level-object, and enemy toolbar pages.

    Each tab wraps an ``ObjectToolBox`` in a scroll area. The tabs isolate
    recent choices from the full SMB3 level-object and enemy palettes while
    forwarding icon clicks through one signal. This class is also the boundary
    between full palette rebuilds after object-set changes and lighter preview
    refreshes after graphics-set changes.

    Parameters
    ----------
    parent : QWidget | None, optional
        Parent Qt widget that owns this object.

    Attributes
    ----------
    _enemies_toolbox : ObjectToolBox
        Enemy/item palette for the loaded object set.
    _objects_toolbox : ObjectToolBox
        Level-object palette for the loaded object set.
    _recent_toolbox : ObjectToolBox
        Recently selected placement objects.
    object_icon_clicked : SignalInstance
        Signal forwarded from all toolbox pages with the clicked icon and its
        stable object payload. Tab labels are localized display text refreshed
        by :meth:`retranslate_ui`; they are not used to route placement data.
    """

    object_icon_clicked: SignalInstance = Signal(ObjectIcon)

    def __init__(self, parent=None):
        """Create the tabbed toolbox and its scrollable pages.

        The constructor builds three independent ``ObjectToolBox`` pages, wraps
        each one in a scroll area, and forwards their click signals through a
        single toolbar-level signal. That keeps recent objects, level objects,
        and enemies isolated as separate editor palettes while still giving the
        rest of the editor one selection surface to listen to. It also selects
        the level-object tab as the initial editor state so newly opened levels
        land on the primary placement palette rather than the transient recent
        list or enemy page.

        Parameters
        ----------
        parent : QWidget | None, optional
            Parent Qt widget that owns this object.
        """
        super(TabbedToolBox, self).__init__(parent)

        self.setTabPosition(self.TabPosition.East)

        self._recent_toolbox = ObjectToolBox(self)
        self._recent_toolbox.object_icon_clicked.connect(self.object_icon_clicked.emit)

        self._objects_toolbox = ObjectToolBox(self)
        self._objects_toolbox.object_icon_clicked.connect(self.object_icon_clicked.emit)

        self._enemies_toolbox = ObjectToolBox(self)
        self._enemies_toolbox.object_icon_clicked.connect(self.object_icon_clicked.emit)

        for toolbox in (self._recent_toolbox, self._objects_toolbox, self._enemies_toolbox):
            scroll_area = QScrollArea(self)
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(toolbox)

            self.addTab(scroll_area, "")

        self.show_level_object_tab()
        self.retranslate_ui()

    def retranslate_ui(self) -> None:
        """Refresh tab labels, help text, and child icon tooltips.

        During live language switching, Qt tab names and tooltips are
        display-only surfaces over the toolbar's stable object payloads. This
        method coordinates toolbar display state by updating those localized
        strings and delegating to each page, while recent-object ordering,
        level-object grids, enemy grids, and emitted placement data remain
        unchanged.
        """
        self.setTabText(0, tr(TR_CONTEXT, "recent", "Recent"))
        self.setTabText(1, tr(TR_CONTEXT, "level_objects", "Level Objects"))
        self.setTabText(2, tr(TR_CONTEXT, "enemies", "Enemies"))
        self._recent_toolbox.retranslate_ui()
        self._objects_toolbox.retranslate_ui()
        self._enemies_toolbox.retranslate_ui()
        self._set_whats_this()

    def _set_whats_this(self) -> None:
        """Refresh translated toolbox help text."""
        self.setWhatsThis(
            tr(
                TR_CONTEXT,
                "help.object_toolbox",
                "<b>Object Toolbox</b><br/>Contains all objects and enemies/items, that can be placed in this type of level. Which are available depends on the object set, that is selected for this level.<br/>You can drag and drop objects into the level or click to select them. After selecting an object, you can place it by clicking the middle mouse button anywhere in the level.<br/><br/>Note: Some items, like blocks with items in them, are displayed as they appear in the ROM, mouse over them and check their names in the ToolTip, or use the object dropdown to find them directly.",
            )
        )

    def sizeHint(self):
        """Return the dock width Qt should reserve for the toolbar column.

        The main-window layout asks this widget for a preferred size while it
        is dividing horizontal space between the toolbar dock and the level
        viewport. ``QTabWidget`` only reports the stacked page area, but this
        toolbar also exposes an east-facing tab bar and a vertical scroll path
        for the active ``ObjectToolBox`` page. During the first layout pass,
        this method takes the base page size, adds the tab-bar width, then
        adds the width of a representative vertical scroll bar before handing
        the hint back to Qt. Qt then uses that combined width when it sizes
        the docked toolbar, which keeps the tab strip, the scrollable palette
        page, and the adjacent level view aligned before any tab switch or
        icon wrap forces a corrective relayout.

        Returns
        -------
        QSize
            Recommended size for the complete tabbed toolbox surface.
        """
        orig_size = super().sizeHint()
        scrollbar_width = QScrollBar(Qt.Orientation.Vertical).sizeHint().width()

        orig_size.setWidth(orig_size.width() + self.tabBar().width() + scrollbar_width)

        return orig_size

    def show_recent_tab(self):
        """Select the recently used objects tab."""
        self.setCurrentIndex(_INDEX_RECENTLY_USED)

    def show_level_object_tab(self):
        """Select the level objects tab."""
        self.setCurrentIndex(1)

    def show_enemy_item_tab(self):
        """Select the enemies/items tab."""
        self.setCurrentIndex(2)

    def select_object(self, level_object):
        """Show the tab that should own an object's placement preview.

        Parameters
        ----------
        level_object : LevelObject | EnemyItem
            Level object being displayed or modified.
        """
        recent_tab_showing = self.currentIndex() == _INDEX_RECENTLY_USED

        if self._recent_toolbox.has_object(level_object) and recent_tab_showing:
            pass
        elif isinstance(level_object, LevelObject):
            self.show_level_object_tab()
        elif isinstance(level_object, EnemyItem):
            self.show_enemy_item_tab()

    def set_object_set(self, object_set_index: int, graphic_set_index: int, palette_group_index: int):
        """Rebuild object and enemy tabs for a newly selected object set.

        Object-set changes invalidate both the terrain and enemy palettes, so
        the toolbox clears all pages and repopulates them from the matching
        SMB3 definitions. The recent tab is cleared as well because its cached
        objects belong to the previous set.

        Parameters
        ----------
        object_set_index : int
            Index of the object set.
        graphic_set_index : int
            Index of the graphic set.
        palette_group_index : int
            Index of the palette group.
        """
        self._recent_toolbox.clear()
        self._objects_toolbox.clear()
        self._objects_toolbox.add_from_object_set(object_set_index, graphic_set_index, palette_group_index)

        self._enemies_toolbox.clear()
        self._enemies_toolbox.add_from_enemy_set(object_set_index)

    def set_graphic_set(self, graphic_set_index: int, palette_group_index: int):
        """Refresh palette art for a graphics-set or palette-group change.

        Graphics-set and palette-group changes do not invalidate the logical
        contents of the toolbar, so this method only redraws the recent and
        level-object pages that depend on palette art. Enemy membership and the
        underlying object-set composition stay untouched until
        :meth:`set_object_set` runs. That split lets the editor respond to
        palette-preview changes without paying the cost of rebuilding every
        object entry after each graphics tweak, and it preserves the user’s
        current palette selection while the preview art is refreshed in place.

        Parameters
        ----------
        graphic_set_index : int
            Index of the graphic set.
        palette_group_index : int
            Index of the palette group.
        """
        self._recent_toolbox.set_graphic_set(graphic_set_index, palette_group_index)
        self._objects_toolbox.set_graphic_set(graphic_set_index, palette_group_index)

    def add_recent_object(self, level_object: InLevelObject):
        """Move an object to the front of the recent tab.

        Parameters
        ----------
        level_object : InLevelObject
            Level object being displayed or modified.
        """
        self._recent_toolbox.place_at_front(level_object)

    def get_equivalent(self, level_object: LevelObject | EnemyItem):
        """Resolve a placed object back to the matching palette entry.

        The editor often needs to jump from an in-level object to the palette
        item that owns its icon, metadata, and selection behavior. This helper
        searches the object and enemy palettes in the same order that the tabs
        expose them so the caller can restore toolbar context without
        reconstructing palette state itself.

        Parameters
        ----------
        level_object : LevelObject | EnemyItem
            Level object being displayed or modified.

        Returns
        -------
        LevelObject | EnemyItem | None
            Matching object from the loaded object or enemy page.
        """
        return self._objects_toolbox.get_equivalent(level_object) or self._enemies_toolbox.get_equivalent(level_object)
