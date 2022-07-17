from typing import Union

from PySide6.QtCore import Qt, Signal, SignalInstance
from PySide6.QtGui import QIcon, QImage, QPixmap, QScreen
from PySide6.QtWidgets import QComboBox, QCompleter, QWidget

from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects.EnemyItem import EnemyObject
from foundry.game.gfx.objects.EnemyItemFactory import EnemyItemFactory
from foundry.game.gfx.objects.LevelObject import LevelObject, get_minimal_icon_object
from foundry.game.gfx.objects.LevelObjectFactory import LevelObjectFactory
from foundry.game.gfx.objects.ObjectLike import ObjectLike
from smb3parse.objects import MAX_DOMAIN, MAX_ENEMY_ITEM_ID, MAX_ID_VALUE, MIN_DOMAIN


class ObjectDropdown(QComboBox):
    object_selected: SignalInstance = Signal(ObjectLike)

    def __init__(self, parent: QWidget):
        super(ObjectDropdown, self).__init__(parent)

        self.setEditable(True)
        self.setMaxVisibleItems(30)

        self.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer().setFilterMode(Qt.MatchContains)

        self.setInsertPolicy(QComboBox.NoInsert)

        self.currentIndexChanged.connect(self._on_object_selected)

        # guard against overly long item descriptions
        self.setMaximumWidth(QScreen().availableSize().width() / 5)

        self.setWhatsThis(
            "<b>Object Dropdown</b><br/>"
            "Contains all objects and enemies/items, that can be placed in this type of level. Which are "
            "available depends on the object set, that is selected for this level.<br/>"
            "You can search, by typing in the name, or simply select it from the list. After selecting "
            "an object, you can place it by clicking the middle mouse button anywhere in the level."
        )

    def setFocus(self):
        super(ObjectDropdown, self).setFocus()

        self.lineEdit().selectAll()

    def set_object_set(self, object_set_index: int, graphic_set_index: int) -> None:
        factory = LevelObjectFactory(
            object_set_index, graphic_set_index, 0, [], vertical_level=False, size_minimal=True
        )

        self._on_object_factory_change(factory)

    def _on_object_selected(self, _):
        if self.currentIndex() == -1:
            return

        level_object = self.currentData(Qt.UserRole)

        self.object_selected.emit(level_object)

    def select_object(self, level_object: ObjectLike):
        """
        Called, when the current placeable object was selected from outside and we need to update the selection in the
        dropdown. This is not the selected object inside the level!

        :param level_object: The type of object, that was selected to be placeable in the level.
        """
        index_of_object = self.findText(level_object.name)

        if index_of_object == -1:
            raise LookupError(f"Couldn't find {level_object} in object dropdown.")

        was_blocked = self.blockSignals(True)
        self.setCurrentIndex(index_of_object)
        self.blockSignals(was_blocked)

    def _on_object_factory_change(self, object_factory: LevelObjectFactory) -> None:
        self.clear()

        self._object_factory = object_factory

        if self._object_factory is None:
            return

        # adds level objects
        for domain in range(MIN_DOMAIN, MAX_DOMAIN + 1):
            for static_object_id in range(0, 0x10):
                level_object = self._object_factory.from_properties(
                    domain, static_object_id, x=0, y=0, length=1, index=0
                )

                if (level_object := get_minimal_icon_object(level_object)) is not None:
                    self._add_item(level_object)

            for expanding_object_id in range(0x10, MAX_ID_VALUE, 0x10):
                level_object = self._object_factory.from_properties(
                    domain, expanding_object_id, x=0, y=0, length=1, index=0
                )

                level_object = get_minimal_icon_object(level_object)

                self._add_item(level_object)

        # insert visual separator between level objects and enemies/items
        self.insertSeparator(self.count())

        # adds enemies and items
        factory = EnemyItemFactory(object_factory.object_set, 0)

        for obj_index in range(MAX_ENEMY_ITEM_ID + 1):
            enemy_item = factory.from_properties(obj_index, x=0, y=0)

            self._add_item(enemy_item)

    def _add_item(self, level_object: Union[LevelObject, EnemyObject]):
        if not isinstance(level_object, (LevelObject, EnemyObject)):
            return

        if level_object.name in ["MSG_CRASH", "MSG_NOTHING", "MSG_POINTER"]:
            return

        icon = QIcon(QPixmap(self._resize_bitmap(level_object.as_image())))

        self.addItem(icon, level_object.name, level_object)

    @staticmethod
    def _resize_bitmap(source_image: QImage) -> QImage:
        image = source_image.scaled(Block.SIDE_LENGTH, Block.SIDE_LENGTH)

        return image
