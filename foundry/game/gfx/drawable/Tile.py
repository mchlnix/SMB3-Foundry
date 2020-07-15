from typing import List
from operator import add
from functools import cached_property, lru_cache
from PySide2.QtCore import QPoint
from PySide2.QtGui import QImage, QPainter, Qt, QColor, QPixmap
import numpy as np

from foundry.game.gfx.Palette import NESPalette
from foundry.game.gfx.drawable import MASK_COLOR
from foundry.game.Size import Size
from foundry.game.gfx.GraphicsPage import GraphicsPage
from foundry.game.Position import Position

PIXEL_OFFSET = 8  # both bits describing the color of a pixel are in separate 8 byte chunks at the same index

BACKGROUND_COLOR_INDEX = 0


@lru_cache
def get_byte_bits(b: int, reverse: bool = False, false_value: int = 0, true_value: int = 1) -> List[int]:
    """Returns a bit array of True and False values in terms of a specific int"""
    if reverse:
        return [true_value if b & (0x80 >> i) else false_value for i in range(8)]
    else:
        return [true_value if b & (0b1 << i) else false_value for i in range(8)]


def get_tile_row(byte_1: int, byte_2: int) -> map:
    """Returns a map of a tile row"""
    return map(add, get_byte_bits(byte_1, True), get_byte_bits(byte_2, True, true_value=2))


def get_color(b: int, palette):
    """Gets the appropriate color for a given pixel and palette"""
    # add alpha values
    if b == BACKGROUND_COLOR_INDEX:
        return MASK_COLOR
    else:
        return NESPalette[palette[b]]


class Tile:
    """A single 8x8 tile in game"""
    image: QPixmap

    image_length = 8
    image_height = image_length

    def __init__(self, pixels: bytes) -> None:
        self.pixels = pixels

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.pixels})"

    @classmethod
    def from_palette_and_pixels(cls, plane_1: List[int], plane_2: List[int], palette):
        """Returns a tiles pixels"""
        pixels = bytearray()
        for (byte_1, byte_2) in zip(plane_1, plane_2):
            for pixel in get_tile_row(byte_1, byte_2):
                pixels.extend(get_color(pixel, palette))
        return cls(bytes(pixels))

    @classmethod
    def from_rom(cls, object_index: int, palette_group: List[List[int]], palette_index: int, graphics_set: GraphicsPage):
        """Returns a tile directly from rom"""
        start = object_index * 0x10
        palette = palette_group[palette_index]
        return cls.from_palette_and_pixels(
            graphics_set.data[start: start + 0x08], graphics_set.data[start + 0x08: start + 0x10], palette
        )

    @property
    def default_size(self):
        """The default size of a tile"""
        return Size(self.image_length, self.image_length)

    @property
    def pixel_count(self) -> int:
        """The amount of pixels inside a tile"""
        return self.default_size.width * self.default_size.height

    @lru_cache
    def qimage_custom(self, width: int = image_length, height: int = image_length, horizontal_mirror: bool = False,
                      vertical_mirror: bool = False, transparent: bool = False) -> QImage:
        """A sized qimage"""
        image = self.qimage_transparent if transparent else self.qimage
        return image.mirrored(horizontal_mirror, vertical_mirror).scaled(width, height)

    @cached_property
    def qimage_transparent(self) -> QImage:
        """Returns a qimage with an alpha channel"""
        image = self.qimage
        mask = self.qimage_mask(image=image)
        image.setAlphaChannel(mask)
        return image

    def qimage_mask(self, image: QImage) -> QImage:
        """Makes a mask of the image"""
        return image.createMaskFromColor(QColor(*MASK_COLOR).rgb(), Qt.MaskOutColor)

    @cached_property
    def qimage(self) -> QImage:
        """Returns a qimage"""
        image = QImage(self.pixels, self.default_size.width, self.default_size.height, QImage.Format_RGB888)
        return image

    @lru_cache
    def qpixmap_custom(self, width: int = image_length, height: int = image_length, horizontal_mirror: bool = False,
                       vertical_mirror: bool = False, transparent: bool = True) -> QPixmap:
        """A sized qpixmap"""
        return QPixmap.fromImage(self.qimage_custom(width, height, horizontal_mirror, vertical_mirror, transparent))

    @cached_property
    def qpixmap(self) -> QPixmap:
        """Returns a qpixmap"""
        return QPixmap.fromImage(self.qimage)

    @cached_property
    def numpy_image(self) -> np.array:
        """Returns a 2d numpy array of the object"""
        return np.reshape(np.asarray(bytearray(self.pixels), dtype="ubyte"), (self.default_size.width, 3*self.default_size.height))

    def draw(self, painter: QPainter, pos: Position, size: Size, horizontal_mirror: bool = False,
             vertical_mirror: bool = False, transparent: bool = False):
        """Draws the image onto the screen"""
        pixmap = self.qpixmap_custom(size.width, size.height, horizontal_mirror, vertical_mirror, transparent)
        painter.drawPixmap(pos.x, pos.y, pixmap)
