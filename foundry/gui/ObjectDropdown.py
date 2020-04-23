from typing import Union

from PySide2.QtCore import Qt, Signal, SignalInstance
from PySide2.QtGui import QIcon, QImage, QPixmap
from PySide2.QtWidgets import QComboBox, QWidget

from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects.EnemyItem import EnemyObject
from foundry.game.gfx.objects.LevelObject import LevelObject, get_minimal_icon
from foundry.game.gfx.objects.LevelObjectFactory import LevelObjectFactory
from foundry.game.gfx.objects.ObjectLike import ObjectLike
from smb3parse.objects import MAX_DOMAIN, MAX_ID_VALUE, MIN_DOMAIN


class ObjectDropdown(QComboBox):
    object_selected: SignalInstance = Signal(ObjectLike)

    def __init__(self, parent: QWidget):
        super(ObjectDropdown, self).__init__(parent)


        self.currentIndexChanged.connect(self._on_object_selected)

    def set_object_factory(self, object_factory: LevelObjectFactory) -> None:
        self._on_object_factory_change(object_factory)

    def _on_object_selected(self, _):
        domain, object_index = self.currentData(Qt.UserRole)

        level_object = self._object_factory.from_properties(domain, object_index, 0, 0, 0, 0)

        self.object_selected.emit(level_object)

    def select_object(self, level_object: ObjectLike):
        """
        Called, when the current placeable object was selected from outside and we need to update the selection in the
        dropdown. This is not the selected object inside the level!

        :param level_object: The type of object, that was selected to be placeable in the level.
        """
        index_of_object = self.findText(level_object.description)

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

        for domain in range(MIN_DOMAIN, MAX_DOMAIN + 1):
            for static_object in range(0, 0x10):
                self._add_object(domain, static_object)

            for expanding_object in range(0x10, MAX_ID_VALUE, 0x10):
                # add one, since some objects have a width of 0, when taking the base index
                # I guess these are just invalid in that case
                self._add_object(domain, expanding_object + 1)

    def _add_object(self, domain: int, object_index: int) -> None:
        level_object = self._object_factory.from_properties(domain, object_index, x=0, y=0, length=1, index=0)

        self._add_item(level_object)

    def _add_item(self, level_object: Union[LevelObject, EnemyObject]):
        if not isinstance(level_object, LevelObject):
            return

        if level_object.description in ["MSG_CRASH", "MSG_NOTHING", "MSG_POINTER"]:
            return

        icon = QIcon(QPixmap(self._resize_bitmap(get_minimal_icon(level_object))))

        self.addItem(icon, level_object.description, (level_object.domain, level_object.obj_index))

    @staticmethod
    def _resize_bitmap(source_image: QImage) -> QImage:
        image = source_image.scaled(Block.SIDE_LENGTH, Block.SIDE_LENGTH)

        return image
