"""Populate the searchable placement dropdown for the active SMB3 level.

``ObjectDropdown`` rebuilds the compact placement picker that sits beside
Foundry's object toolbar. ``set_object_set`` takes the active level header's
``object_set_index``, ``graphic_set_index``, and ``palette_group_index``,
uses :class:`~foundry.game.gfx.objects.in_level.level_object_factory.LevelObjectFactory`
to decode placeable level objects, and then appends the enemy and item entries
that
:class:`~foundry.game.gfx.objects.in_level.enemy_item_factory.EnemyItemFactory`
exposes for the same object set. The result is an editable ``QComboBox`` with
preview icons, substring completion, and ``UserRole`` payloads that carry the
live placement objects later emitted through ``object_selected``.

Read :mod:`foundry.gui.ObjectList` next for the matching toolbar presentation
of the same catalog, then follow the in-level object factories when tracing
how header state becomes placement rows.

See Also
--------
foundry.gui.ObjectList.ObjectList : Toolbar-style placement palette that mirrors the same catalog.
foundry.game.gfx.objects.in_level.level_object_factory.LevelObjectFactory : Factory used to rebuild level-object entries.
foundry.game.gfx.objects.in_level.enemy_item_factory.EnemyItemFactory : Factory used to rebuild enemy and item entries.
"""

from itertools import product

from PySide6.QtCore import Qt, Signal, SignalInstance
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtWidgets import QComboBox, QCompleter, QWidget

from foundry.game import should_be_placeable
from foundry.game.gfx import object_to_image
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects.in_level.enemy_item import EnemyItem
from foundry.game.gfx.objects.in_level.enemy_item_factory import EnemyItemFactory
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from foundry.game.gfx.objects.in_level.jump import Jump
from foundry.game.gfx.objects.in_level.level_object import LevelObject
from foundry.game.gfx.objects.in_level.level_object_factory import LevelObjectFactory
from foundry.gui.localization import tr, tr_object_name
from smb3parse.objects import MAX_DOMAIN, MAX_ENEMY_ITEM_ID, MAX_ID_VALUE
from smb3parse.util import apply

TR_CONTEXT = "ObjectDropdown"


class ObjectDropdown(QComboBox):
    """Searchable palette of placeable level objects and enemies.

    The dropdown mirrors the object-toolbar contents in compact form. It builds
    level-object entries from the active object and graphics set, inserts a
    separator, then appends enemy/item entries for the same object set.

    Parameters
    ----------
    parent : QWidget
        Parent Qt widget that owns this object.

    Attributes
    ----------
    _graphic_set_index : int
        Graphics set currently used for level-object icons.
    _object_factory : LevelObjectFactory
        Factory for rebuilding level-object payloads when the active graphics
        set changes. It owns decoded object identity; row text remains
        display-only.
    _object_set_index : int
        Object set currently loaded into the dropdown.
    object_selected : SignalInstance
        Signal emitted with the selected placeable object stored in the
        current row's ``Qt.UserRole`` payload. The payload is the stable
        placement object; localized row text is display-only and is refreshed
        by :meth:`retranslate_ui` without changing selection identity.
    """

    object_selected: SignalInstance = Signal(InLevelObject)

    def __init__(self, parent: QWidget):
        """Create the searchable object dropdown.

        Foundry uses this widget as the keyboard-first placement picker beside
        the tabbed object toolbar. Initialization wires substring completion,
        selection emission, and the empty pre-level state that later gets
        repopulated by ``set_object_set`` with SMB3 object and enemy entries.
        The widget therefore sits in the middle of one placement pipeline:
        loaded level header -> object factory -> dropdown rows -> emitted
        placement object.

        Parameters
        ----------
        parent : QWidget
            Parent Qt widget that owns this object.
        """
        super(ObjectDropdown, self).__init__(parent)

        self.setEditable(True)
        self.setMaxVisibleItems(30)

        self.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer().setFilterMode(Qt.MatchFlag.MatchContains)

        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        self.currentIndexChanged.connect(self._on_object_selected)

        # guard against overly long item descriptions
        self.setMaximumWidth(self.screen().availableSize().width() // 5)

        self.setWhatsThis(
            tr(
                TR_CONTEXT,
                "help.object_dropdown",
                "<b>Object Dropdown</b><br/>Contains all objects and enemies/items, that can be placed in this type of level. Which are available depends on the object set, that is selected for this level.<br/>You can search, by typing in the name, or simply select it from the list. After selecting an object, you can place it by clicking the middle mouse button anywhere in the level.",
            )
        )

        self._object_set_index = -1
        self._graphic_set_index = -1

    def setFocus(self):
        """Focus the search field for the next placement-object query.

        Foundry calls this from the keyboard placement workflow. Selecting the
        current text means the existing search term becomes the next keystroke
        target immediately, so switching placement objects stays inside the
        same keyboard-driven interaction loop.
        """
        super(ObjectDropdown, self).setFocus()

        self.lineEdit().selectAll()

    def set_object_set(self, object_set_index: int, graphic_set_index: int, palette_group_index: int) -> None:
        """Load dropdown entries for an object set and graphics set.

        Changing object set rebuilds the full level-object and enemy list
        because the available SMB3 definitions change. Changing only graphics
        set keeps the same logical objects and refreshes just their icons.
        That split mirrors how Foundry preserves placement selection while
        still updating art after header or palette changes.

        Parameters
        ----------
        object_set_index : int
            Index of the object set.
        graphic_set_index : int
            Index of the graphic set.
        palette_group_index : int
            Index of the palette group.
        """

        factory = LevelObjectFactory(
            object_set_index,
            graphic_set_index,
            palette_group_index,
            [],
            vertical_level=False,
            size_minimal=True,
        )

        needs_full_update = self._object_set_index != object_set_index

        self._object_set_index = object_set_index
        self._graphic_set_index = graphic_set_index

        if needs_full_update:
            self._on_object_factory_change(factory)

        else:
            self.set_graphics_set(factory)

    def set_graphics_set(self, factory: LevelObjectFactory) -> None:
        """Refresh level-object icons for a new graphics set.

        The row's logical placement identity is still domain/object-index data
        from the active object set. This method refreshes the icon and decoded
        ``Qt.UserRole`` object from those stable values; translated row text is
        not used to identify or rebuild the placement entry.

        Parameters
        ----------
        factory : LevelObjectFactory
            Factory used to create level objects.
        """

        for index in range(self.count()):
            old_level_object = self.itemData(index)

            if old_level_object is None:
                # found the separator object, after which only enemies and items follow
                break

            new_level_object = factory.from_properties(
                old_level_object.domain, old_level_object.obj_index, 0, 0, None, 0
            )

            self.setItemIcon(index, QIcon(QPixmap(self._resize_bitmap(object_to_image(new_level_object)))))
            self.setItemData(index, new_level_object)

    def _on_object_selected(self, _):
        """Emit the selected placeable object.

        Parameters
        ----------
        _ : int
            Selected combo-box index emitted by Qt.
        """
        if self.currentIndex() == -1:
            return

        level_object = self.currentData(Qt.ItemDataRole.UserRole)

        self.object_selected.emit(level_object)

    def select_object(self, level_object: InLevelObject):
        """Select a placeable object in the dropdown.

        This updates the toolbar selection when another UI path chooses the
        object type to place. It does not select an existing object inside the
        level.

        Parameters
        ----------
        level_object : InLevelObject
            Object type selected for placement in the level.

        Raises
        ------
        LookupError
            If no matching dropdown entry exists.
        """
        index_of_object = -1
        for index in range(self.count()):
            if self._matches_placement_identity(self.itemData(index, Qt.ItemDataRole.UserRole), level_object):
                index_of_object = index
                break

        if index_of_object == -1:
            raise LookupError(f"Couldn't find {level_object} in object dropdown.")

        was_blocked = self.blockSignals(True)
        self.setCurrentIndex(index_of_object)
        self.blockSignals(was_blocked)

    @staticmethod
    def _matches_placement_identity(candidate: object, level_object: InLevelObject) -> bool:
        """Compare placement identity without using translated row text.

        The dropdown uses this helper when another UI surface asks it to select
        a placement entry. The state flow stays payload-driven: row data carries
        object-set/domain/id fields, and localized names are ignored.

        Parameters
        ----------
        candidate : object
            Row payload read from ``Qt.UserRole``.
        level_object : InLevelObject
            Placement object requested by another UI surface.

        Returns
        -------
        bool
            ``True`` when both objects describe the same SMB3 palette entry.
            Level objects compare object set, domain, and object id; enemy/item
            rows compare object set and enemy/item id.
        """
        if isinstance(candidate, LevelObject) and isinstance(level_object, LevelObject):
            return (
                candidate.object_set == level_object.object_set
                and candidate.domain == level_object.domain
                and candidate.obj_index == level_object.obj_index
            )

        if isinstance(candidate, EnemyItem) and isinstance(level_object, EnemyItem):
            return candidate.object_set == level_object.object_set and candidate.obj_index == level_object.obj_index

        return False

    def retranslate_ui(self) -> None:
        """Refresh translated row labels without changing stored payloads.

        Each row keeps the placeable object instance in ``Qt.UserRole``. Live
        translation replaces only the visible combo-box text by re-reading that
        payload through :func:`tr_object_name`, so search identity, placement
        emissions, and object matching remain bound to stable object data.
        """
        for index in range(self.count()):
            level_object = self.itemData(index, Qt.ItemDataRole.UserRole)
            if isinstance(level_object, (LevelObject, EnemyItem)):
                self.setItemText(index, tr_object_name(level_object))

    def _on_object_factory_change(self, object_factory: LevelObjectFactory) -> None:
        """Rebuild all entries for a new level-object factory.

        This is the full-population path used when a level header points at a
        different SMB3 object set. It regenerates level objects first, inserts
        the visual separator, and then appends the placeable enemy/item list
        for the same set.
        The resulting order mirrors the toolbar so both selectors talk about
        the same placement catalog, and each row's ``UserRole`` payload becomes
        the object emitted back into the editor when a person chooses an item.
        In data-flow terms this is the repopulation boundary between the level
        header's object-set settings and the placement UI: once the factory
        changes, every row in the dropdown must be rebuilt so later selection
        signals emit objects that match the active decoding and graphics
        context.

        Parameters
        ----------
        object_factory : LevelObjectFactory
            Factory used to create level objects.
        """

        self.clear()

        self._object_factory = object_factory

        if self._object_factory is None:
            return

        # adds level objects
        domains = range(MAX_DOMAIN + 1)
        object_ids = list(range(0x00, 0x10)) + list(range(0x10, MAX_ID_VALUE, 0x10))

        level_objects = [
            self._object_factory.from_properties(domain, obj_index, 0, 0, None, 0)
            for domain, obj_index in product(domains, object_ids)
        ]

        valid_level_objects = filter(should_be_placeable, level_objects)

        apply(self._add_item, valid_level_objects)

        # insert visual separator between level objects and enemies/items
        self.insertSeparator(self.count())

        # adds enemies and items
        factory = EnemyItemFactory(object_factory.object_set)

        enemy_items = map(factory.from_properties, range(MAX_ENEMY_ITEM_ID + 1))

        valid_enemy_items = filter(should_be_placeable, enemy_items)

        apply(self._add_item, valid_enemy_items)

    def _add_item(self, level_object: Jump | LevelObject | EnemyItem):
        """Add one placeable object with a preview icon.

        The visible row text is localized through :func:`tr_object_name`, while
        the object itself is stored as item data. Selection, search matching,
        and ``object_selected`` emissions therefore keep using stable placement
        objects rather than translated labels.

        Parameters
        ----------
        level_object : Jump | LevelObject | EnemyItem
            Level object being displayed or modified.
        """
        if not should_be_placeable(level_object):
            return

        icon = QIcon(QPixmap(self._resize_bitmap(object_to_image(level_object))))

        self.addItem(icon, tr_object_name(level_object), level_object)

    @staticmethod
    def _resize_bitmap(source_image: QImage) -> QImage:
        """Resize a rendered object image for combo-box display.

        The dropdown normalizes every preview to one block so search results
        and long object lists stay visually comparable even when the original
        SMB3 object footprint is much larger.
        Keeping every icon to the same display size also preserves row height
        and popup layout while graphics sets change.

        Parameters
        ----------
        source_image : QImage
            Source image resized for display.

        Returns
        -------
        QImage
            Bitmap resized for the dropdown preview.
        """
        image = source_image.scaled(Block.SIDE_LENGTH, Block.SIDE_LENGTH)

        return image
