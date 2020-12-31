from typing import List, Optional, Tuple, Union
from warnings import warn
from abc import abstractmethod
from typing import List, Tuple, Optional
from dataclasses import dataclass

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
from smb3parse.objects.object_set import PLAINS_OBJECT_SET

from foundry.core.geometry.Size.Size import Size
from PySide2.QtCore import QSize
from foundry.core.geometry.Position.Position import Position
from foundry.game.Rect import Rect
from smb3parse.asm6_converter import to_hex


SKY = 0
GROUND = 27

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

    level_object.icon()

    return level_object


@dataclass
class BlockGenerator:
    size: Size
    object_set: Tileset
    domain: int
    index: int
    overflow: list
    pos: Position
    object_factory_idx: int
    bytes: int

    @property
    def y_pos(self) -> int:
        return self.pos.y

    @y_pos.setter
    def y_pos(self, y: int) -> None:
        self.pos.y = y

    @property
    def x_pos(self) -> int:
        return self.pos.x

    @x_pos.setter
    def x_pos(self, x: int) -> None:
        self.pos.x = x

    @property
    def is_4byte(self) -> bool:
        """Returns if the object takes 4 bytes"""
        return self.bytes == 4

    @staticmethod
    def _bytes(object_set: Tileset, type: int) -> int:
        """Returns if an object is 4 bytes from the object set from a given type"""
        return object_set.get_definition_of(type).bytes

    @property
    def is_single_block(self) -> bool:
        """Returns if a block is a single block"""
        return self._is_single_block(self.index)

    @staticmethod
    def _is_single_block(index: int) -> bool:
        """Returns if the index is in the range for single blocks"""
        return index <= 0x0F

    @property
    def domain_offset(self) -> int:
        """Returns the offset for type of a domain"""
        return self._domain_offset(self.domain)

    @staticmethod
    def _domain_offset(domain: int) -> int:
        """Returns the correct offset for a type from a given domain"""
        return domain * 0x1F

    @property
    def type(self) -> int:
        """Returns the type of the block"""
        return self._type(self.index, self.domain)

    @staticmethod
    def _type(index: int, domain: int) -> int:
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
    def from_bytes(
            cls,
            object_set: Tileset,
            data: bytearray,
            is_vertical: bool = False,
            object_factory_idx: int = 0) -> "BlockGenerator":
        """Fabricates an object from bytes in rom"""
        domain = (data[0] & 0b1110_0000) >> 5
        y_pos = data[0] & 0b0001_1111
        x_pos = data[1]
        if is_vertical:
            y_pos += (x_pos // SCREEN_WIDTH) * SCREEN_HEIGHT
            x_pos %= SCREEN_WIDTH
        index = data[2]

        bytes = cls._bytes(object_set, cls._type(index, domain))
        if cls._is_single_block(index):
            length, height = 1, 0
        elif bytes >= 4:
            height = index & 0b0000_1111
            try:
                length = data[3]
            except IndexError:
                length = 0
        else:
            length = index & 0b0000_1111
            height = 0

        if bytes > 4:
            overflow = data[4:] if len(data) > 3 else [0 for _ in range(bytes - 4)]
            if len(overflow) == 0:
                overflow = [0]
        else:
            overflow = []

        return cls(object_set=object_set, domain=domain, index=index, overflow=overflow, pos=Position(x_pos, y_pos),
                   size=Size(length, height), object_factory_idx=object_factory_idx, bytes=bytes)


class LevelObject(ObjectLike, BlockGenerator):
    def __init__(
            self,
            object_set: Tileset,
            palette_group: List[List[int]],
            pattern_table: PatternTableHandler,
            objects_ref: List["LevelObjectController"],
            is_vertical: bool,
            domain: int,
            index: int,
            overflow: list,
            position: Position,
            size: Size,
            object_factory_idx: int,
            render: bool = True
    ):
        self.object_set, self.palette_group = object_set, palette_group
        self.pattern_table, self.objects_ref, self.vertical_level = pattern_table, objects_ref, is_vertical
        self.domain, self.index, self.pos = domain, index, position
        self.size, self.overflow = size, overflow
        self.object_factory_idx = object_factory_idx
        self.bytes = self._bytes(self.object_set, self.type)
        self.does_render = render

        self.index_in_level: int = len(self.objects_ref)

        self.rendered_position: Position = Position(0, 0)
        self.rendered_size: Size = Size(0, 0)
        self.rendered_positions: List[Tuple[Position, int]] = []
        self.last_rect: Optional[Rect] = None

        self.selected: bool = False

        self.ground_level: int = GROUND

        self.rect: Rect = Rect()

        self.render()

    @classmethod
    def from_data(
            cls,
            data: bytearray,
            object_set: Tileset,
            palette_group: List[List[int]],
            pattern_table: PatternTableHandler,
            objects_ref: List["LevelObjectController"],
            is_vertical: bool,
            object_factory_idx: int,
            render: bool):
        bg = BlockGenerator.from_bytes(object_set, data, is_vertical)
        domain, index, position, size = bg.domain, bg.index, bg.pos, bg.size
        return cls(
            object_set=object_set,
            palette_group=palette_group,
            pattern_table=pattern_table,
            objects_ref=objects_ref,
            is_vertical=is_vertical,
            domain=domain,
            index=index,
            overflow=[],
            position=position,
            size=size,
            object_factory_idx=object_factory_idx,
            render=render
        )

    def properties(self) -> Tuple[str, int, int, int]:
        return self.description, self.domain, self.index, self.size.width

    @property
    def tsa_data(self) -> bytearray:
        return ROM().get_tsa_data(self.object_set.index)

    @property
    def bmp(self) -> BitMapPicture:
        return self.object_set.get_definition_of(self.type).bmp

    @property
    def orientation(self) -> int:
        return self.object_set.get_definition_of(self.type).orientation

    @property
    def ending(self) -> int:
        return self.object_set.get_definition_of(self.type).ending

    @property
    def description(self) -> str:
        return self.object_set.get_definition_of(self.type).description

    @property
    def blocks(self) -> List[int]:
        bcks = []
        for idx, block in enumerate(
                [int(block) for block in self.object_set.get_definition_of(self.type).rom_object_design]
        ):
            if block <= 0xFF:
                bcks.append(block)
            else:
                bcks.append(ROM().get_byte(block))
        return bcks

    def render(self) -> None:
        if self.does_render:
            self._render()

    @abstractmethod
    def _render(self) -> None:
        pass

    def icon(self) -> None:
        self.size = Size(1, 1)
        self.render()

    def backtrace_update(self) -> None:
        """By default blocks do not need to update when blocks above them move"""

    def get_blocks_and_positions(self) -> List[Tuple[Position, int]]:
        return self.rendered_positions

    def draw(self, painter: QPainter, block_length: int, transparent: bool) -> None:
        for idx, pos in enumerate(self.rendered_size.positions()):
            if idx < len(self.rendered_blocks) and self.rendered_blocks[idx] != BLANK:
                po = pos + self.rendered_position
                self._draw_block(painter, self.rendered_blocks[idx], po, block_length, transparent)


    def _draw_block(
            self, painter: QPainter, block_index: int, position: Position, block_length: int, transparent: bool
        ) -> None:
        Block.from_rom(block_index, self.palette_group, self.pattern_table, self.tsa_data).draw(
            painter, pos=Position(position.x * block_length, position.y * block_length),
            size=Size(block_length, block_length), transparent=transparent,
        )

    def set_position(self, pos: Position) -> None:
        self.pos = pos
        self.pos.x = max(self.pos.x, 0)
        self.pos.y = min(max(self.pos.y, 0), 26)
        self.render()

    def move_by(self, pos: Position) -> None:
        self.set_position(pos + self.pos)

    def get_position(self) -> Tuple[int, int]:
        return self.pos.x, self.pos.y

    @property
    @abstractmethod
    def expands(self) -> int:
        """Determines how the object expands"""

    @property
    @abstractmethod
    def primary_expansion(self) -> int:
        """Determines what the primary expansion is"""

    def resize_x(self, x: int) -> None:
        if not x or self.expands & EXPANDS_HORIZ == 0:
            return

        if self.primary_expansion == EXPANDS_HORIZ and self.is_4byte:
            length = x
            length = max(0, length)
            length = min(length, 0xFF)
            self.size.width = length

        elif self.primary_expansion == EXPANDS_HORIZ:

            length = x
            length = max(0, length)
            length = min(length, 0x0F)

            self.index = (self.index & 0xF0) + length
            self.size.width = length

        else:
            length = x
            length = max(0, length)
            length = min(length, 0xFF)

            if self.is_4byte:
                self.size.width = length
            else:
                raise ValueError("Resize impossible", self)

        self.render()

    def resize_y(self, y: int) -> None:
        if self.expands & EXPANDS_VERT == 0:
            return

        if self.primary_expansion == EXPANDS_VERT:
            length = y - self.pos.y

            length = max(0, length)
            length = min(length, 0x0F)

            index = (self.index // 0x10) * 0x10

            self.index = index + length
            self.size.width = self.index
        else:
            length = y - self.pos.y
            length = max(0, length)
            length = min(length, 0xFF)

            if self.is_4byte:
                self.size.width = length
            else:
                raise ValueError("Resize impossible", self)

        self._calculate_lengths()

        self.render()

    def _calculate_lengths(self) -> None:
        if self.is_single_block:
            self._length = 1
        else:
            self._length = self.index & 0b0000_1111

        if self.is_4byte:
            self.size.height = self.size.width

    def resize_by(self, dx: int, dy: int) -> None:

        if dx:
            self.resize_x(dx)

        if dy:
            self.resize_y(self.pos.y + dy)


    def increment_type(self) -> None:
        self.change_type(True)

    def decrement_type(self) -> None:
        self.change_type(False)

    def change_type(self, increment: int) -> None:
        """"""

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
            ("Orientation", self.orientation)
        ]

    def display_size(self, zoom_factor: int = 1) -> QSize:
        size = self.rendered_position * Block.image_length * zoom_factor
        return size.to_qt()

    def as_image(self) -> QImage:
        self.rendered_position = Position(0, 0)
        size = self.rendered_size * Block.image_length
        image = QImage(size.to_qt(), QImage.Format_RGB888)
        bg_color = bg_color_for_object_set(self.object_set.number, 0)
        image.fill(bg_color)
        painter = QPainter(image)
        self.draw(painter, Block.image_length, True)
        return image

    def vertical_offset_pos(self, pos: Position) -> Position:
        if self.vertical_level:
            offset = pos.y // SCREEN_HEIGHT
            return Position(pos.x + offset * SCREEN_WIDTH, pos.y % SCREEN_HEIGHT)
        else:
            return pos

    def to_asm6(self) -> str:
        pos = self.vertical_offset_pos(self.pos)
        if self.is_4byte:
            fourth_byte = f", {to_hex(self.size.width)}"
        else:
            fourth_byte = ""
        s = f"\t.byte {to_hex(self.domain << 5)} | {to_hex(pos.y)}, {to_hex(max(min(pos.x, 0xFF), 0))}, " \
            f"{to_hex(self.index)}{fourth_byte}; {self.description}\n"
        return s

    def to_bytes(self) -> bytearray:
        data = bytearray()

        pos = self.vertical_offset_pos(self.pos)

        data.append((self.domain << 5) | pos.y)
        data.append(max(min(pos.x, 0xFF), 0))
        data.append(self.index)

        if self.is_4byte:
            data.append(self.size.width)

        return data

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.description} at {self.pos.x}, {self.pos.y}"

    def __eq__(self, other: "LevelObject") -> bool:
        try:
            return self.to_bytes() == other.to_bytes()
        except KeyError:
            return False

    def __lt__(self, other: "LevelObject") -> bool:
        return self.index_in_level < other.index_in_level

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

        return background_routine_by_objectset[self.object_set.index]()

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
