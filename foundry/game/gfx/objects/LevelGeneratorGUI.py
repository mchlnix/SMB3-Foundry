from abc import abstractmethod
from typing import List, Tuple, Optional
from dataclasses import dataclass
from functools import wraps

from PySide2.QtGui import QImage, QPainter

from foundry.game.File import ROM

from foundry.game.ObjectSet import ObjectSet
from foundry.game.ObjectDefinitions import BitMapPicture

from foundry.game.gfx.objects.Jump import Jump
from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx.Palette import bg_color_for_object_set
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects.EnemyItem import EnemyObject
from foundry.game.gfx.objects.ObjectLike import EXPANDS_BOTH, EXPANDS_HORIZ, EXPANDS_NOT, EXPANDS_VERT, ObjectLike

from foundry.game.Size import Size
from PySide2.QtCore import QSize
from foundry.game.Position import Position
from foundry.game.Rect import Rect
from smb3parse.asm6_converter import to_hex

from foundry.game.gfx.objects.LevelGeneratorBase import BlockGeneratorHandler, BlockGeneratorBase


SKY = 0
GROUND = 27

# not all objects provide a block index for blank block
BLANK = -1

SCREEN_HEIGHT = 15
SCREEN_WIDTH = 16


def request_update(func):
    @wraps(func)
    def wrapper(self: LevelBlockGenerator, *args, **kwargs):
        if self.update_queued:
            self.update()
            self.update_queued = False
        return func(self, *args, **kwargs)
    return wrapper


def queue_update(func):
    @wraps(func)
    def wrapper(self: LevelBlockGenerator, *args, **kwargs):
        self.update_queued = True
        return func(self, *args, *kwargs)
    return wrapper


class LevelBlockGenerator(BlockGeneratorHandler):
    def __init__(self, block_generator: BlockGeneratorBase) -> None:
        super().__init__(block_generator=block_generator)
        self.update_queued = True
        self.blocks = []
        self._rendered_rect = Rect()

    @classmethod
    def from_data(cls, tileset: int, data: dataclass) -> "LevelBlockGenerator":
        return LevelBlockGenerator(BlockGeneratorBase.generator_from_bytes(tileset=tileset, data=data))

    @property
    def position(self) -> Position:
        """The horizontal position of the generator"""
        return super().position

    @queue_update
    @position.setter
    def position(self, pos: Position) -> None:
        super().position = pos

    @property
    def vertical_position(self) -> Position:
        """The vertical position of the generator"""
        return super().vertical_position

    @queue_update
    @vertical_position.setter
    def vertical_position(self, pos: Position) -> None:
        super().vertical_position = pos

    @property
    def base_size(self) -> Size:
        """The base size of the generator"""
        return super().base_size

    @queue_update
    @base_size.setter
    def base_size(self, size: Size) -> None:
        super().base_size = size

    @property
    def type(self) -> int:
        """The type of the generator in terms of its tileset"""
        return super().type

    @queue_update
    @type.setter
    def type(self, type: int) -> None:
        super().type = type

    @property
    def tileset(self) -> int:
        """The tileset that this generator resides"""
        return super().tileset

    @queue_update
    @tileset.setter
    def tileset(self, tileset: int) -> None:
        super().tileset = tileset

    @request_update
    @property
    def rendered_rect(self) -> Rect:
        return self._rendered_rect

    @rendered_rect.setter
    def rendered_rect(self, rect: Rect) -> None:
        self._rendered_rect = rect

    def update(self):
        self._render()

    @abstractmethod
    def _render(self) -> None:
        pass

    def get_blocks_and_positions(self) -> List[Tuple[Position, int]]:
        return self.rendered_positions

    @property
    @abstractmethod
    def expands(self) -> int:
        """Determines how the object expands"""

    @property
    @abstractmethod
    def primary_expansion(self) -> int:
        """Determines what the primary expansion is"""

    def to_asm6(self) -> str:
        pos = self.vertical_offset_pos(self.pos)
        if self.is_4byte:
            fourth_byte = f", {to_hex(self.size.width)}"
        else:
            fourth_byte = ""
        s = f"\t.byte {to_hex(self.domain << 5)} | {to_hex(pos.y)}, {to_hex(max(min(pos.x, 0xFF), 0))}, " \
            f"{to_hex(self.index)}{fourth_byte}; {self.description}\n"
        return s

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.description} at {self.pos.x}, {self.pos.y}"

    def _render_positions(self) -> None:
        if self.rect != self.last_rect:
            self.rendered_positions = tuple(zip(
                self.rendered_blocks,
                [pos + self.rendered_position for pos in self.rendered_size.positions()])
            )
            self.last_rect = self.rect

    def _confirm_render(self, size: Size, pos: Position, blocks: list) -> None:
        blocks = blocks if blocks else self.blocks
        self.rendered_size, self.rendered_position, self.rendered_blocks = size, pos, blocks
        self.rect = Rect.from_size_and_position(self.rendered_size, self.rendered_position)
        self._render_positions()

    def _get_obj_index(self) -> int:
        try:
            return self.objects_ref.index(self)
        except ValueError:
            # the object has not been added yet, so stick with the one given in the constructor
            return self.object_factory_idx

    def _if_intersects(self, rect: Rect) -> bool:
        return any(
            [
                rect.intersects(obj.get_rect()) for obj in self.objects_ref[:self._get_obj_index()]
            ]
        )

    def _get_background(self):
        background_routine_by_objectset = {
            0: self.default_background,
            1: self.default_background,
            2: self.fortress_background,
            3: self.default_background,
            4: self.sky_background,
            5: self.default_background,
            6: self.default_background,
            7: self.default_background,
            8: self.default_background,
            9: self.desert_background,
            10: self.default_background,
            11: self.default_background,
            12: self.sky_background,
            13: self.default_background,
            14: self.default_background,
            15: self.default_background
        }

        return background_routine_by_objectset[self.object_set.object_set_number]()

    def default_background(self) -> List[int]:
        return [self.object_set.background_block for _ in range(16 * 15 * 27)]

    def sky_background(self) -> List[int]:
        blocks = []
        level_rect = Rect.from_size_and_position(Size(16 * 15, 27), Position(0, 0))
        for pos in level_rect.positions():
            if pos.y != 0:
                blocks.append(self.object_set.background_block)
            else:
                blocks.append(0x86)
        return blocks

    def desert_background(self) -> List[int]:
        blocks = []
        level_rect = Rect.from_size_and_position(Size(16 * 15, 27), Position(0, 0))
        for pos in level_rect.positions():
            if pos.y != GROUND - 1:
                blocks.append(self.object_set.background_block)
            else:
                blocks.append(0x56)
        return blocks

    def fortress_background(self) -> List[int]:
        blocks = []
        fortress_blocks = [0x14, 0x15, 0x16, 0x17]
        level_rect = Rect.from_size_and_position(Size(16 * 15, 27), Position(0, 0))
        for pos in level_rect.positions():
            if pos.y == 0:
                blocks.append(0xE5)
            elif pos.y == 1:
                blocks.append(0x8E)
            elif pos.y == GROUND - 1:
                blocks.append(fortress_blocks[2 + pos.x % 2])
            elif pos.y == GROUND - 2:
                blocks.append(fortress_blocks[pos.x % 2])
            else:
                blocks.append(self.object_set.background_block)
        return blocks

    def _get_blocks(self, level_objs: List["LevelObject"]) -> List[int]:
        """Renders the level objects into memory"""
        level_rect = Rect.from_size_and_position(Size(16 * 15, 27), Position(0, 0))
        objects = self._get_background()
        for level_object in level_objs:
            for block in level_object.get_blocks_and_positions():
                if block[0] == -1:
                    continue
                try:
                    objects[level_rect.index_position(block[1])] = block[0]
                except IndexError:
                    pass
        for idx, obj in enumerate(objects):
            if obj > 0xFF:
                objects[idx] = ROM().get_byte(obj)

        return objects

    @staticmethod
    def _get_block_at_position(blocks: List[int], pos: Position) -> int:
        """Finds a block in level space"""
        if pos.y > 26:
            pos = Position(pos.x + (pos.y // 26) * 0x10, pos.y % 26)  # offset by the screen
        level_rect = Rect.from_size_and_position(Size(16 * 15, 26), Position(0, 0))
        try:
            return blocks[level_rect.index_position(pos)]
        except IndexError:
            return 0

    def get_block(self, index: int) -> int:
        try:
            block = self.blocks[index]
        except IndexError:
            try:
                block = self.blocks[0]
            except IndexError:
                block = 0
        return block
