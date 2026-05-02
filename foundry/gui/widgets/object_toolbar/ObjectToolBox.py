"""Populate one toolbar page of placeable SMB3 objects.

This module owns the grid widget that turns object-set metadata and recent
selection history into clickable ``ObjectIcon`` cells. ``ObjectToolBox`` is the
per-tab unit used by the object toolbar: it rebuilds from level or enemy
definitions when compatibility changes, refreshes previews in place when only
graphics or palette data changes, and reorders recent picks without changing
the click/drag contract that the surrounding toolbar relies on.

See Also
--------
foundry.gui.widgets.object_toolbar.ObjectToolBar
    Tabbed container that composes multiple toolbox pages into the full object
    picker workflow.
foundry.gui.widgets.object_toolbar.object_icon.ObjectIcon
    Icon widget embedded in each grid cell and forwarded through the toolbox
    click signal.
"""

from itertools import product
from typing import cast

from PySide6.QtCore import QSize, Qt, Signal, SignalInstance
from PySide6.QtWidgets import QGridLayout, QSizePolicy, QWidget

from foundry.game import should_be_placeable
from foundry.game.gfx import GraphicsSet
from foundry.game.gfx.objects.in_level.enemy_item import EnemyItem
from foundry.game.gfx.objects.in_level.enemy_item_factory import EnemyItemFactory
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from foundry.game.gfx.objects.in_level.level_object import LevelObject
from foundry.game.gfx.objects.in_level.level_object_factory import LevelObjectFactory
from foundry.game.gfx.Palette import load_palette_group
from smb3parse.objects import MAX_DOMAIN, MAX_ENEMY_ITEM_ID, MAX_ID_VALUE
from smb3parse.util import apply

from .object_icon import ObjectIcon

COLUMN_COUNT = 2


class ObjectToolBox(QWidget):
    """Two-column grid of placeable object icons.

    A toolbox page is populated from either SMB3 level-object definitions,
    enemy/item ids, or the recent-object list. Each cell owns an ``ObjectIcon``
    that emits selection and drag data for placement in the level view. The
    toolbox is the unit that gets rebuilt when object-set compatibility changes
    and selectively re-skinned when only graphics or palette data changes. The
    tabbed toolbar composes several of these pages to separate recent choices,
    terrain objects, and enemies while reusing the same selection and drag
    behavior. Data flows into the grid in three ways: full rebuilds from object
    definitions, preview refreshes for graphics/palette changes, and
    reorder-only updates when the recent-object page moves a picked object to
    the front.

    Parameters
    ----------
    parent : QWidget | None, optional
        Parent Qt widget that owns this object.

    Attributes
    ----------
    _layout : QGridLayout
        Grid that stores object icons in row-major order.
    _object_set_index : int
        Object set used to build level-object icons on this page.
    object_icon_clicked : SignalInstance
        Signal emitted with the clicked ``ObjectIcon``. The icon owns the
        stable object payload used for placement and drag data; translated
        tooltips are display-only and are refreshed by :meth:`retranslate_ui`.
    """

    object_icon_clicked: SignalInstance = Signal(ObjectIcon)

    def __init__(self, parent: QWidget | None = None):
        """Create an empty toolbox grid.

        Parameters
        ----------
        parent : QWidget | None, optional
            Parent Qt widget that owns this object.
        """
        super(ObjectToolBox, self).__init__(parent)

        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

        self._layout = QGridLayout(self)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self._object_set_index: int = -1

    def sizeHint(self):
        """Report a size hint wide enough for the fixed two-column grid.

        Width is pinned to two icon columns so every tabbed toolbox page keeps
        the same footprint while object definitions, recent picks, or enemy
        lists swap in and out. The surrounding toolbar can therefore switch
        pages without reflowing the editor chrome around the active picker.
        That stable width is part of the toolbar handoff to the containing
        dock: layout decisions happen once at the page level instead of
        bouncing every time the toolbox repopulates. Qt consults this hint when
        the toolbar page is first laid out and again after repopulation, so the
        method keeps object-set rebuilds, enemy-list rebuilds, and recent-page
        reordering from resizing the dock around the picker. The method is the
        layout-side counterpart to the population methods below: as the grid's
        object data changes, this hint preserves one presentation contract for
        the surrounding toolbar and dock instead of letting each rebuild choose
        a different width.

        Returns
        -------
        QSize
            The recommended Qt size.
        """
        orig_size_hint: QSize = super().sizeHint()
        width = COLUMN_COUNT * ObjectIcon.MIN_SIZE.width()

        orig_size_hint.setWidth(width)

        return orig_size_hint

    def add_object(self, level_object: InLevelObject, index: int = -1):
        """Insert an object icon at a grid position.

        Each inserted icon is connected back to the toolbox so the owning tab
        can translate clicks into placement selection. The grid position is
        stable, which lets full rebuilds and recent-object reordering recreate
        the page contents without changing how selection signals are propagated
        to the parent toolbar. This method is therefore the last step in every
        population path: build or reuse a preview object, wrap it in an icon,
        and anchor the icon at the row-major slot that the rest of the toolbar
        logic expects. Full rebuilds, enemy-set loads, and recent-object
        reordering all converge here before the page is handed back to the
        surrounding toolbar as a clickable placement surface. Once the widget
        is inserted, downstream code no longer distinguishes how the preview
        object was sourced; it just relies on the icon's signal wiring and
        stable slot index. This method is therefore the data-to-widget
        transition point for the page: it turns a preview object into a live
        grid cell, increments the page contents, and establishes the row-major
        position that later lookup, refresh, and recent-object maintenance use.
        The caller supplies preview data, and this method commits that data to
        toolbox state by connecting the icon back to ``_on_icon_clicked`` and
        inserting the widget into ``_layout`` at either an explicit slot or
        the next append position.

        Parameters
        ----------
        level_object : InLevelObject
            Level object being displayed or modified.
        index : int, optional
            Zero-based index of the item to access.
        """
        icon = ObjectIcon(level_object)

        icon.clicked.connect(self._on_icon_clicked)

        if index == -1:
            index = self._layout.count()

        self._layout.addWidget(icon, index // COLUMN_COUNT, index % COLUMN_COUNT)

    def add_from_object_set(self, object_set_index: int, graphic_set_index: int, palette_group_index: int):
        """Populate placeable level objects for an object set.

        The toolbox samples each SMB3 object domain and representative object
        ids, then filters definitions that should not be placed directly before
        materializing icon widgets. This is the expensive full-rebuild path
        used when compatibility changes. It converts object-set metadata into
        the palette of placeable terrain objects that the toolbar page exposes,
        so callers use it when a new level header or object set makes the
        previous grid contents invalid. The method records the object-set index
        for later preview refreshes, materializes representative objects
        through ``LevelObjectFactory``, filters them to the placeable subset,
        and feeds the surviving previews through ``add_object`` so the rebuilt
        page can immediately participate in the normal click and drag workflow.

        Parameters
        ----------
        object_set_index : int
            Index of the object set.
        graphic_set_index : int
            Index of the graphic set.
        palette_group_index : int
            Index of the palette group.
        """
        self._object_set_index = object_set_index

        if graphic_set_index == -1:
            graphic_set_index = object_set_index

        factory = LevelObjectFactory(
            object_set_index,
            graphic_set_index,
            palette_group_index,
            [],
            vertical_level=False,
            size_minimal=True,
        )

        domains = range(MAX_DOMAIN + 1)
        object_ids = list(range(0x00, 0x10)) + list(range(0x10, MAX_ID_VALUE, 0x10))

        level_objects = [
            factory.from_properties(domain, obj_index, 0, 0, None, -1)
            for domain, obj_index in product(domains, object_ids)
        ]

        valid_level_objects = filter(should_be_placeable, level_objects)

        apply(self.add_object, valid_level_objects)

    def add_from_enemy_set(self, object_set_index: int):
        """Populate placeable enemies and items for an object set.

        Parameters
        ----------
        object_set_index : int
            Index of the object set.
        """
        factory = EnemyItemFactory(object_set_index)

        enemy_items = map(factory.from_properties, range(MAX_ENEMY_ITEM_ID + 1))

        valid_enemy_items = filter(should_be_placeable, enemy_items)

        apply(self.add_object, valid_enemy_items)

    def set_graphic_set(self, graphic_set_index: int, palette_group_index: int):
        """Refresh level-object previews for a new graphics or palette group.

        Enemy previews are skipped because they do not use the level-object
        graphics-set path that terrain objects do. Existing icon widgets are
        updated in place so selection and tab order stay stable.
        That makes graphics-only refreshes much cheaper than rebuilding the
        toolbox from object definitions.
        Callers use this narrower path when the level header changes how
        objects should render but does not change which objects belong in the
        page. The method mutates the preview objects already owned by each icon
        and clears their cached blocks before asking the icon to repaint, which
        keeps the toolbar synchronized with ROM hotswap and level-header
        updates without disturbing the rest of the placement workflow.

        Parameters
        ----------
        graphic_set_index : int
            Index of the graphic set.
        palette_group_index : int
            Index of the palette group.
        """
        for object_icon in self._gen_icon_widgets():
            obj = object_icon.object

            if isinstance(obj, EnemyItem):
                continue

            assert isinstance(obj, LevelObject)

            obj.graphics_set = GraphicsSet.from_number(graphic_set_index)
            obj.palette_group = load_palette_group(obj.object_set.number, palette_group_index)
            obj.block_cache.clear()
            object_icon.set_object(obj)

    def clear(self):
        """Remove all icon widgets from the grid."""
        self._extract_objects()

    def _on_icon_clicked(self):
        """Forward the clicked icon through ``object_icon_clicked``."""
        self.object_icon_clicked.emit(self.sender())

    @property
    def draw_background_color(self):
        """Expose whether icons draw their palette background color.

        Callers use this to keep toolbox pages visually consistent with the
        larger current-object preview. Reading the flag from the first icon lets
        toolbar-level UI code treat the page as one visual surface instead of
        tracking per-cell presentation state.

        Returns
        -------
        bool
            Whether icons draw their palette background color.
        """
        return self._layout.itemAt(0).draw_background_color

    @draw_background_color.setter
    def draw_background_color(self, value):
        """Update whether every icon draws its palette background color.

        Parameters
        ----------
        value : bool
            Whether icons draw their palette background color.
        """
        for index in range(self._layout.count()):
            self._layout.itemAt(index).draw_background_color = value

    def has_object(self, level_object):
        """Check whether the toolbox already contains an equivalent object.

        Recent-object pages use this to avoid duplicate entries while
        translating between live level objects and palette-owned preview
        objects.
        The boolean result is the quick membership gate before recent-object
        reordering decides whether it can move an existing icon or must rebuild
        the front of the page with a new preview object. In other words, this
        is the cheap preflight check in the recent-selection workflow before
        the page mutates its row-major contents.

        Parameters
        ----------
        level_object : InLevelObject
            Level object being displayed or modified.

        Returns
        -------
        bool
            ``True`` when an equivalent icon exists.
        """
        return self.index_of_object(level_object) != -1

    def get_equivalent(self, level_object):
        """Find the toolbox object matching another object's identity.

        Matching is based on object-set identity and type rather than Python
        object identity so callers can translate between live level objects and
        the palette-owned preview objects that should appear selected in the UI.

        Parameters
        ----------
        level_object : InLevelObject
            Object whose object set and type should be matched.

        Returns
        -------
        InLevelObject | None
            Matching toolbar object, if one exists.
        """
        for index in range(self._layout.count()):
            internal_object = self._layout.itemAtPosition(index // COLUMN_COUNT, index % COLUMN_COUNT).widget().object

            if internal_object.object_set == level_object.object_set and internal_object.type == level_object.type:
                return internal_object

        else:
            return None

    def index_of_object(self, level_object):
        """Look up the grid index of an equivalent object icon.

        This lookup is the bridge between live selection objects and the
        palette-owned preview objects stored in the toolbox. Callers use the
        returned index to keep recent-object pages and active selection state
        aligned without depending on object identity surviving rebuilds.

        Parameters
        ----------
        level_object : InLevelObject
            Level object being displayed or modified.

        Returns
        -------
        int
            Index of the object in the toolbar page.
        """
        for index, object_icon in enumerate(self._gen_icon_widgets()):
            if object_icon.object == level_object:
                return index
        else:
            return -1

    def retranslate_ui(self) -> None:
        """Refresh page icon tooltips without rebuilding the icon grid.

        Each ``ObjectIcon`` receives a live-refresh pass from the active
        catalog. Grid order, icon widgets, and their stored object payloads stay
        stable so filtering or recent-object identity is not affected by
        translated tooltip text.
        """
        for object_icon in self._gen_icon_widgets():
            object_icon.retranslate_ui()

    def _gen_icon_widgets(self):
        """Yield icon widgets in grid order.

        The generator gives callers one consistent traversal order for redraw,
        lookup, recent-object maintenance, and preview-state synchronization.
        Using one shared traversal path keeps grid mutations and toolbar-level
        bookkeeping aligned on the same row-major ordering.

        Yields
        ------
        ObjectIcon
            Icon widget stored in the grid.
        """
        for index in range(self._layout.count()):
            yield cast(ObjectIcon, self._layout.itemAtPosition(index // COLUMN_COUNT, index % COLUMN_COUNT).widget())

    def _extract_objects(self):
        """Remove icons and return their objects in grid order.

        This is the restructuring primitive used by full clears and recent-tab
        reordering: remove widgets first, then rebuild them in the desired
        order.
        By preserving row-major object order in the returned list, the caller
        can apply reorder logic and repopulate the grid without losing the
        toolbox's notion of first-choice vs later-choice objects. The extracted
        list is the handoff between one toolbar-page state and the next:
        callers drain the Qt widgets, transform the preview-object ordering,
        then feed the result back through ``add_object`` to reestablish the
        interactive grid.

        Returns
        -------
        list[InLevelObject]
            Objects extracted from the toolbar page.
        """
        objects = []

        while True:
            item = self._layout.takeAt(0)

            if item is None:
                break
            else:
                objects.append(item.widget().object)
                item.widget().deleteLater()

        return objects

    def place_at_front(self, new_object):
        """Move an object to the front of the grid without duplicates.

        Recent objects are de-duplicated by the fields users care about when
        picking from the toolbar again: domain and type for level objects, or
        enemy id for enemies/items.

        Parameters
        ----------
        new_object : InLevelObject
            Object to place first in the grid.
        """
        objects = self._extract_objects()

        for obj in objects.copy():
            same_level_object = (
                isinstance(obj, LevelObject) and obj.domain == new_object.domain and obj.type == new_object.type
            )

            same_enemy = isinstance(obj, EnemyItem) and obj.obj_index == new_object.obj_index

            if same_level_object or same_enemy:
                objects.remove(obj)

        objects.insert(0, new_object)

        assert self._layout.count() == 0

        for obj in objects:
            self.add_object(obj)
