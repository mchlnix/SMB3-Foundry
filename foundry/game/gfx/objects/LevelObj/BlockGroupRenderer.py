from typing import List, Tuple
from itertools import product

from PySide2.QtCore import QSize
from PySide2.QtGui import QImage, QPainter

from foundry.game.File import ROM
from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx.Palette import PaletteGroup, bg_color_for_object_set
from foundry.game.gfx.drawable.Block import Block, get_block


# todo: Create tests for BlockGroupRenderer
class BlockGroupRenderer:
    """
    A class to render a square grouping of blocks
    """

    BLANK = -1  # A block that does no render

    def __init__(
        self,
        rect: Tuple[Tuple[int, int], Tuple[int, int]],
        blocks: List[int],
        palette_group: PaletteGroup,
        graphics_set: GraphicsSet,
        object_set_index: int,
    ):
        self.rect = rect
        self.blocks = blocks
        self.palette_group = palette_group
        self.graphics_set = graphics_set
        self.object_set_index = object_set_index
        self.selected = False
        self.block_cache = {}

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"{self.rect}, {self.blocks}, {self.palette_group}, {self.graphics_set}, {self.object_set_index}"
            f")"
        )

    @property
    def object_set_index(self) -> int:
        """
        The tileset
        """
        return self._object_set_index

    @object_set_index.setter
    def object_set_index(self, idx: int) -> None:
        self._object_set_index = idx
        self.tsa_data = ROM.get_tsa_data(idx)

    @property
    def x(self) -> int:
        """
        The x coordinate of the generator
        """
        return self._x

    @x.setter
    def x(self, x: int) -> None:
        self._x = x

    @property
    def y(self) -> int:
        """
        The y coordinate of the generator
        """
        return self._y

    @y.setter
    def y(self, y: int) -> None:
        self._y = y

    @property
    def position(self) -> Tuple[int, int]:
        """
        The position of the generator
        """
        return self.x, self.y

    @position.setter
    def position(self, position: Tuple[int, int]) -> None:
        self.x, self.y = position

    @property
    def width(self) -> int:
        """
        The width of the generator
        """
        return self._width

    @width.setter
    def width(self, width: int) -> None:
        self._width = max(width, 1)  # Cannot have a width of 0

    @property
    def height(self) -> int:
        """
        The height of the generator
        """
        return self._height

    @height.setter
    def height(self, height):
        self._height = max(height, 1)  # Cannot have a height of 0

    @property
    def size(self) -> Tuple[int, int]:
        """
        The width and height of the generator
        """
        return self.width, self.height

    @size.setter
    def size(self, size: Tuple[int, int]) -> None:
        self.width, self.height = size

    @property
    def rect(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """
        The position and size of the generator as a representation of into 2D space
        """
        return self.position, self.size

    @rect.setter
    def rect(self, rect: Tuple[Tuple[int, int], Tuple[int, int]]) -> None:
        self.position, self.size = rect

    def draw(self, painter: QPainter, block_length, transparent):
        # Saves run time by converting O(n^2) to O(n+m)
        x_offsets = [(self.x + i) * block_length for i in range(self.width)]
        y_offsets = [(self.y + i) * block_length for i in range(self.height)]
        self._draw(painter, block_length, transparent, x_offsets, y_offsets)

    def _draw(self, painter: QPainter, block_length, transparent, x_offsets, y_offsets):
        for i, (y, x) in enumerate(product(range(self.height), range(self.width))):
            if self.blocks[i] == self.BLANK:
                continue
            self._draw_block(painter, self.blocks[i], x_offsets[x], y_offsets[y], block_length, transparent)

    def _draw_block(self, painter: QPainter, block_index, x, y, block_length, transparent):
        if block_index not in self.block_cache:
            self.block_cache[block_index] = get_block(block_index, self.palette_group, self.graphics_set, self.tsa_data)

        self.block_cache[block_index].draw(
            painter,
            x,
            y,
            block_length=block_length,
            selected=self.selected,
            transparent=transparent,
        )

    def as_image(self) -> QImage:
        image = QImage(
            QSize(self.width * Block.SIDE_LENGTH, self.height * Block.SIDE_LENGTH),
            QImage.Format_RGB888,
        )

        bg_color = bg_color_for_object_set(self.object_set_index, 0)

        image.fill(bg_color)

        painter = QPainter(image)

        x_offsets = [i * Block.SIDE_LENGTH for i in range(self.width)]
        y_offsets = [i * Block.SIDE_LENGTH for i in range(self.height)]
        self._draw(painter, Block.SIDE_LENGTH, True, x_offsets, y_offsets)

        return image
