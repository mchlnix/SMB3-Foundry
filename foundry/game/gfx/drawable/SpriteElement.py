from typing import List
from functools import cached_property
from methodtools import lru_cache  # functools has a similar lru_cache, but can leak memory and is less class friendly
from PySide2.QtGui import QImage, QPainter, QPixmap
from qimage2ndarray import array2qimage
import numpy as np

from foundry.core.geometry.Size.Size import Size
from foundry.game.Position import Position
from foundry.game.gfx.PatternTableHandler import PatternTableHandler
from foundry.game.gfx.drawable.Tile import qimage_mask
from foundry.game.gfx.drawable.Sprite import Sprite
from foundry.game.gfx.objects.objects.LevelObjectDefinition import Animation


class SpriteElement:
    """A grouping of sprites to make a frame of an object"""
    sprites: np.array

    def __init__(self, sprites: np.array) -> None:
        self.sprites = sprites

    def __repr__(self):
        return f"{self.__class__.__name__}({self.sprites})"

    @property
    def image_width(self) -> int:
        """
        Provides the default width of the image
        :return: int
        """
        return self.sprites.shape[1] * 0x08

    @property
    def image_height(self) -> int:
        """
        Provides the default height of the image
        :return: int
        """
        return self.sprites.shape[0] * 0x10

    @property
    def default_size(self) -> Size:
        """
        The default size of the sprite element
        :return: Size(self.image_width, self.image_height)
        """
        return Size(self.image_width, self.image_height)

    @property
    def pixel_count(self) -> int:
        """The amount of pixels inside a tile"""
        return self.image_width * self.image_height

    @lru_cache
    def qimage_custom(self, width: int = None, height: int = None, transparent: bool = False) -> QImage:
        """
        Provides a customized QImage from the Tile
        :param width: The width of the QImage
        :param height: The height of the QImage
        :param transparent: Determines if the Tile will mask out transparency
        :return: QImage
        """
        width = self.image_width if width is None else width
        height = self.image_height if height is None else height
        image = self.qimage_transparent if transparent else self.qimage
        return image.scaled(width, height)

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
        return array2qimage(self.numpy_image)

    @lru_cache
    def qpixmap_custom(self, width: int = None, height: int = None, transparent: bool = True) -> QPixmap:
        """
        Provides a customized QPixmap from the Tile
        :param width: The width of the QPixmap
        :param height: The height of the QPixmap
        :param transparent: Determines if the Tile will mask out transparency
        :return: QPixmap
        """
        width = self.image_width if width is None else width
        height = self.image_height if height is None else height
        return QPixmap.fromImage(self.qimage_custom(width, height, transparent))

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
        :return: np.array[dtype: byte, shape(self.image_width, self.image_height * 3)]
        """
        image = np.empty((self.image_width, self.image_height * 3), dtype="ubyte")
        height = Sprite.image_height * 3
        for sprite, (x, y) in zip(self.sprites, np.ndindex(self.sprites)):
            x_off, y_off = x * Sprite.image_length, y * height
            image[x_off, x_off + Sprite.image_length, y_off: y_off + height] = sprite.numpy_image
        return image

    @classmethod
    def from_list_and_size(cls, sprites: List[Sprite], size: Size) -> "SpriteElement":
        """Makes a sprite element from a list of sprites and a given size"""
        return cls(np.reshape(np.asarray(sprites), (size.width, size.height)))

    @classmethod
    def from_animation(cls, palette_group: List[List[int]], animation: Animation) -> "SpriteElement":
        """Makes a sprite element from an animation"""
        return cls.from_list_and_size(
            sprites=[Sprite.from_sprite_graphic(
                graphic, palette_group, animation.palette, PatternTableHandler(animation.page)
            ) for graphic in animation.graphics],
            size=animation.size
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
            self.qpixmap_custom(size.width, size.height, transparent)
        )
