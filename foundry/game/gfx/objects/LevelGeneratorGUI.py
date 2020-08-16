from abc import abstractmethod, ABC
from typing import List, Tuple, Optional, Callable
from dataclasses import dataclass
from functools import wraps, lru_cache
import numpy as np

from PySide2.QtGui import QImage, QPainter

from foundry.game.File import ROM

from foundry.game.Tileset import Tileset
from foundry.game.ObjectDefinitions import BitMapPicture

from foundry.game.gfx.objects.Jump import Jump
from foundry.game.gfx.PatternTableHandler import PatternTableHandler
from foundry.game.gfx.Palette import bg_color_for_object_set
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects.EnemyItem import EnemyObject
from foundry.game.gfx.objects.ObjectLike import EXPANDS_BOTH, EXPANDS_HORIZ, EXPANDS_NOT, EXPANDS_VERT, ObjectLike

from foundry.game.ObjectDefinitions import ObjectDefinition as GeneratorDefinition
from smb3parse.objects.object_set import _ending_graphic_offset
from foundry.core.geometry.Size.Size import Size
from PySide2.QtCore import QSize
from foundry.game.Position import Position, LevelPosition
from foundry.game.Rect import Rect
from foundry.game.Range import Range
from smb3parse.asm6_converter import to_hex

from foundry.game.gfx.objects.LevelGeneratorBase import BlockGeneratorHandler, BlockGeneratorBase


SKY = 0
GROUND = 27

# not all objects provide a block index for blank block
BLANK = -1

SCREEN_HEIGHT = 15
SCREEN_WIDTH = 16



def request(req: str, operation: str):
    """Requests for a value to change"""
    def middle(func: Callable):
        """Makes the decorator that is returned"""
        @wraps(func)
        def wrapper(self: LevelBlockGenerator, *args, **kwargs):
            """Sets the flag for what we are concerned about"""
            if getattr(self, req):
                func_operation = getattr(self, operation)
                func_operation(self, *args, **kwargs)
                setattr(self, req, False)
            return func(self, *args, **kwargs)
        return wrapper
    return middle


def queue(req: str):
    """Queues for an update whenever needed"""
    def middle(func: Callable):
        """Makes the decorator that is returned"""
        @wraps(func)
        def wrapper(self: LevelBlockGenerator, *args, **kwargs):
            """Sets the flag to need an update"""
            setattr(self, req, True)
            return func(self, *args, *kwargs)
        return wrapper
    return middle


queue_render_update = queue("update_queued_render")
request_render_update = request("update_queued_render", "update_render")
queue_rect_update = queue("update_queue_rect")
request_rect_update = request("update_queue_rect", "update_rect")


class LevelBlockGenerator(BlockGeneratorHandler):
    """A level block generator that is editable and provides rendered blocks"""
    def __init__(self, block_generator: BlockGeneratorBase, block_function: Callable = None) -> None:
        super().__init__(block_generator=block_generator)

        self.block_function = block_function

        self.update_queued_render = True
        self._rendered_blocks = []

        self.update_queue_rect = True
        self._rendered_rect = None

    def __str__(self) -> str:
        return f"{self.__class__.__name__} at {self.position} with a size of {self.real_size}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.block_generator}, {self.block_function})"

    @classmethod
    def from_data(cls, tileset: int, data: dataclass, block_function: Callable = None) -> "LevelBlockGenerator":
        """Provides a level block generator from data"""
        return LevelBlockGenerator(BlockGeneratorBase.generator_from_bytes(tileset=tileset, data=data), block_function)

    @property
    def position(self) -> Position:
        """The horizontal position of the generator"""
        return super().position

    @queue_render_update
    @position.setter
    def position(self, pos: Position) -> None:
        super().position = pos

    @property
    def vertical_position(self) -> Position:
        """The vertical position of the generator"""
        return super().vertical_position

    @queue_render_update
    @vertical_position.setter
    def vertical_position(self, pos: Position) -> None:
        super().vertical_position = pos

    @property
    def base_size(self) -> Size:
        """The base size of the generator"""
        return super().base_size

    @queue_render_update
    @base_size.setter
    def base_size(self, size: Size) -> None:
        super().base_size = size

    @property
    def bmp_size(self) -> Size:
        """The size of the bmp"""
        return super().bmp_size

    @property
    def type(self) -> int:
        """The type of the generator in terms of its tileset"""
        return super().type

    @queue_render_update
    @type.setter
    def type(self, t: int) -> None:
        super().type = t

    @property
    def tileset(self) -> int:
        """The tileset that this generator resides"""
        return super().tileset

    @queue_render_update
    @tileset.setter
    def tileset(self, tileset: int) -> None:
        super().tileset = tileset

    @request_render_update
    @property
    def rendered_blocks(self) -> np.shape:
        """Provides the rendered blocks from the generator"""
        return self._rendered_blocks

    @request_rect_update
    @property
    def rendered_rect(self) -> Rect:
        """Provides the rendered rect"""
        return self._rendered_rect

    @property
    def generator(self) -> GeneratorDefinition:
        """Provides the generator definition"""
        return self.block_generator.generator

    @property
    def blocks(self) -> List[int]:
        """Provides the blocks that are specified in the yaml file"""
        return self.generator.block_design.blocks

    @abstractmethod
    def update_rect(self):
        """Updates the rect to be correct"""

    @queue_rect_update
    def update_render(self):
        """Update the data that is rendered"""
        self._render()

    @abstractmethod
    def _render(self) -> None:
        pass

    @property
    @abstractmethod
    def expands(self) -> int:
        """Determines how the object expands"""

    @property
    @abstractmethod
    def primary_expansion(self) -> int:
        """Determines what the primary expansion is"""

    def get_level_blocks(self, rect: Rect) -> np.shape[int]:
        """Provides the level blocks for generators that interact with the level"""
        return self.block_function(rect)

    def get_level_block_from_pos(self, pos: Position) -> int:
        return self.block_function(pos)

    def contains_in_range(self, rect: Rect, nums: Tuple[int]) -> bool:
        return any([any(self.get_level_blocks(rect) == num)] for num in nums)

    @lru_cache
    def get_block(self, index: int) -> int:
        try:
            block = self.blocks[index]
        except IndexError:
            try:
                block = self.blocks[0]
            except IndexError:
                block = 0
        return block


class LevelGeneratorToSky(LevelBlockGenerator):
    """An generator the goes to the sky"""

    @property
    def expands(self):
        """Tells what way the generator expands"""
        return EXPANDS_NOT

    @property
    def primary_expansion(self) -> int:
        """Tells the primary method of expansion"""
        return EXPANDS_NOT

    def update_rect(self):
        """Update the rect to the correct value"""
        pos, size = Position(self.position.x, SKY), Size(self.bmp_size.width, self.position.y - SKY + 1)
        self._rendered_rect = Rect.from_size_and_position(size=size, pos=pos)

    def _render(self, regular: bool = True) -> None:
        """
        Draws an blocks to the sky from a given y position
        Note: This class is a very unique case and needs to be updated if desired to be used by bigger applications
        """
        blocks_to_draw = np.zeros((1, self.position.y - SKY + 1))
        blocks_to_draw[-1] = 1  # The last element is different
        blocks_to_draw = np.array([self.get_block(block) for block in blocks_to_draw])
        self._rendered_blocks = blocks_to_draw


class LevelGeneratorDesertPipeBox(LevelBlockGenerator):
    """The generator that makes the pipe prefabs in the desert levels"""
    LINES_PER_ROW = 4

    @property
    def expands(self):
        """Tells what way the generator expands"""
        return EXPANDS_HORIZ

    @property
    def primary_expansion(self) -> int:
        """Tells the primary method of expansion"""
        return EXPANDS_HORIZ

    @property
    def horizontal_segments(self) -> int:
        """The amount of pipe sections horizontally"""
        return (self.base_size.width + 1) * 2

    @property
    def vertical_size(self) -> int:
        """The amount of vertical space between each segment"""
        return self.bmp_size.height + 1

    def update_rect(self):
        """Update the rect to the correct value"""
        pos = Position(self.position.x, SKY)
        size = Size(self.horizontal_segments * self.bmp_size.width, self.LINES_PER_ROW * self.vertical_size)
        self._rendered_rect = Rect.from_size_and_position(size=size, pos=pos)

    def _render(self) -> None:
        """
        Segments are the horizontal sections, which are 8 blocks long
        two of those are drawn per length bit
        rows are the 4 block high rows Mario can walk in
        """
        blocks_to_draw = []
        is_pipe_box_type_b = self.type == 18  # Todo: Move this to a new class

        for row_number in range(self.vertical_size):
            for line in range(self.LINES_PER_ROW):
                # pipe box type b does not repeat the horizontal beams
                line += 1 if is_pipe_box_type_b and row_number > 0 and line == 0 else 0

                rng = Range.from_offset(line * self.bmp_size.width, self.bmp_size.width)
                for _ in range(self.horizontal_segments):
                    blocks_to_draw.extend(self.blocks[rng.start:rng.end])

        # draw another open row or draw the first row again to close the box
        start = self.bmp_size.width if is_pipe_box_type_b else 0
        rng = Range.from_offset(start, self.bmp_size.width)
        for _ in range(self.horizontal_segments):
            blocks_to_draw.extend(self.blocks[rng.start:rng.end])

        blocks_to_draw = np.asarray(blocks_to_draw)
        blocks_to_draw.reshape((self.rendered_rect.abs_size.width, self.rendered_rect.abs_size.height))
        self._rendered_blocks = blocks_to_draw


class LevelGeneratorDiagonal(LevelBlockGenerator):
    """The class that makes diagonal blocks"""

    VERTICAL_OFFSET = 0
    HORIZONTAL_OFFSET = 0

    @property
    @abstractmethod
    def slope(self) -> int:
        """The slope from self.blocks"""

    @property
    @abstractmethod
    def body(self) -> int:
        """The body from self.blocks"""

    @abstractmethod
    def _render(self) -> None:
        """The render routine for the level object"""

    @abstractmethod
    def get_block_from_position(self, x: int, y: int) -> int:
        """Returns the corresponding block for a given position"""

    @property
    def expands(self) -> int:
        """Tells what way the generator expands"""
        return EXPANDS_HORIZ

    @property
    def primary_expansion(self) -> int:
        """Tells the primary method of expansion"""
        return EXPANDS_HORIZ

    def render_slope(self) -> np.array:
        """Returns the size, pos, and blocks_to_draw of the rendered slope"""
        blocks_to_draw = np.empty((self.rendered_rect.abs_size.width, self.rendered_rect.abs_size.height))
        for i in range(self.rendered_rect.abs_size.width):
            for j in range(self.rendered_rect.abs_size.height):
                blocks_to_draw[i, j] = self.get_block_from_position(i, j)
        return blocks_to_draw


class LevelGeneratorDiagonal45(LevelGeneratorDiagonal):
    """The default 45 degree generator"""

    @property
    @abstractmethod
    def slope(self) -> int:
        """The slope from self.blocks"""

    @property
    @abstractmethod
    def body(self) -> int:
        """The body from self.blocks"""

    @abstractmethod
    def _render(self) -> None:
        """The render routine for the level object"""

    def update_rect(self):
        """Update the rect to the correct value"""
        pos, size = self.position + Position(self.HORIZONTAL_OFFSET, self.VERTICAL_OFFSET), self.base_size
        self._rendered_rect = Rect.from_size_and_position(size=size, pos=pos)

    def get_block_from_position(self, x: int, y: int) -> int:
        """Returns the appropriate block from a position"""
        if x == y:
            return self.slope
        elif x < y:
            return self.body
        else:
            return BLANK


class LevelGeneratorDiagonal30(LevelGeneratorDiagonal):
    """The default 30 degree generator"""
    @property
    @abstractmethod
    def slope(self) -> List[int]:
        """The slope from self.blocks"""

    @property
    @abstractmethod
    def body(self) -> int:
        """The body from self.blocks"""

    @abstractmethod
    def _render(self) -> None:
        """The render routine for the level object"""

    def update_rect(self):
        """Update the rect to the correct value"""
        pos, size = self.position + Position(self.HORIZONTAL_OFFSET, self.VERTICAL_OFFSET), self.base_size * Size(2, 1)
        self._rendered_rect = Rect.from_size_and_position(size=size, pos=pos)

    def get_block_from_position(self, x: int, y: int) -> int:
        """Returns the appropriate block from a position"""
        if x // 2 == y:
            return self.slope[x % 2]
        elif x // 2 < y:
            return self.body
        else:
            return BLANK


class LevelGeneratorDiagonal60(LevelGeneratorDiagonal):
    """The default 60 degree generator"""
    @property
    @abstractmethod
    def slope(self) -> List[int]:
        """The slope from self.blocks"""

    @property
    @abstractmethod
    def body(self) -> Optional[int]:
        """The body from self.blocks"""

    @abstractmethod
    def _render(self) -> None:
        """The render routine for the level object"""

    def update_rect(self):
        """Update the rect to the correct value"""
        pos, size = self.position + Position(self.HORIZONTAL_OFFSET, self.VERTICAL_OFFSET), self.base_size * Size(1, 2)
        self._rendered_rect = Rect.from_size_and_position(size=size, pos=pos)

    def get_block_from_position(self, x: int, y: int) -> int:
        """Returns the appropriate block from a position"""
        if y // 2 == x:
            return self.slope[y % 2]
        elif y // 2 < x:
            return self.body
        else:
            return BLANK


class DownRightDiagonal(LevelGeneratorDiagonal, ABC):
    """A \\ rightwards diagonal slope"""
    def _render(self) -> None:
        self._rendered_blocks = self.render_slope()


class DownLeftDiagonal(LevelGeneratorDiagonal, ABC):
    """A / leftwards diagonal slope"""
    def _render(self) -> None:
        self._rendered_blocks = np.flip(self.render_slope(), 1)


class UpRightDiagonal(LevelGeneratorDiagonal, ABC):
    """A \\ rightwards diagonal slope"""
    def _render(self) -> None:
        self._rendered_blocks = np.flip(self.render_slope(), 0)


class UpLeftDiagonal(LevelGeneratorDiagonal, ABC):
    """A / leftwards diagonal slope"""
    def _render(self) -> None:
        self._rendered_blocks = np.flip(np.flip(self.render_slope(), 0), 1)


class LevelGeneratorDiagonalDownLeft45(DownLeftDiagonal, LevelGeneratorDiagonal45):
    """A 45 degree / slope"""
    HORIZONTAL_OFFSET = 1

    @property
    def slope(self) -> int:
        """The slope from self.blocks"""
        return self.get_block(0)

    @property
    def body(self) -> int:
        """The body from self.blocks"""
        return self.get_block(1)


class LevelGeneratorDiagonalDownLeft30(DownLeftDiagonal, LevelGeneratorDiagonal30):
    """A 30 degree / slope"""
    HORIZONTAL_OFFSET = 2

    @property
    def slope(self) -> List[int]:
        """The slope from self.blocks"""
        return [self.get_block(1), self.get_block(0)]

    @property
    def body(self) -> int:
        """The body from self.blocks"""
        return self.get_block(2)


class LevelGeneratorDiagonalDownRight60(DownRightDiagonal, LevelGeneratorDiagonal60):
    """A 60 degree \\ slope"""
    @property
    def slope(self) -> List[int]:
        """The slope from self.blocks"""
        return [self.get_block(0), self.get_block(1)]

    @property
    def body(self) -> int:
        """The body from self.blocks"""
        return self.get_block(2)


class LevelGeneratorDiagonalDownLeft60(DownLeftDiagonal, LevelGeneratorDiagonal60):
    """A 60 degree / slope"""
    HORIZONTAL_OFFSET = 1
    VERTICAL_OFFSET = 4

    @property
    def slope(self) -> List[int]:
        """The slope from self.blocks"""
        return [self.get_block(0), self.get_block(1)]

    @property
    def body(self) -> int:
        """The body from self.blocks"""
        return self.get_block(2)


class LevelGeneratorDiagonalDownRight30(DownRightDiagonal, LevelGeneratorDiagonal30):
    """A 30 degree \\ slope"""
    @property
    def slope(self) -> List[int]:
        """The slope from self.blocks"""
        return [self.get_block(1), self.get_block(2)]

    @property
    def body(self) -> int:
        """The body from self.blocks"""
        return self.get_block(0)


class LevelGeneratorDiagonalUpRight30(UpRightDiagonal, LevelGeneratorDiagonal30):
    """A 30 degree / slope"""
    @property
    def slope(self) -> List[int]:
        """The slope from self.blocks"""
        return [self.get_block(1), self.get_block(2)]

    @property
    def body(self) -> int:
        """The body from self.blocks"""
        return self.get_block(0)


class LevelGeneratorDiagonalUpLeft30(UpLeftDiagonal, LevelGeneratorDiagonal30):
    """A 30 degree \\ slope"""
    @property
    def slope(self) -> List[int]:
        """The slope from self.blocks"""
        return [self.get_block(1), self.get_block(0)]

    @property
    def body(self) -> int:
        """The body from self.blocks"""
        return self.get_block(2)


class LevelGeneratorDiagonalDownRight45(DownRightDiagonal, LevelGeneratorDiagonal45):
    """A 45 degree \\ slope"""
    @property
    def slope(self) -> int:
        """The slope from self.blocks"""
        return self.get_block(1)

    @property
    def body(self) -> int:
        """The body from self.blocks"""
        return self.get_block(0)


class LevelGeneratorDiagonalUpRight45(UpRightDiagonal, LevelGeneratorDiagonal45):
    """A 45 degree / slope"""
    @property
    def slope(self) -> int:
        """The slope from self.blocks"""
        return self.get_block(1)

    @property
    def body(self) -> int:
        """The body from self.blocks"""
        return self.get_block(0)


class LevelGeneratorDiagonalUpLeft45(UpLeftDiagonal, LevelGeneratorDiagonal45):
    """A 45 degree \\ slope"""
    @property
    def slope(self) -> int:
        """The slope from self.blocks"""
        return self.get_block(0)

    @property
    def body(self) -> int:
        """The body from self.blocks"""
        return self.get_block(1)


class LevelGeneratorEndingBackground(LevelBlockGenerator):
    """Generator prefab for the end of the level"""
    GROUND = 26
    ENDING_GRAPHIC_HEIGHT = 6
    FLOOR_HEIGHT = 1

    @property
    def expands(self) -> int:
        """Tells what way the generator expands"""
        return EXPANDS_NOT

    @property
    def primary_expansion(self) -> int:
        """Tells the primary method of expansion"""
        return EXPANDS_NOT

    @property
    def fade_block(self) -> int:
        """The block that is used for fading between backgrounds"""
        return self.get_block(0)

    @property
    def background(self) -> int:
        """The black background block"""
        return self.get_block(1)

    @property
    def page_limit(self) -> int:
        """Helps determine how long the generator is"""
        return LevelPosition.SCREEN_WIDTH - (self.position.x % LevelPosition.SCREEN_WIDTH)

    @property
    def rom_offset(self) -> int:
        """The offset in ROM to the prefab"""
        return _ending_graphic_offset[self.tileset]

    def update_rect(self):
        """Update the rect to the correct value"""
        pos = LevelPosition.from_pos(Position(self.position.x, 0))
        size = Size(LevelPosition.SCREEN_WIDTH + pos.rel_x_inverse, self.GROUND)
        self._rendered_rect = Rect.from_size_and_position(size=size, pos=pos)

    def _render(self) -> None:
        """Draws the end of level background"""
        size = self.rendered_rect.abs_size
        blocks_to_draw = np.full((size.width, size.height), self.background)
        fade_to_draw = np.full((size.width,), self.fade_block)
        blocks_to_draw[:, 0] = fade_to_draw

        data = ROM().bulk_read(position=self.rom_offset, count=SCREEN_WIDTH * self.ENDING_GRAPHIC_HEIGHT)
        custom_blocks = np.asarray(data)
        custom_blocks.reshape((SCREEN_WIDTH, self.ENDING_GRAPHIC_HEIGHT))
        x_off, y_off = self.page_limit + 1, self.GROUND - self.ENDING_GRAPHIC_HEIGHT
        blocks_to_draw[x_off: x_off + SCREEN_WIDTH, y_off: y_off + self.ENDING_GRAPHIC_HEIGHT] = custom_blocks
        self._rendered_blocks = blocks_to_draw


class LevelGeneratorBlockGetter(LevelBlockGenerator, ABC):
    """The base for a generator that provides a mini picture to be rendered"""

    @abstractmethod
    def get_block_layout(self):
        """Returns a tiny image of generator"""

    def update_rect(self):
        """Update the rect to the correct value"""
        self._rendered_rect = Rect.from_size_and_position(size=self.real_size, pos=self.position)

    def _render(self) -> None:
        """
        Draws an blocks to the sky from a given y position
        Note: This class is a very unique case and needs to be updated if desired to be used by bigger applications
        """
        blocks_to_draw = np.empty((self.rendered_rect.abs_size.width, self.rendered_rect.abs_size.height))
        base_blocks = self.get_block_layout()
        blocks = self.blocks_to_bmp()
        ix, iix, iy, iiy = 0, 0, 0, 0
        for x, y in np.ndindex(base_blocks.shape):
            iix, iiy = ix + self.bmp_size.width, iy + self.bmp_size.height
            blocks_to_draw[ix: iix, iy: iiy] = blocks[:, :, base_blocks[x, y]]
            ix, iy = iix, iiy

        self._rendered_blocks = blocks_to_draw

    def blocks_to_bmp(self) -> np.array:
        """Provides the blocks in terms of units of the bmp"""
        blocks = np.asarray(self.blocks)
        return np.reshape(blocks, (self.bmp_size.width, self.bmp_size.height, -1))


class EndOnTopAndBottom(LevelGeneratorBlockGetter, ABC):
    """Generates a top and bottom"""
    def get_block_layout(self):
        """Returns a tiny image of generator"""
        layout = np.full((self.base_size.width, self.base_size.height), 1)
        layout[0] = 0
        layout[-1] = 2
        return layout


class EndOnBottom(LevelGeneratorBlockGetter, ABC):
    """Only generates a bottom"""
    def get_block_layout(self):
        """Returns a tiny image of generator"""
        layout = np.full((self.base_size.width, self.base_size.height), 0)
        layout[-1] = 1
        return layout


class EndOnTop(LevelGeneratorBlockGetter, ABC):
    """Only generates a top"""
    def get_block_layout(self):
        """Returns a tiny image of generator"""
        layout = np.full((self.base_size.width, self.base_size.height), 1)
        layout[0] = 0
        return layout


class EndOnDoubleTop(LevelGeneratorBlockGetter, ABC):
    """Generates two layers that represent the top and then precedes to copy the same block over and over"""
    def get_block_layout(self):
        """Returns a tiny image of generator"""
        layout = np.full((self.base_size.width, self.base_size.height), 2)
        layout[0] = 0
        layout[1] = 1
        return layout


class EndOnSides(LevelGeneratorBlockGetter, ABC):
    """Provides sides to the generator"""
    def get_block_layout(self):
        """Returns a tiny image of generator"""
        layout = np.full((self.base_size.width, self.base_size.height), 1)
        layout[:, 0] = 0
        layout[:, -1] = 2
        return layout


class EndOnLeft(LevelGeneratorBlockGetter, ABC):
    """Provides a left side to the generator"""
    def get_block_layout(self):
        """Returns a tiny image of generator"""
        layout = np.full((self.base_size.width, self.base_size.height), 1)
        layout[:, 0] = 0
        return layout


class EndOnRight(LevelGeneratorBlockGetter, ABC):
    """Provides a left side to the generator"""
    def get_block_layout(self):
        """Returns a tiny image of generator"""
        layout = np.full((self.base_size.width, self.base_size.height), 1)
        layout[:, -1] = 2
        return layout


class EndOnAllSides(LevelGeneratorBlockGetter, ABC):
    """Provides a generator with custom sides and edges"""
    def get_block_layout(self):
        """Returns a tiny image of generator"""
        layout = np.full((self.base_size.width, self.base_size.height), 4)
        layout[:, 0] = 3; layout[:, -1] = 5; layout[0] = 1; layout[-1] = 7
        layout[0, 0] = 0; layout[0, -1] = 2; layout[-1, 0] = 6; layout = [-1, -1] = 8
        return layout


class LevelGeneratorSimple(LevelBlockGenerator, ABC):
    """A non-expandable level generator"""
    @property
    def expands(self) -> int:
        """Tells what way the generator expands"""
        return EXPANDS_NOT

    @property
    def primary_expansion(self) -> int:
        """Tells the primary method of expansion"""
        return EXPANDS_NOT

    def update_rect(self):
        """Update the rect to the correct value"""
        self._rendered_rect = Rect.from_size_and_position(size=self.bmp_size, pos=self.position)


class LevelGeneratorVertical(LevelGeneratorBlockGetter, ABC):
    """A default vertical generator"""
    @property
    def expands(self) -> int:
        """Tells what way the generator expands"""
        return EXPANDS_VERT

    def primary_expansion(self) -> int:
        """Tells the primary method of expansion"""
        if len(self.to_bytes()[1]) == 4:
            return EXPANDS_BOTH
        else:
            return EXPANDS_VERT


class LevelGeneratorHorizontal(LevelGeneratorBlockGetter, ABC):
    """A default horizontal generator"""
    @property
    def expands(self) -> int:
        """Tells what way the generator expands"""
        return EXPANDS_HORIZ

    def primary_expansion(self) -> int:
        """Tells the primary method of expansion"""
        if len(self.to_bytes()[1]) == 4:
            return EXPANDS_BOTH
        else:
            return EXPANDS_HORIZ


class LevelGeneratorVerticalWithTop(EndOnTop, LevelGeneratorVertical):
    """Vertical generator with a custom top"""


class LevelGeneratorVerticalWithDoubleTop(EndOnDoubleTop, LevelGeneratorVertical):
    """Vertical generator with two custom tops"""


class LevelGeneratorVerticalWithAllSides(EndOnAllSides, LevelGeneratorVertical):
    """Vertical generator with custom sides and edges"""


class LevelGeneratorVerticalWithTopAndBottom(EndOnTopAndBottom, LevelGeneratorVertical):
    """Vertical generator with a custom bottom and top"""


class LevelGeneratorVerticalWithBottom(EndOnBottom, LevelGeneratorVertical):
    """Vertical generator with a custom bottom"""


class LevelGeneratorHorizontal5Byte(LevelGeneratorHorizontal):
    """An object that has an apos: Position, *_) ->ermine the block displayed"""
    """Generates a top and bottom"""
    def get_block_layout(self):
        """Returns a tiny image of generator"""
        layout = np.zeros((self.base_size.width, self.base_size.height))
        return layout

    def blocks_to_bmp(self) -> np.array:
        """Provides the blocks in terms of units of the bmp"""
        blocks = np.asarray(self.to_bytes()[1][4] for _ in range(self.bmp_size.width * self.bmp_size.height))
        return np.reshape(blocks, (self.bmp_size.width, self.bmp_size.height, -1))


class LevelGeneratorHorizontalWithTop(EndOnTop, LevelGeneratorHorizontal):
    """Horizontal generator with a custom top"""


class LevelGeneratorHorizontalWithBottom(EndOnBottom, LevelGeneratorHorizontal):
    """Horizontal generator with a custom bottom"""


class LevelGeneratorHorizontalWithAllSides(EndOnAllSides, LevelGeneratorHorizontal):
    """Horizontal generator with custom sides and edges"""


class LevelGeneratorHorizontalWithSides(EndOnSides, LevelGeneratorHorizontal):
    """Horizontal generator with both sides"""


class LevelGeneratorHorizontalWithLeftSide(EndOnLeft, LevelGeneratorHorizontal):
    """Horizontal generator with only a left side"""


class LevelGeneratorHorizontalWithRightSide(EndOnRight, LevelGeneratorHorizontal):
    """Horizontal generator with only a right side"""


class LevelGeneratorHorizontalWithSidesAndTop(LevelGeneratorHorizontal):
    """Horizontal generator with two sides and a top"""
    def get_block_layout(self):
        """Returns a tiny image of generator"""
        layout = np.full((self.base_size.width, self.base_size.height), 4)
        layout[:, 0] = 3
        layout[:, -1] = 5
        layout[0] = 1

        layout[0, 0] = 0
        layout[0, -1] = 2
        return layout


class LevelObjectPlainsPlatformFloating(LevelGeneratorHorizontal):
    """A floating block with a shadow"""
    @property
    def shadow_block(self) -> List[int]:
        """The shadow blocks to display"""
        return [
            0xC1, -1, 0xC0, -1, -1, 0xC4, 0xC2, 0xC5, 0xC3
        ]

    def get_block_layout(self):
        """Returns a tiny image of generator"""
        layout = np.full((self.base_size.width, self.base_size.height), 4)
        layout[:, 0] = 3; layout[:, -2] = 5; layout[0] = 1; layout[-2] = 7
        layout[:, -1] = 14; layout[-1] = 16
        layout[0, -1] = 11; layout[-1, 0] = 15; layout[-1, -1] = 17
        layout[0, 0] = 0; layout[0, -2] = 2; layout[-2, 0] = 6; layout = [-2, -2] = 8
        return layout

    def update_rect(self):
        """Update the rect to the correct value"""
        self._rendered_rect = Rect.from_size_and_position(size=self.real_size + 1, pos=self.position)

    def blocks_to_bmp(self) -> np.array:
        """Provides the blocks in terms of units of the bmp"""
        blocks = np.asarray(self.blocks + self.shadow_block)
        return np.reshape(blocks, (self.bmp_size.width, self.bmp_size.height, -1))


class LevelGeneratorInteractable(LevelBlockGenerator, ABC):
    """Re-renders the object if something is moved"""
    def backtrace_update(self) -> None:
        """Provides an update whenever the level is updated"""
        self._render()


class LevelGeneratorPyramidToGround(LevelGeneratorSimple, LevelGeneratorInteractable):
    """Makes a pyramid that grows horizontally in both directions that extends to the ground"""

    def update_rect(self):
        """Update the rect to the correct value"""
        p = pos = self.position
        size = Size(2, 1)
        while p.y >= GROUND:
            p -= 1; pos.x -= 1; size += Size(2, 1)
            if self.get_level_block_from_pos(p) != 0x80:
                break
        self._rendered_rect = Rect.from_size_and_position(size=size, pos=pos)

    def _render(self) -> None:
        """Draws a pyramid that expands every block"""
        blank, left_slope, left_fill, right_fill, right_slope = self.blocks[0:5]
        blocks_to_draw = np.array((left_slope, right_slope))
        for idx in range(self.rendered_rect.abs_size.height - 1):
            blocks = np.empty(((idx + 1) * 2, (idx + 1)))
            blocks[0:, 0:] = blocks_to_draw
            blocks[-1] = np.array([left_slope] + [left_fill] * idx + [right_fill] * idx + [right_slope])

        self._rendered_blocks = blocks_to_draw


class LevelGeneratorPlainsPlatformToGround(LevelGeneratorHorizontal, LevelGeneratorInteractable):
    """A block generator that stretches to the ground and provides a shadow"""
    def get_corner_shadow(self, level_block: int) -> int:
        """Provide the correct corner shadow"""
        try:
            return self.CORNER_SHADOWS[level_block]
        except KeyError:
            return level_block & 0xC0 | 0x0B

    def get_edge_shadow(self, level_block: int) -> int:
        """Provide the correct edge shadow"""
        try:
            return self.SHADOW_TO_BLOCK[level_block]
        except KeyError:
            return 0xC4

    CORNER_SHADOWS = {
        0x80: 0xC0, 0x90: 0x9D, 0x9F: 0x9D
    }

    SHADOW_TO_BLOCK = {
        0x53: 0x00, 0x57: 0x00,
        0x07: 0x0C, 0x09: 0x0C, 0x0A: 0x0F, 0x0D: 0x0F,
        0x47: 0x4C, 0x49: 0x4C, 0x4A: 0x4F, 0x4D: 0x4F,
        0x87: 0x8C, 0x89: 0x8C, 0x8A: 0x8F, 0x8D: 0x8F,
        0xC7: 0xCC, 0xC9: 0xCC, 0xCA: 0xCF, 0xCD: 0xCF,
        0x90: 0x99, 0x94: 0x9E, 0x91: 0x9A, 0x95: 0x9F, 0x92: 0x9B, 0x96: 0x9E, 0x93: 0x9C, 0x97: 0x9E, 0x98: 0x9E
    }

    def update_rect(self):
        """Update the rect to the correct value"""
        rect = Rect.from_size_and_position(Size(1, self.position.y - GROUND + 1), self.position + Position(0, 1))
        level_blocks = self.get_level_blocks(rect)
        size = self.real_size + Size(1, 1)
        for level_block in level_blocks:
            if level_block == 0x51 or level_blocks == 0x53:
                break
            size.width += 1
        self._rendered_rect = Rect.from_size_and_position(size=size, pos=self.position)

    def get_block_layout(self) -> np.array:
        """Returns a tiny image of generator"""
        layout = np.full((self.base_size.width, self.base_size.height), 4)
        layout[:, 0] = 3; layout[:, -2] = 5; layout[0] = 1; layout[-1] = 7; layout[:, -1] = 10
        layout[-1, -1] = 9; layout[0, 0] = 0; layout[0, -2] = 2; layout[-1, 0] = 6; layout = [-1, -2] = 8
        return layout

    def get_block_from_layout(self, idx: int, level_block: int) -> int:
        """Returns the appropriate block from a given location"""
        if 0 >= idx >= 8:
            return self.get_block(idx)
        elif 9 == idx:
            return self.get_corner_shadow(level_block=level_block)
        elif 10 == idx:
            return self.get_edge_shadow(level_block=level_block)
        else:
            return NotImplemented

    def _render(self) -> None:
        """
        A simple render routine that disregards the bmp to allow for faster speed
        """
        blocks_to_draw = self.get_block_layout()
        level_blocks = self.get_level_blocks(self.rendered_rect)
        v_get_block_from_layout = np.vectorize(self.get_block_from_layout)
        self._rendered_blocks = v_get_block_from_layout(blocks_to_draw, level_blocks)


class LevelGeneratorBushPrefab(LevelGeneratorSimple, LevelGeneratorInteractable):
    """Provides a bush that interacts minimally with its surroundings"""
    @staticmethod
    def get_block_from_idx(block: int, level_block: int) -> int:
        """Provides a block from an index and level block"""
        if block == BLANK or block == 0x80:
            return BLANK
        if block == 0x93 or block == 0x94:
            return block
        if block == level_block or not 0x90 <= level_block <= 0x9F:
            return block
        if block == 0x90 or block == 0x91:
            return block + 2
        else:
            return 0x98

    def _render(self) -> None:
        level_blocks = self.get_level_blocks(self.rendered_rect)
        blocks = np.asarray(self.blocks)
        blocks.reshape((self.rendered_rect.width, self.rendered_rect.height))
        vec_block = np.vectorize(self.get_block_from_idx)
        self._rendered_blocks = vec_block(blocks, level_blocks)


class LevelGeneratorFortressPillars(LevelGeneratorInteractable):
    """Makes pillars that go to the ground"""
    @property
    def expands(self) -> int:
        """Tells what way the generator expands"""
        return EXPANDS_HORIZ

    @property
    def primary_expansion(self) -> int:
        """Tells the primary method of expansion"""
        return EXPANDS_HORIZ

    @property
    def top_pillar(self) -> int:
        """The top of the pillar"""
        return self.get_block(0)

    @property
    def middle_pillar(self) -> int:
        """The middle of the pillar"""
        return self.get_block(1)

    @property
    def bottom_pillar(self) -> int:
        """The bottom of the pillar"""
        return self.get_block(2)

    @property
    def top_shadow(self) -> int:
        """The top of the shadow"""
        return self.get_block(3)

    @property
    def middle_shadow(self) -> int:
        """The middle of the shadow"""
        return self.get_block(4)

    @property
    def continue_block(self) -> int:
        """The block to allow for continuation of the pillar"""
        return self.get_block(5)

    @property
    def pillars(self) -> List[Position]:
        """Provides the positions for each pillar"""
        return [self.position + Position(self.bmp_size.width * idx, 0) for idx in range(self.base_size.width + 1)]

    def get_pillar_size(self, pos: Position):
        """Provides the length of a pillar"""
        pos, size = Position(pos.x, pos.y + 1), 1
        while pos.y >= GROUND:
            size += 1
            pos.y += 1
            if self.get_level_block_from_pos(pos) != self.continue_block:
                break
        return size

    def update_rect(self):
        """Update the rect to the correct value"""
        width = self.bmp_size.width
        size = Size(width * (self.base_size.width + 1), max([self.get_pillar_size(pillar) for pillar in self.pillars]))
        return Rect.from_size_and_position(size, self.position)

    def _render(self) -> None:
        """Draws an blocks to the sky from a given y position"""
        blocks_to_draw = np.full((self.rendered_rect.abs_size.width, self.rendered_rect.abs_size.height), -1)
        for idx, pillar in enumerate(self.pillars):
            size = self.get_pillar_size(pillar)
            pil = np.full((size,), self.middle_pillar)
            pil[0] = self.top_pillar
            pil[-1] = self.bottom_pillar
            sha = np.full((size,), self.middle_shadow)
            sha[0] = self.top_shadow
            column = idx * self.base_size.width
            blocks_to_draw[column] = pil
            blocks_to_draw[column + 1] = sha
        self._rendered_blocks = blocks_to_draw


class LevelObjectFillBackgroundHorizontalLevel(LevelBlockGenerator):
    """Fills a horizontal's level background"""
    def expands(self) -> int:
        """Tells what way the generator expands"""
        return EXPANDS_NOT

    def primary_expansion(self) -> int:
        """Tells the primary method of expansion"""
        return EXPANDS_NOT

    def update_rect(self):
        """Update the rect to the correct value"""
        pos, size = Position(0, 0), Size(16 * 15, 26)
        self._rendered_rect = Rect.from_size_and_position(size=size, pos=pos)

    def _render(self, regular: int = True) -> None:
        self._rendered_blocks = np.full((16 * 15, 26), self.get_block(0))


class LevelObjectDownwardPipe(LevelGeneratorVerticalWithBottom):
    """A prefab for downward pipes"""
    @property
    def bmp_size(self) -> Size:
        """The size of the segments of the pipes"""
        return Size(2, 1)


class LevelObjectUpwardPipe(LevelGeneratorVerticalWithTop):
    """A prefab for upward pipes"""
    @property
    def bmp_size(self) -> Size:
        """The size of the segments of the pipes"""
        return Size(2, 1)


class LevelObjectLeftwardPipe(LevelGeneratorHorizontalWithLeftSide):
    """A prefab for leftward pipes"""
    @property
    def bmp_size(self) -> Size:
        """The side of the segments of the pipes"""
        return Size(1, 2)


class LevelObjectRightwardPipe(LevelGeneratorHorizontalWithRightSide):
    """A prefab for rightward pipes"""
    @property
    def bmp_size(self) -> Size:
        """The side of the segments of the pipes"""
        return Size(1, 2)
