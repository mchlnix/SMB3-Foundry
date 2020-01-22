from typing import List

from PySide2.QtGui import QIcon, QImage, QPixmap
from PySide2.QtWidgets import QComboBox, QWidget

from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects.LevelObject import LevelObject
from foundry.game.gfx.objects.LevelObjectFactory import LevelObjectFactory


class ObjectDropdown(QComboBox):
    def __init__(self, parent: QWidget):
        super(ObjectDropdown, self).__init__(parent)

        # the internal list of objects, which can be filtered down
        self._object_items: List[tuple] = []

        # text entered in the combobox to filter the items
        self._text: str = ""

    def set_object_factory(self, object_factory: LevelObjectFactory) -> None:
        self._on_object_factory_change(object_factory)

    def _update_filter_text(self, _) -> None:
        self._text = self.GetValue()

        self._fill_combobox()

    def _on_object_factory_change(self, object_factory: LevelObjectFactory) -> None:
        self._object_factory: LevelObjectFactory = object_factory

        if self._object_factory is None:
            return

        for domain in range(0, 8):
            for static_object in range(0, 0x10):
                self._add_object(domain, static_object)

            for expanding_object in range(0x10, 0xFF, 0x10):
                # add one, since some objects have a width of 0, when taking the base index
                # I guess these are just invalid in that case
                self._add_object(domain, expanding_object + 1)

        self._fill_combobox()

    def _fill_combobox(self) -> None:
        self.clear()

        filter_values = self._text.lower().split(" ")

        for description, image, client_data in self._object_items:
            if filter_values:
                if not all(filter_value in description.lower() for filter_value in filter_values):
                    continue

            self.addItem(QIcon(QPixmap(image)), description, client_data)

    def _add_object(self, domain: int, object_index: int) -> None:
        """
        Adds objects described by the domain and index, if they are displayable.

        :param int domain: The domain of the object.
        :param int object_index: The index inside the domain of the object.
        """

        level_object = self._object_factory.from_properties(domain, object_index, x=0, y=0, length=1, index=0)

        if not isinstance(level_object, LevelObject):
            return

        if level_object.description in ["MSG_CRASH", "MSG_NOTHING", "MSG_POINTER"]:
            return

        bitmap = self._resize_bitmap(level_object.as_image())

        self._object_items.append((level_object.description, bitmap, (domain, object_index)))

    @staticmethod
    def _resize_bitmap(source_image: QImage) -> QImage:
        image = source_image.scaled(Block.SIDE_LENGTH, Block.SIDE_LENGTH)

        return image
