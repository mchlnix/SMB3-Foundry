from abc import abstractmethod
from typing import List, Tuple
from dataclasses import dataclass

from PySide2.QtGui import QImage, QPainter

from foundry.game.File import ROM

from foundry.game.ObjectDefinitions import (
    PYRAMID_2,
    PYRAMID_TO_GROUND
)
from foundry.game.ObjectSet import ObjectSet
from foundry.game.gfx.objects.Jump import Jump
from foundry.game.gfx.Palette import bg_color_for_object_set
from foundry.game.gfx.drawable.Block import Block, get_block
from foundry.game.gfx.objects.EnemyItem import EnemyObject
from foundry.game.gfx.objects.ObjectLike import EXPANDS_BOTH, EXPANDS_HORIZ, EXPANDS_NOT, EXPANDS_VERT, ObjectLike

from foundry.game.Size import Size
from foundry.game.Position import Position
from foundry.game.Rect import Rect

SKY = 0
GROUND = 27

ENDING_STR = {
    EndType.UNIFORM: "Uniform",
    EndType.END_ON_TOP_OR_LEFT: "Top or Left",
    EndType.END_ON_BOTTOM_OR_RIGHT: "Bottom or Right",
    EndType.TWO_ENDS: "Top & Bottom/Left & Right",
}


# not all objects provide a block index for blank block
BLANK = -1

SCREEN_HEIGHT = 15
SCREEN_WIDTH = 16


def get_minimal_icon_object(level_object):
    """
    Gets an icon of the object if applicable
    :param level_object: A subclass of object like
    :return: The rendered object
    """
    if isinstance(level_object, EnemyObject):
        return level_object
    if isinstance(level_object, Jump):
        return None
    while (
            any(block not in level_object.rendered_blocks for block in
                level_object.blocks) and level_object.size.width < 0x10
    ):
        level_object.size.width += 1

        if level_object.is_4byte:
            level_object.size.height += 1

        level_object.render()

    return level_object


class BlockCache:
    def __init__(self):
        self.cache = {}

    @staticmethod
    def is_from_memory(block_index):
        return block_index > 0xFF

    def block(self, palette_group, pattern_table, tsa_data, block_index):
        if block_index not in self.cache:
            if self.is_from_memory(block_index):
                block = Block(ROM().get_byte(block_index), palette_group, pattern_table, tsa_data)
            else:
                block = Block(block_index, palette_group, pattern_table, tsa_data)

            self.cache[block_index] = block
        return self.cache[block_index]


@dataclass
class BlockGenerator:
    size: Size
    object_set: ObjectSet
    domain: int
    index: int
    pos: Position
    object_factory_idx: int

    @property
    def y_pos(self):
        return self.pos.y

    @y_pos.setter
    def y_pos(self, y: int):
        self.pos.y = y

    @property
    def x_pos(self):
        return self.pos.x

    @x_pos.setter
    def x_pos(self, x: int):
        self.pos.x = x

    @property
    def is_4byte(self):
        """Returns if the object takes 4 bytes"""
        return self._is_4byte(self.object_set, self.type)

    @property
    def bytes(self):
        return self.object_set.get_definition_of(self.type).bytes

    @staticmethod
    def _is_4byte(object_set, type):
        """Returns if an object is 4 bytes from the object set from a given type"""
        return object_set.get_definition_of(type).is_4byte

    @property
    def is_single_block(self):
        """Returns if a block is a single block"""
        return self._is_single_block(self.index)

    @staticmethod
    def _is_single_block(index):
        """Returns if the index is in the range for single blocks"""
        return index <= 0x0F

    @property
    def domain_offset(self):
        """Returns the offset for type of a domain"""
        return self._domain_offset(self.domain)

    @staticmethod
    def _domain_offset(domain):
        """Returns the correct offset for a type from a given domain"""
        return domain * 0x1F

    @property
    def type(self):
        """Returns the type of the block"""
        return self._type(self.index, self.domain)

    @staticmethod
    def _type(index, domain):
        """Returns the type of the block from a given index and domain
        For every domain there is 16 single-block types and 15 multi-block types
        Single-block objects exist at the beginning of every domain
        Multi-block objects exist in the remainder, being split into 16 block indexes
        """
        if BlockGenerator._is_single_block(index):
            return index + BlockGenerator._domain_offset(domain)
        else:
            return (index >> 4) + BlockGenerator._domain_offset(domain) + 15

    @classmethod
    def from_bytes(cls, object_set: ObjectSet, data: bytearray, is_vertical: bool = False, object_factory_idx=0):
        """Fabricates an object from bytes in rom"""
        domain = (data[0] & 0b1110_0000) >> 5
        y_pos = data[0] & 0b0001_1111
        x_pos = data[1]
        if is_vertical:
            y_pos += (x_pos // SCREEN_WIDTH) * SCREEN_HEIGHT
            x_pos %= SCREEN_WIDTH
        index = data[2]

        if cls._is_single_block(index):
            length, height = 1, 0
        elif cls._is_4byte(object_set, cls._type(index, domain)):
            height = index & 0b0000_1111
            try:
                length = data[3]
            except IndexError:
                length = 0
        else:
            length = index & 0b0000_1111
            height = 0
        return cls(object_set=object_set, domain=domain, index=index, pos=Position(x_pos, y_pos),
                   size=Size(length, height), object_factory_idx=object_factory_idx)


class LevelObject(ObjectLike, BlockGenerator):
    def __init__(
            self,
            object_set: ObjectSet,
            palette_group,
            pattern_table: PatternTable,
            objects_ref: List["LevelObjectController"],
            is_vertical: bool,
            domain: int,
            index: int,
            position: Position,
            size: Size,
            object_factory_idx: int
    ):
        self.object_set, self.palette_group = object_set, palette_group
        self.pattern_table, self.objects_ref, self.vertical_level = pattern_table, objects_ref, is_vertical
        self.domain, self.index, self.pos = domain, index, position
        self.size = size
        self.object_factory_idx = object_factory_idx

        self.index_in_level = len(self.objects_ref)

        self.block_cache = BlockCache()
        self.rendered_position = Position(0, 0)
        self.rendered_size = Size(0, 0)

        self.selected = False

        self.ground_level = GROUND

        self.rect = Rect()

        self._render()

    @classmethod
    def from_data(cls, data: bytearray, object_set: ObjectSet, palette_group, pattern_table: PatternTable,
                  objects_ref: List["LevelObjectController"], is_vertical: bool, object_factory_idx):
        bg = BlockGenerator.from_bytes(object_set, data, is_vertical)
        domain, index, position, size = bg.domain, bg.index, bg.pos, bg.size
        return cls(
            object_set,
            palette_group,
            pattern_table,
            objects_ref,
            is_vertical,
            domain,
            index,
            position,
            size,
            object_factory_idx
        )

    def properties(self):
        return [self.description, self.domain, self.index, self.size.width]

    @property
    def tsa_data(self):
        return ROM.get_tsa_data(self.object_set.object_set_number)

    @property
    def bmp(self):
        return self.object_set.get_definition_of(self.type).bmp

    @property
    def orientation(self):
        return self.object_set.get_definition_of(self.type).orientation

    @property
    def ending(self):
        return self.object_set.get_definition_of(self.type).ending

    @property
    def description(self):
        return self.object_set.get_definition_of(self.type).description

    @property
    def blocks(self):
        return [int(block) for block in self.object_set.get_definition_of(self.type).rom_object_design]

    def render(self):
        self._render()

    @abstractmethod
    def _render(self):
        pass

    def draw(self, painter: QPainter, block_length, transparent):
        for idx, pos in enumerate(self.rendered_size.positions()):
            if idx < len(self.rendered_blocks) and self.rendered_blocks[idx] != BLANK:
                po = pos + self.rendered_position
                self._draw_block(painter, self.rendered_blocks[idx], po, block_length, transparent)

    def _draw_block(self, painter: QPainter, block_index, position, block_length, transparent):
        self.block_cache.block(self.palette_group, self.pattern_table, self.tsa_data, block_index).draw(
            painter, position.x * block_length, position.y * block_length,
            block_length=block_length, selected=self.selected, transparent=transparent,
        )

    def set_position(self, pos: Position):
        positional_difference, self.rendered_position = self.pos - self.rendered_position, self.in_bounds(pos)
        self.pos = self.rendered_position + positional_difference
        self.render()

    def move_by(self, pos: Position):
        self.set_position(self.rendered_position + pos)

    def get_position(self):
        return self.pos.y, self.pos.y

    def expands(self):
        return EXPANDS_NOT

    def primary_expansion(self):
        return EXPANDS_BOTH

    def resize_x(self, x: int):
        if self.expands() & EXPANDS_HORIZ == 0:
            return

        if self.primary_expansion() == EXPANDS_HORIZ and self.is_4byte:
            length = x - self.pos.x
            length = max(0, length)
            length = min(length, 0xFF)
            self.size.width = length

        elif self.primary_expansion() == EXPANDS_HORIZ:
            length = x - self.pos.x

            length = max(0, length)
            length = min(length, 0x0F)

            base_index = (self.obj_index // 0x10) * 0x10

            self.obj_index = base_index + length
            self.size.width = self.obj_index
        else:
            length = x - self.pos.x
            length = max(0, length)
            length = min(length, 0xFF)

            if self.is_4byte:
                self.size.width = length
            else:
                raise ValueError("Resize impossible", self)

        self._render()

    def resize_y(self, y: int):
        if self.expands() & EXPANDS_VERT == 0:
            return

        if self.primary_expansion() == EXPANDS_VERT:
            length = y - self.pos.y

            length = max(0, length)
            length = min(length, 0x0F)

            base_index = (self.obj_index // 0x10) * 0x10

            self.obj_index = base_index + length
            self.size.width = self.obj_index
        else:
            length = y - self.pos.y
            length = max(0, length)
            length = min(length, 0xFF)

            if self.is_4byte:
                self.size.width = length
            else:
                raise ValueError("Resize impossible", self)

        self._calculate_lengths()

        self._render()

    def _calculate_lengths(self):
        if self.is_single_block:
            self._length = 1
        else:
            self._length = self.obj_index & 0b0000_1111

        if self.is_4byte:
            self.size.height = self.size.width

    def resize_by(self, dx: int, dy: int):
        if dx:
            self.resize_x(self.pos.x + dx)

        if dy:
            self.resize_y(self.pos.y + dy)

    def increment_type(self):
        self.change_type(True)

    def decrement_type(self):
        self.change_type(False)

    def change_type(self, increment: int):
        pass

    def __contains__(self, item: Tuple[int, int]) -> bool:
        x, y = item

        return self.point_in(x, y)

    def point_in(self, x: int, y: int) -> bool:
        return self.rect.contains(x, y)

    def get_status_info(self) -> List[tuple]:
        return [
            ("x", self.rendered_position.x),
            ("y", self.rendered_position.y),
            ("Width", self.rendered_size.width),
            ("Height", self.rendered_size.height),
            ("Orientation", self.orientation),
            ("Ending", ENDING_STR[self.ending]),
        ]

    def display_size(self, zoom_factor: int = 1):
        size = self.rendered_position * Block.SIDE_LENGTH * zoom_factor
        return size.to_qt()

    def as_image(self) -> QImage:
        self.rendered_position = Position(0, 0)
        size = self.rendered_size * Block.SIDE_LENGTH
        image = QImage(size.to_qt(), QImage.Format_RGB888)
        bg_color = bg_color_for_object_set(self.object_set.number, 0)
        image.fill(bg_color)
        painter = QPainter(image)
        self.draw(painter, Block.SIDE_LENGTH, True)
        return image

    def to_bytes(self) -> bytearray:
        data = bytearray()

        if self.vertical_level:
            offset = self.pos.y // SCREEN_HEIGHT
            pos = Position(self.pos.x + offset * SCREEN_WIDTH, self.pos.y % SCREEN_HEIGHT)
        else:
            pos = self.pos

        if self.orientation in [PYRAMID_TO_GROUND, PYRAMID_2]:
            pos.x = self.rendered_position.x - 1 + self.rendered_size.width // 2

        data.append((self.domain << 5) | pos.y)
        data.append(max(min(pos.x, 0xFF), 0))

        if not self.is_4byte and not self.is_single_block:
            third_byte = (self.obj_index & 0xF0) + self.size.width
        else:
            third_byte = self.obj_index

        data.append(third_byte)

        if self.is_4byte:
            data.append(self.size.width)

        return data

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.description} at {self.pos.x}, {self.pos.y}"

    def __eq__(self, other):
        try:
            return self.to_bytes() == other.to_bytes()
        except KeyError:
            return False

    def __lt__(self, other):
        return self.index_in_level < other.index_in_level

    def _confirm_render(self, size: Size, pos: Position, blocks: list):
        blocks = blocks if blocks else self.blocks
        self.rendered_size, self.rendered_position, self.rendered_blocks = size, pos, blocks
        self.rect = Rect.from_size_and_position(self.rendered_size, self.rendered_position)

    def _get_obj_index(self):
        try:
            return self.objects_ref.index(self)
        except ValueError:
            # the object has not been added yet, so stick with the one given in the constructor
            return self.object_factory_idx

    def _if_intersects(self, rect):
        return any(
            [
                rect.intersects(obj.get_rect()) for obj in self.objects_ref[:self._get_obj_index()]
            ]
        )
