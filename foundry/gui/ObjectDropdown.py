from typing import Any, List

import wx.adv

from game.gfx.drawable.Block import Block
from game.gfx.objects.LevelObject import LevelObject
from game.gfx.objects.LevelObjectFactory import LevelObjectFactory


class ObjectDropdown(wx.adv.BitmapComboBox):
    def __init__(self, parent: wx.Window):
        super(ObjectDropdown, self).__init__(parent)

        # the internal list of objects, which can be filtered down
        self._object_items: List[tuple] = []

        # text entered in the combobox to filter the items
        self._text: str = ""

        self.Bind(wx.EVT_TEXT, self._update_filter_text)

    def set_object_factory(self, object_factory: LevelObjectFactory) -> None:
        self._on_object_factory_change(object_factory)

    def GetSelection(self) -> int:
        """
        Overwritten method of wx.Combobox, which goes through the objects, that are saved behind the scenes and gives
        the actual index, independent on the currently filtered contents of the ComboBox.

        :return: The real index of the selected object, or wx.NotFound if none is selected.
        """
        current_value = self.GetValue()

        for index, (object_description, *_) in enumerate(self._object_items):
            if current_value == object_description:
                return index
        else:
            return -1

    def GetClientData(self, index: int) -> Any:
        """
        Overwritten method of wx.Combobox, which returns the client data based on the real index of the object, not the
        current index, of a possible filtered down ComboBox.

        :param int index: The real index of an object inside the ComboBox, obtained by GetSelection().
        :return: The ClientData of the object with the given index.
        """

        description, bitmap, client_data = self._object_items[index]

        return client_data

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
        self.SetItems([])

        filter_values = self._text.lower().split(" ")

        for description, bitmap, client_data in self._object_items:
            if filter_values:
                if not all(
                    filter_value in description.lower()
                    for filter_value in filter_values
                ):
                    continue

            self.Append(description, bitmap, client_data)

    def _add_object(self, domain: int, object_index: int) -> None:
        """
        Adds objects described by the domain and index, if they are displayable.

        :param int domain: The domain of the object.
        :param int object_index: The index inside the domain of the object.
        """

        level_object = self._object_factory.from_properties(
            domain, object_index, x=0, y=0, length=1, index=0
        )

        if not isinstance(level_object, LevelObject):
            return

        if level_object.description in ["MSG_CRASH", "MSG_NOTHING", "MSG_POINTER"]:
            return

        bitmap = self._resize_bitmap(level_object.as_bitmap())

        self._object_items.append(
            (level_object.description, bitmap, (domain, object_index))
        )

    @staticmethod
    def _resize_bitmap(source_bitmap: wx.Bitmap) -> wx.Bitmap:
        """
        Takes a wx.Bitmap and resizes it to the size of the ImageDropdown.

        :param wx.Bitmap source_bitmap: Bitmap to resize.

        :return: Resized copy of Bitmap.
        :rtype: wx.Bitmap
        """

        image = source_bitmap.ConvertToImage()

        image.Rescale(Block.SIDE_LENGTH, Block.SIDE_LENGTH)

        return image.ConvertToBitmap()
