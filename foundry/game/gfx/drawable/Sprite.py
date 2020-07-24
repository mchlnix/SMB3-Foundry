from typing import List
from functools import cached_property
from methodtools import lru_cache  # functools has a similar lru_cache, but can leak memory and is less class friendly
import numpy as np
from PySide2.QtGui import QImage, QPainter, QPixmap

from foundry.game.Size import Size
from foundry.game.gfx.GraphicsPage import GraphicsPage
from foundry.game.Position import Position
from foundry.game.gfx.drawable.Tile import Tile, qimage_mask
from foundry.game.gfx.objects.objects.LevelObjectDefinition import SpriteGraphic


@lru_cache
def make_sprite(sprite_idx: int, pal_group: List[List[int]], graphics_page: GraphicsPage, palette_idx: int) -> "Sprite":
    """Makes a sprite and stores it in a cache"""
    return Sprite.from_rom(sprite_idx, pal_group, palette_idx, graphics_page)


class Sprite:
    """Represents sprites inside the game"""
    image_length = 0x08
    image_height = 0x10

    def __init__(self, pixels: bytes, horizontal_mirror: bool = False, vertical_mirror: bool = False) -> None:
        self.pixels = pixels
        self.horizontal_mirror = horizontal_mirror
        self.vertical_mirror = vertical_mirror

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.pixels}, {self.horizontal_mirror}, {self.vertical_mirror})"

    @classmethod
    def from_sprite_graphic(
            cls,
            graphic: SpriteGraphic,
            palette_group: List[List[int]],
            palette_index: int,
            graphics_page: GraphicsPage):
        """Makes a sprite from a sprite graphic"""
        return cls.from_rom(
            graphic.graphic, palette_group, palette_index, graphics_page, graphic.horizontal_flip, graphic.vertical_flip
        )

    @classmethod
    def from_rom(
            cls,
            sprite_index: int,
            palette_group: List[List[int]],
            palette_index: int,
            graphics_page: GraphicsPage,
            horizontal_mirror: bool = False,
            vertical_mirror: bool = False
    ):
        """Returns a block directly from rom"""
        image = np.empty((Sprite.image_length, Sprite.image_length * 3), dtype="ubyte")
        tile_offset = 2 * (sprite_index // 2)
        for idx in range(2):
            tile = Tile.from_rom(tile_offset + idx, palette_group, palette_index, graphics_page)
            y_off = idx * Tile.image_height
            image[y_off:y_off + Tile.image_height, 0:3 * Tile.image_length] = tile.numpy_image
        return cls(bytes(image.flatten().tolist()), horizontal_mirror, vertical_mirror)

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
    def numpy_image(self) -> np.array:
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
        transparent: bool = False
    ) -> None:
        """
        Draws the Tile with a QPainter
        :param painter: The QPainter that will draw the image
        :param pos: The position to draw the image
        :param size: The size of the image to draw
        :param transparent: Masks out the background color
        :return: None
        """
        painter.drawPixmap(
            pos.x,
            pos.y,
            self.qpixmap_custom(size.width, size.height, self.horizontal_mirror, self.vertical_mirror, transparent)
        )
