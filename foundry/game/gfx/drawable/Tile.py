"""
This module converts the Nintendo's 2 bit per pixel image format into a Tile or a 8x8 RGB image in bytes.
get_byte_bits: Converts a byte to a row 1 bit per pixel row of image data
get_tile_row: Converts the upper and lower 1 bit per pixel row into a 2 bit per pixel representation
get_color: A color lookup that allows for transparency
qimage_mask: Masks out a color and returns a alpha mask
Tile: The class for loading any NES graphic
"""

from typing import List
from operator import add
from functools import cached_property
from functools import lru_cache as lru_cache
from PySide2.QtGui import QImage, QPainter, Qt, QColor, QPixmap
import numpy as np

from foundry.game.gfx.Palette import PaletteController
from foundry.game.gfx.drawable import MASK_COLOR
from foundry.core.geometry.Size.Size import Size
from foundry.game.gfx.PatternTableHandler import PatternTableHandler
from foundry.core.geometry.Position.Position import Position
import pyximport
pyximport.install(inplace=True)
from foundry.game.gfx.drawable.get_byte_bits_cython import get_byte_bits


PIXEL_OFFSET = 8  # both bits describing the color of a pixel are in separate 8 byte chunks at the same index

BACKGROUND_COLOR_INDEX = 0
palette_controller = PaletteController()


def get_tile_row(byte_1: int, byte_2: int) -> map:
    """
    Converts the upper and lower 1 bit per pixel row into a 2 bit per pixel representation
    :param byte_1: The lower byte to be converted
    :param byte_2: The upper byte to be converted
    :return: A list representation of the NES 2bpp format
    """
    return map(add, get_byte_bits(byte_1, True), get_byte_bits(byte_2, True, true_value=2))


def get_color(b: int, palette):
    """
    A color lookup that allows for transparency
    :param b: The idx in terms of the NES palette
    :param palette: The NES palette to look up
    :return: The correct NES color
    """
    # add alpha values
    if b == BACKGROUND_COLOR_INDEX:
        return MASK_COLOR
    else:
        try:
            return palette_controller.colors[palette[b]]
        except KeyError:
            return palette[b]  # the palette has the correct color already


def qimage_mask(image: QImage) -> QImage:
    """
    Makes a mask from a given image
    :param image: The QImage to be masked
    :return: A QImage of the given alpha mask
    """
    return image.createMaskFromColor(QColor(*MASK_COLOR).rgb(), Qt.MaskOutColor)


class Tile:
    """
    A square that represents the fundamental unit of the Nintendo's 2bpp image format.
    """
    image: QPixmap

    image_length = 8
    image_height = image_length

    def __init__(self, pixels: bytes) -> None:
        self.pixels = pixels

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.pixels})"

    @classmethod
    def from_palette_and_pixels(cls, plane_1: List[int], plane_2: List[int], palette):
        """
        Converts from the Nintendo's 2 bit per pixel format into RGB pixels
        :param plane_1: The lower plane of bytes
        :param plane_2: The upper plane of bytes
        :param palette: The palette for the Tile
        :return: Tile
        """
        pixels = bytearray()
        for (byte_1, byte_2) in zip(plane_1, plane_2):
            for pixel in get_tile_row(byte_1, byte_2):
                pixels.extend(get_color(pixel, palette))
        return cls(bytes(pixels))

    @classmethod
    def from_rom(
            cls, object_index: int, palette_group: List[List[int]], palette_index: int, graphics_page: PatternTableHandler
    ):
        """
        Makes a Tile directly from the ROM
        :param object_index: The index into the graphics page (0 - 0xFF)
        :param palette_group: The palettes available
        :param palette_index: The palette used
        :param graphics_page: The page (upper) index into the graphics
        :return: Tile
        """
        start = object_index * 0x10
        palette = palette_group[palette_index]
        return cls.from_palette_and_pixels(
            graphics_page.data[start: start + 0x08], graphics_page.data[start + 0x08: start + 0x10], palette
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
        """
        Provides a customized QImage from the Tile
        :param width: The width of the QImage
        :param height: The height of the QImage
        :param horizontal_mirror: Determines if the QImage will be flipped over the y axis
        :param vertical_mirror: Determines if the QImage will be flipped over the x axis
        :param transparent: Determines if the Tile will mask out transparency
        :return: QImage
        """
        image = self.qimage_transparent if transparent else self.qimage
        return image.mirrored(horizontal_mirror, vertical_mirror).scaled(width, height)

    @cached_property
    def qimage_transparent(self) -> QImage:
        """
        Applies a mask to the QImage constructor to make it transparent
        :return: An RGBA QImage
        """
        image = self.qimage
        image.setAlphaChannel(qimage_mask(image=image))
        return image

    @cached_property
    def qimage(self) -> QImage:
        """
        Makes a RGB QImage of the Tile
        :return: QImage
        """
        image = QImage(self.pixels, self.default_size.width, self.default_size.height, QImage.Format_RGB888)
        return image

    @lru_cache
    def qpixmap_custom(self, width: int = image_length, height: int = image_length, horizontal_mirror: bool = False,
                       vertical_mirror: bool = False, transparent: bool = True) -> QPixmap:
        """
        Provides a customized QPixmap from the Tile
        :param width: The width of the QPixmap
        :param height: The height of the QPixmap
        :param horizontal_mirror: Determines if the QPixmap will be flipped over the y axis
        :param vertical_mirror: Determines if the QPixmap will be flipped over the x axis
        :param transparent: Determines if the Tile will mask out transparency
        :return: QPixmap
        """
        return QPixmap.fromImage(self.qimage_custom(width, height, horizontal_mirror, vertical_mirror, transparent))

    @cached_property
    def qpixmap(self) -> QPixmap:
        """
        Makes a RGB QPixmap of the Tile
        :return: QPixmap
        """
        return QPixmap.fromImage(self.qimage)

    @cached_property
    def numpy_image(self) -> "np.array[np.dtype: np.ubyte]":
        """
        Makes a 2D virtualization of the data in terms of a numpy array
        :return: np.array[dtype: byte, shape(Tile.default_size.width, Tile.default_size.height * 3)]
        """
        return np.reshape(
            np.asarray(bytearray(self.pixels), dtype="ubyte"), (self.default_size.width, 3 * self.default_size.height)
        )

    def draw(
        self,
        painter: QPainter,
        pos: Position,
        size: Size,
        horizontal_mirror: bool = False,
        vertical_mirror: bool = False,
        transparent: bool = False
    ) -> None:
        """
        Draws the Tile with a QPainter
        :param painter: The QPainter that will draw the image
        :param pos: The position to draw the image
        :param size: The size of the image to draw
        :param horizontal_mirror: Flips the image over the y axis
        :param vertical_mirror: Flips the image over the x axis
        :param transparent: Masks out the background color
        :return: None
        """
        painter.drawPixmap(
            pos.x,
            pos.y,
            self.qpixmap_custom(size.width, size.height, horizontal_mirror, vertical_mirror, transparent)
        )
