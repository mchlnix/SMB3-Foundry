from abc import abstractmethod
from typing import List, Optional, Tuple, Union
from dataclasses import dataclass

from PySide2.QtCore import QRect, QSize
from PySide2.QtGui import QImage, QPainter

from foundry.game.File import ROM
from foundry.game.ObjectDefinitions import (
    DESERT_PIPE_BOX,
    DIAG_DOWN_LEFT,
    DIAG_DOWN_RIGHT,
    DIAG_UP_RIGHT,
    DIAG_WEIRD,
    ENDING,
    END_ON_BOTTOM_OR_RIGHT,
    END_ON_TOP_OR_LEFT,
    HORIZONTAL,
    HORIZONTAL_2,
    HORIZ_TO_GROUND,
    PYRAMID_2,
    PYRAMID_TO_GROUND,
    SINGLE_BLOCK_OBJECT,
    TO_THE_SKY,
    TWO_ENDS,
    UNIFORM,
    VERTICAL,
)
from foundry.game.ObjectSet import ObjectSet
from foundry.game.gfx.objects.Jump import Jump
from foundry.game.gfx.Palette import bg_color_for_object_set
from foundry.game.gfx.PatternTable import PatternTable
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects.EnemyItem import EnemyObject
from foundry.game.gfx.objects.ObjectLike import EXPANDS_BOTH, EXPANDS_HORIZ, EXPANDS_NOT, EXPANDS_VERT, ObjectLike

from foundry.game.Size import Size
from foundry.game.Position import Position

SKY = 0
GROUND = 27

ENDING_STR = {0: "Uniform", 1: "Top or Left", 2: "Bottom or Right", 3: "Top & Bottom/Left & Right"}

ORIENTATION_TO_STR = {
    0: "Horizontal",
    1: "Vertical",
    2: "Diagonal Left-Down",
    3: "Desert Pipe Box",
    4: "Diagonal Right-Down",
    5: "Diagonal Right-Up",
    6: "Horizontal to the Ground",
    7: "Horizontal Alternative",
    8: "Diagonal Weird",  # up left?
    9: "Single Block",
    10: "Centered",
    11: "Pyramid to Ground",
    12: "Pyramid Alternative",
    13: "To the Sky",
    14: "Ending",
}

# not all objects provide a block index for blank block
BLANK = -1

SCREEN_HEIGHT = 15
SCREEN_WIDTH = 16


def get_minimal_icon_object(
        level_object: Union["LevelObject", EnemyObject]
) -> Optional[Union["LevelObject", EnemyObject]]:
    """
    Returns the object with a length, so that every block is rendered. E. g. clouds with length 0, don't have a face.
    """
    if isinstance(level_object, EnemyObject):
        return level_object
    if isinstance(level_object, Jump):
        return None
    while (
            any(block not in level_object.rendered_blocks for block in
                level_object.blocks) and level_object.length < 0x10
    ):
        level_object.length += 1

        if level_object.is_4byte:
            level_object.secondary_length += 1

        level_object.render()

    return level_object




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
    def height_len(self):
        return self.size.height

    @height_len.setter
    def height_len(self, value):
        self.size.height = value

    @property
    def length(self):
        return self.size.width

    @length.setter
    def length(self, value):
        if not self.is_4byte and not self.is_single_block:
            self.index &= 0xF0
            self.index |= value & 0x0F
        self.size.width = value

    @property
    def is_4byte(self):
        """Returns if the object takes 4 bytes"""
        return self._is_4byte(self.object_set, self.type)

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

        self.block_cache = {}
        self.rendered_position = Position(0, 0)
        self.rendered_size = Size(0, 0)

        self.selected = False

        self.ground_level = GROUND

        self.rect = QRect()

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
        return [self.description, self.domain, self.index, self.length]

    @property
    def rendered_width(self):
        return self.rendered_size.width

    @rendered_width.setter
    def rendered_width(self, width):
        self.rendered_size.width = width

    @property
    def rendered_height(self):
        return self.rendered_size.height

    @rendered_height.setter
    def rendered_height(self, height):
        self.rendered_size.height = height

    @property
    def rendered_base_x(self):
        return self.rendered_position.x

    @rendered_base_x.setter
    def rendered_base_x(self, pos):
        self.rendered_position.x = pos

    @property
    def rendered_base_y(self):
        return self.rendered_position.y

    @rendered_base_y.setter
    def rendered_base_y(self, pos):
        self.rendered_position.y = pos

    @property
    def secondary_length(self):
        return self.height_len

    @secondary_length.setter
    def secondary_length(self, len):
        self.height_len = len

    @property
    def x_position(self):
        return self.x_pos

    @x_position.setter
    def x_position(self, pos):
        self.x_pos = pos

    @property
    def y_position(self):
        return self.y_pos

    @y_position.setter
    def y_position(self, pos):
        self.y_pos = pos

    @property
    def tsa_data(self):
        return ROM.get_tsa_data(self.object_set.object_set_number)

    @property
    def width(self):
        return self.bmp.size.width

    @property
    def height(self):
        return self.bmp.size.height

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
        object_data = self.object_set.get_definition_of(self.type).rom_object_design
        return [int(block) for block in object_data]

    def render(self):
        self._render()

    @abstractmethod
    def _render(self):
        pass

    def draw(self, painter: QPainter, block_length, transparent):
        for index, block_index in enumerate(self.rendered_blocks):
            if block_index == BLANK:
                continue

            x = self.rendered_base_x + index % self.rendered_width
            y = self.rendered_base_y + index // self.rendered_width

            self._draw_block(painter, block_index, x, y, block_length, transparent)

    def _draw_block(self, painter: QPainter, block_index, x, y, block_length, transparent):
        if block_index not in self.block_cache:
            if block_index > 0xFF:
                rom_block_index = ROM().get_byte(block_index)  # block_index is an offset into the graphic memory
                block = Block(rom_block_index, self.palette_group, self.pattern_table, self.tsa_data)
            else:
                block = Block(block_index, self.palette_group, self.pattern_table, self.tsa_data)

            self.block_cache[block_index] = block

        self.block_cache[block_index].draw(
            painter,
            x * block_length,
            y * block_length,
            block_length=block_length,
            selected=self.selected,
            transparent=transparent,
        )

    def set_position(self, x, y):
        # todo also check for the upper bounds
        x = max(0, x)
        y = max(0, y)

        x_diff = self.x_position - self.rendered_base_x
        y_diff = self.y_position - self.rendered_base_y

        self.rendered_base_x = int(x)
        self.rendered_base_y = int(y)

        self.x_position = self.rendered_base_x + x_diff
        self.y_position = self.rendered_base_y + y_diff

        self._render()

    def move_by(self, dx: int, dy: int):
        new_x = self.rendered_base_x + dx
        new_y = self.rendered_base_y + dy

        self.set_position(new_x, new_y)

    def get_position(self):
        return self.x_position, self.y_position

    def expands(self):
        expands = EXPANDS_NOT

        if self.is_single_block:
            return expands

        if self.is_4byte:
            expands |= EXPANDS_BOTH

        elif self.orientation in [HORIZONTAL, HORIZONTAL_2, HORIZ_TO_GROUND] or self.orientation in [
            DIAG_DOWN_LEFT,
            DIAG_DOWN_RIGHT,
            DIAG_UP_RIGHT,
            DIAG_WEIRD,
        ]:
            expands |= EXPANDS_HORIZ

        elif self.orientation in [VERTICAL, DIAG_WEIRD]:
            expands |= EXPANDS_VERT

        return expands

    def primary_expansion(self):
        if self.orientation in [HORIZONTAL, HORIZONTAL_2, HORIZ_TO_GROUND] or self.orientation in [
            DIAG_DOWN_LEFT,
            DIAG_DOWN_RIGHT,
            DIAG_UP_RIGHT,
            DIAG_WEIRD,
        ]:
            if self.is_4byte:
                return EXPANDS_VERT
            else:
                return EXPANDS_HORIZ
        elif self.orientation in [VERTICAL]:
            if self.is_4byte:
                return EXPANDS_HORIZ
            else:
                return EXPANDS_VERT
        else:
            return EXPANDS_BOTH

    def resize_x(self, x: int):
        if self.expands() & EXPANDS_HORIZ == 0:
            return

        if self.primary_expansion() == EXPANDS_HORIZ and self.is_4byte:
            length = x - self.x_position
            length = max(0, length)
            length = min(length, 0xFF)
            self.length = length

        elif self.primary_expansion() == EXPANDS_HORIZ:
            length = x - self.x_position

            length = max(0, length)
            length = min(length, 0x0F)

            base_index = (self.obj_index // 0x10) * 0x10

            self.obj_index = base_index + length
            self.length = self.obj_index
        else:
            length = x - self.x_position
            length = max(0, length)
            length = min(length, 0xFF)

            if self.is_4byte:
                self.length = length
            else:
                raise ValueError("Resize impossible", self)

        self._render()

    def resize_y(self, y: int):
        if self.expands() & EXPANDS_VERT == 0:
            return

        if self.primary_expansion() == EXPANDS_VERT:
            length = y - self.y_position

            length = max(0, length)
            length = min(length, 0x0F)

            base_index = (self.obj_index // 0x10) * 0x10

            self.obj_index = base_index + length
            self.height_len = self.obj_index
        else:
            length = y - self.y_position
            length = max(0, length)
            length = min(length, 0xFF)

            if self.is_4byte:
                pass #self.data[3] = length
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
            self.secondary_length = self.length

    def resize_by(self, dx: int, dy: int):
        if dx:
            self.resize_x(self.x_position + dx)

        if dy:
            self.resize_y(self.y_position + dy)

    def increment_type(self):
        self.change_type(True)

    def decrement_type(self):
        self.change_type(False)

    def change_type(self, increment: int):
        if self.obj_index < 0x10 or self.obj_index == 0x10 and not increment:
            value = 1
        else:
            self.obj_index = self.obj_index // 0x10 * 0x10
            value = 0x10

        if not increment:
            value *= -1

        new_type = self.obj_index + value

        if new_type < 0 and self.domain > 0:
            new_domain = self.domain - 1
            new_type = 0xF0
        elif new_type > 0xFF and self.domain < 7:
            new_domain = self.domain + 1
            new_type = 0x00
        else:
            new_type = min(0xFF, new_type)
            new_type = max(0, new_type)

            new_domain = self.domain

        self.data[0] &= 0b0001_1111
        self.data[0] |= new_domain << 5

        self.data[2] = new_type

        self._setup()

    def __contains__(self, item: Tuple[int, int]) -> bool:
        x, y = item

        return self.point_in(x, y)

    def point_in(self, x: int, y: int) -> bool:
        return self.rect.contains(x, y)

    def get_status_info(self) -> List[tuple]:
        return [
            ("x", self.rendered_base_x),
            ("y", self.rendered_base_y),
            ("Width", self.rendered_width),
            ("Height", self.rendered_height),
            ("Orientation", ORIENTATION_TO_STR[self.orientation]),
            ("Ending", ENDING_STR[self.ending]),
        ]

    def display_size(self, zoom_factor: int = 1):
        return QSize(self.rendered_width * Block.SIDE_LENGTH, self.rendered_height * Block.SIDE_LENGTH) * zoom_factor

    def as_image(self) -> QImage:
        self.rendered_base_x = 0
        self.rendered_base_y = 0

        image = QImage(
            QSize(self.rendered_width * Block.SIDE_LENGTH, self.rendered_height * Block.SIDE_LENGTH),
            QImage.Format_RGB888,
        )

        bg_color = bg_color_for_object_set(self.object_set.number, 0)

        image.fill(bg_color)

        painter = QPainter(image)

        self.draw(painter, Block.SIDE_LENGTH, True)

        return image

    def to_bytes(self) -> bytearray:
        data = bytearray()

        if self.vertical_level:
            # todo from vertical to non-vertical is bugged, because it
            # seems like you can't convert the coordinates 1:1
            # there seems to be ambiguity

            offset = self.y_position // SCREEN_HEIGHT

            x_position = self.x_position + offset * SCREEN_WIDTH
            y_position = self.y_position % SCREEN_HEIGHT
        else:
            x_position = self.x_position
            y_position = self.y_position

        if self.orientation in [PYRAMID_TO_GROUND, PYRAMID_2]:
            x_position = self.rendered_base_x - 1 + self.rendered_width // 2

        data.append((self.domain << 5) | y_position)
        data.append(x_position)

        if not self.is_4byte and not self.is_single_block:
            third_byte = (self.obj_index & 0xF0) + self.length
        else:
            third_byte = self.obj_index

        data.append(third_byte)

        if self.is_4byte:
            data.append(self.length)

        return data

    def __repr__(self) -> str:
        return f"LevelObject {self.description} at {self.x_position}, {self.y_position}"

    def __eq__(self, other):
        try:
            return self.to_bytes() == other.to_bytes()
        except KeyError:
            return False

    def __lt__(self, other):
        return self.index_in_level < other.index_in_level

    def _confirm_render(self, size: Size, pos: Position, blocks: list):
        # for not yet implemented objects and single block objects
        if blocks:
            self.rendered_blocks = blocks
        else:
            self.rendered_blocks = self.blocks

        self.rendered_size = size
        self.rendered_position = pos
        self.rendered_blocks = blocks

        self.rect = QRect(self.rendered_base_x, self.rendered_base_y, self.rendered_width, self.rendered_height)

    def _get_obj_index(self):
        try:
            return self.objects_ref.index(self)
        except ValueError:
            # the object has not been added yet, so stick with the one given in the constructor
            return self.object_factory_idx

    def _if_intersects(self, rect):
        print(self._get_obj_index())
        return any(
            [
                rect.intersects(obj.get_rect()) for obj in self.objects_ref[0: self._get_obj_index()]
            ]
        )
