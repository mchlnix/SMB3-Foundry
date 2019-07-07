import wx.adv

from game.gfx.drawable.Block import Block
from game.gfx.objects.LevelObject import LevelObject


class ObjectDropdown(wx.adv.BitmapComboBox):
    def __init__(self, parent, object_factory):
        super(ObjectDropdown, self).__init__(parent)

        self._on_object_factory_change(object_factory)

    def set_object_factory(self, object_factory):
        self._on_object_factory_change(object_factory)

    def _on_object_factory_change(self, object_factory):
        self._object_factory = object_factory

        self.Clear()

        if self._object_factory is None:
            return

        for domain in range(0, 8):
            for static_object in range(0, 0x10):
                self._add_object(domain, static_object)

            for expanding_object in range(0x10, 0xFF, 0x10):
                # add one, since some objects have a width of 0, when taking the base index
                # I guess these are just invalid in that case
                self._add_object(domain, expanding_object + 1)

    def _add_object(self, domain, object_index):
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

        self.Append(level_object.description, bitmap, (domain, object_index))

    @staticmethod
    def _resize_bitmap(source_bitmap):
        """
        Takes a wx.Bitmap and resizes it to the size of the ImageDropdown.

        :param wx.Bitmap source_bitmap: Bitmap to resize.

        :return: Resized copy of Bitmap.
        :rtype: wx.Bitmap
        """

        image = source_bitmap.ConvertToImage()

        image.Rescale(Block.SIDE_LENGTH, Block.SIDE_LENGTH)

        return image.ConvertToBitmap()
