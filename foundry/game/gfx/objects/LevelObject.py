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

    if not isinstance(level_object, (LevelObject, EnemyObject)):
        return None

    if isinstance(level_object, EnemyObject):
        return level_object

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
    def from_bytes(cls, object_set: ObjectSet, data: list, is_vertical: bool = False):
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
        return cls(object_set=object_set, domain=domain, index=index, pos=Position(x_pos, y_pos), size=Size(length, height))


class LevelObject(ObjectLike, BlockGenerator):
    def __init__(
            self,
            object_set: ObjectSet,
            palette_group,
            pattern_table: PatternTable,
            objects_ref: List["LevelObject"],
            is_vertical: bool,
            domain: int = 0,
            index: int = 0,
            position: Position = (0, 0),
            size: Size = (0, 0)
    ):
        self.object_set, self.palette_group = object_set, palette_group
        self.pattern_table, self.objects_ref, self.vertical_level = pattern_table, objects_ref, is_vertical
        self.domain, self.index, self.pos = domain, index, position
        self.size = size

        self.index_in_level = None

        self.block_cache = {}
        self.rendered_base_x, self.rendered_base_y = 0, 0
        self.selected = False

        self.ground_level = GROUND

        self.rect = QRect()

        self._render()

    @classmethod
    def from_data(cls, data: bytearray, object_set: ObjectSet, palette_group, pattern_table: PatternTable,
                  objects_ref: List["LevelObject"], is_vertical: bool):
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
            size
        )

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
        return self.object_set.get_definition_of(self.type).bmp_width

    @property
    def height(self):
        return self.object_set.get_definition_of(self.type).bmp_height

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

    def rend(self):
        pass

    def _render(self):
        self.rendered_base_x = base_x = self.x_position
        self.rendered_base_y = base_y = self.y_position

        self.rendered_width = new_width = self.width
        self.rendered_height = new_height = self.height

        try:
            self.index_in_level = self.objects_ref.index(self)
        except ValueError:
            # the object has not been added yet, so stick with the one given in the constructor
            pass

        blocks_to_draw = []

        if self.orientation == TO_THE_SKY:
            base_x = self.x_position
            base_y = SKY

            for _ in range(self.y_position):
                blocks_to_draw.extend(self.blocks[0: self.width])

            blocks_to_draw.extend(self.blocks[-self.width:])

        elif self.orientation == DESERT_PIPE_BOX:
            # segments are the horizontal sections, which are 8 blocks long
            # two of those are drawn per length bit
            # rows are the 4 block high rows Mario can walk in

            is_pipe_box_type_b = self.obj_index // 0x10 == 4

            rows_per_box = self.height
            lines_per_row = 4

            segment_width = self.width
            segments = (self.length + 1) * 2

            box_height = lines_per_row * rows_per_box

            new_width = segments * segment_width
            new_height = box_height

            for row_number in range(rows_per_box):
                for line in range(lines_per_row):
                    if is_pipe_box_type_b and row_number > 0 and line == 0:
                        # in pipebox type b we do not repeat the horizontal beams
                        line += 1

                    start = line * segment_width
                    stop = start + segment_width

                    for segment_number in range(segments):
                        blocks_to_draw.extend(self.blocks[start:stop])

            if is_pipe_box_type_b:
                # draw another open row
                start = segment_width
            else:
                # draw the first row again to close the box
                start = 0

            stop = start + segment_width

            for segment_number in range(segments):
                blocks_to_draw.extend(self.blocks[start:stop])

        elif self.orientation in [DIAG_DOWN_LEFT, DIAG_DOWN_RIGHT, DIAG_UP_RIGHT, DIAG_WEIRD]:
            if self.ending == UNIFORM:
                new_height = (self.length + 1) * self.height
                new_width = (self.length + 1) * self.width

                left = [BLANK]
                right = [BLANK]
                slopes = self.blocks

            elif self.ending == END_ON_TOP_OR_LEFT:
                new_height = (self.length + 1) * self.height
                new_width = (self.length + 1) * (self.width - 1)  # without fill block

                if self.orientation in [DIAG_DOWN_RIGHT, DIAG_UP_RIGHT]:
                    fill_block = self.blocks[0:1]
                    slopes = self.blocks[1:]

                    left = fill_block
                    right = [BLANK]
                elif self.orientation == DIAG_DOWN_LEFT:
                    fill_block = self.blocks[-1:]
                    slopes = self.blocks[0:-1]

                    right = fill_block
                    left = [BLANK]

                else:
                    fill_block = self.blocks[0:1]
                    slopes = self.blocks[1:]

                    right = [BLANK]
                    left = fill_block

            elif self.ending == END_ON_BOTTOM_OR_RIGHT:
                new_height = (self.length + 1) * self.height
                new_width = (self.length + 1) * (self.width - 1)  # without fill block

                fill_block = self.blocks[-1:]
                slopes = self.blocks[0:-1]

                left = [BLANK]
                right = fill_block
            else:
                # todo other two ends not used with diagonals?
                print(self.description)
                self.rendered_blocks = []
                return

            rows = []

            if self.height > self.width:
                slope_width = self.width
            else:
                slope_width = len(slopes)

            for y in range(new_height):
                amount_right = (y // self.height) * slope_width
                amount_left = new_width - slope_width - amount_right

                offset = y % self.height

                rows.append(amount_left * left + slopes[offset: offset + slope_width] + amount_right * right)

            if self.orientation in [DIAG_UP_RIGHT]:
                for row in rows:
                    row.reverse()

            if self.orientation in [DIAG_DOWN_RIGHT, DIAG_UP_RIGHT]:
                if not self.height > self.width:  # special case for 60 degree platform wire down right
                    rows.reverse()

            if self.orientation in [DIAG_UP_RIGHT]:
                base_y -= new_height - 1

            if self.orientation in [DIAG_DOWN_LEFT]:
                base_x -= new_width - slope_width

            for row in rows:
                blocks_to_draw.extend(row)

        elif self.orientation in [PYRAMID_TO_GROUND, PYRAMID_2]:
            # since pyramids grow horizontally in both directions when extending
            # we need to check for new ground every time it grows

            base_x += 1  # set the new base_x to the tip of the pyramid

            for y in range(base_y, self.ground_level):
                new_height = y - base_y
                new_width = 2 * new_height

                bottom_row = QRect(base_x, y, new_width, 1)

                if any(
                        [
                            bottom_row.intersects(obj.get_rect()) and y == obj.get_rect().top()
                            for obj in self.objects_ref[0: self.index_in_level]
                        ]
                ):
                    break

            base_x = base_x - (new_width // 2)

            blank = self.blocks[0]
            left_slope = self.blocks[1]
            left_fill = self.blocks[2]
            right_fill = self.blocks[3]
            right_slope = self.blocks[4]

            for y in range(new_height):
                blank_blocks = (new_width // 2) - (y + 1)
                middle_blocks = y  # times two

                blocks_to_draw.extend(blank_blocks * [blank])

                blocks_to_draw.append(left_slope)
                blocks_to_draw.extend(middle_blocks * [left_fill] + middle_blocks * [right_fill])
                blocks_to_draw.append(right_slope)

                blocks_to_draw.extend(blank_blocks * [blank])

        elif self.orientation == ENDING:
            page_width = 16
            page_limit = page_width - self.x_position % page_width

            new_width = page_width + page_limit + 1
            new_height = (GROUND - 1) - SKY

            for y in range(SKY, GROUND - 1):
                blocks_to_draw.append(self.blocks[0])
                blocks_to_draw.extend([self.blocks[1]] * (new_width - 1))

            rom_offset = self.object_set.get_ending_offset()

            rom = ROM()

            ending_graphic_height = 6
            floor_height = 1

            y_offset = GROUND - floor_height - ending_graphic_height

            for y in range(ending_graphic_height):
                for x in range(page_width):
                    block_index = rom.get_byte(rom_offset + y * page_width + x - 1)

                    block_position = (y_offset + y) * new_width + x + page_limit + 1
                    blocks_to_draw[block_position] = block_index

            # Mushroom/Fire flower/Star is categorized as an enemy

        elif self.orientation == VERTICAL:
            new_height = self.length + 1
            new_width = self.width

            if self.ending == UNIFORM:
                if self.is_4byte:
                    # there is one VERTICAL 4-byte object: Vertically oriented X-blocks
                    # the width is the primary expansion
                    new_width = (self.obj_index & 0x0F) + 1

                for _ in range(new_height):
                    for x in range(new_width):
                        for y in range(self.height):
                            blocks_to_draw.append(self.blocks[x % self.width])

            elif self.ending == END_ON_TOP_OR_LEFT:
                # in case the drawn object is smaller than its actual size
                for y in range(min(self.height, new_height)):
                    offset = y * self.width
                    blocks_to_draw.extend(self.blocks[offset: offset + self.width])

                additional_rows = new_height - self.height

                # assume only the last row needs to repeat
                # todo true for giant blocks?
                if additional_rows > 0:
                    last_row = self.blocks[-self.width:]

                    for _ in range(additional_rows):
                        blocks_to_draw.extend(last_row)

            elif self.ending == END_ON_BOTTOM_OR_RIGHT:
                additional_rows = new_height - self.height

                # assume only the first row needs to repeat
                # todo true for giant blocks?
                if additional_rows > 0:
                    last_row = self.blocks[0: self.width]

                    for _ in range(additional_rows):
                        blocks_to_draw.extend(last_row)

                # in case the drawn object is smaller than its actual size
                for y in range(min(self.height, new_height)):
                    offset = y * self.width
                    blocks_to_draw.extend(self.blocks[offset: offset + self.width])

            elif self.ending == TWO_ENDS:
                # object exists on ships
                top_row = self.blocks[0: self.width]
                bottom_row = self.blocks[-self.width:]

                blocks_to_draw.extend(top_row)

                additional_rows = new_height - 2

                # repeat second to last row
                if additional_rows > 0:
                    for _ in range(additional_rows):
                        blocks_to_draw.extend(self.blocks[-2 * self.width: -self.width])

                if new_height > 1:
                    blocks_to_draw.extend(bottom_row)

        elif self.orientation in [HORIZONTAL, HORIZ_TO_GROUND, HORIZONTAL_2]:
            new_width = self.length + 1

            if self.orientation == HORIZ_TO_GROUND:
                # to the ground only, until it hits something
                for y in range(base_y, self.ground_level):
                    bottom_row = QRect(base_x, y, new_width, 1)

                    if any(
                            [
                                bottom_row.intersects(obj.get_rect()) and y == obj.get_rect().top()
                                for obj in self.objects_ref[0: self.index_in_level]
                            ]
                    ):
                        new_height = y - base_y
                        break
                else:
                    # nothing underneath this object, extend to the ground
                    new_height = self.ground_level - base_y

                if self.is_single_block:
                    new_width = self.length

            elif self.orientation == HORIZONTAL_2 and self.ending == TWO_ENDS:
                # floating platforms seem to just be one shorter for some reason
                new_width -= 1
            else:
                new_height = self.height + self.secondary_length

            if self.ending == UNIFORM and not self.is_4byte:
                for y in range(new_height):
                    offset = (y % self.height) * self.width

                    for _ in range(0, new_width):
                        blocks_to_draw.extend(self.blocks[offset: offset + self.width])

                # in case of giant blocks
                new_width *= self.width

            elif self.ending == UNIFORM and self.is_4byte:
                # 4 byte objects
                top = self.blocks[0:1]
                bottom = self.blocks[-1:]

                new_height = self.height + self.secondary_length

                # ceilings are one shorter than normal
                if self.height > self.width:
                    new_height -= 1

                blocks_to_draw.extend(new_width * top)

                for _ in range(1, new_height):
                    blocks_to_draw.extend(new_width * bottom)

            elif self.ending == END_ON_TOP_OR_LEFT:
                for y in range(new_height):
                    offset = y * self.width

                    blocks_to_draw.append(self.blocks[offset])

                    for x in range(1, new_width):
                        blocks_to_draw.append(self.blocks[offset + 1])

            elif self.ending == END_ON_BOTTOM_OR_RIGHT:
                for y in range(new_height):
                    offset = y * self.width

                    for x in range(new_width - 1):
                        blocks_to_draw.append(self.blocks[offset])

                    blocks_to_draw.append(self.blocks[offset + self.width - 1])

            elif self.ending == TWO_ENDS:
                top_and_bottom_line = 2

                for y in range(self.height):
                    offset = y * self.width
                    left, *middle, right = self.blocks[offset: offset + self.width]

                    blocks_to_draw.append(left)
                    blocks_to_draw.extend(middle * (new_width - top_and_bottom_line))
                    blocks_to_draw.append(right)

                if not len(blocks_to_draw) % self.height == 0:
                    print(f"Blocks to draw are not divisible by height. {self}")

                new_width = int(len(blocks_to_draw) / self.height)

                top_row = blocks_to_draw[0:new_width]
                bottom_row = blocks_to_draw[-new_width:]

                middle_blocks = blocks_to_draw[new_width:-new_width]

                new_rows = new_height - top_and_bottom_line

                if new_rows >= 0:
                    blocks_to_draw = top_row + middle_blocks * new_rows + bottom_row
        else:
            if not self.orientation == SINGLE_BLOCK_OBJECT:
                print(f"Didn't render {self.description}")
                # breakpoint()

        # for not yet implemented objects and single block objects
        if blocks_to_draw:
            self.rendered_blocks = blocks_to_draw
        else:
            self.rendered_blocks = self.blocks

        self.rendered_width = new_width
        self.rendered_height = new_height
        self.rendered_base_x = base_x
        self.rendered_base_y = base_y

        if new_width and not self.rendered_height == len(self.rendered_blocks) / new_width:
            print(
                f"Not enough Blocks for calculated height: {self.description}. "
                f"Blocks for height: {len(self.rendered_blocks) / new_width}. Rendered height: {self.rendered_height}"
            )

            self.rendered_height = len(self.rendered_blocks) / new_width
        elif new_width == 0:
            print(
                f"Calculated Width is 0, setting to 1: {self.description}. "
                f"Blocks to draw: {len(self.rendered_blocks)}. Rendered height: {self.rendered_height}"
            )

            self.rendered_width = 1

        self.rect = QRect(self.rendered_base_x, self.rendered_base_y, self.rendered_width, self.rendered_height)

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

        if self.primary_expansion() == EXPANDS_HORIZ:
            length = x - self.x_position

            length = max(0, length)
            length = min(length, 0x0F)

            base_index = (self.obj_index // 0x10) * 0x10

            self.obj_index = base_index + length
            self.data[2] = self.obj_index
        else:
            length = x - self.x_position
            length = max(0, length)
            length = min(length, 0xFF)

            if self.is_4byte:
                self.data[3] = length
            else:
                raise ValueError("Resize impossible", self)

        self._calculate_lengths()

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
            self.data[2] = self.obj_index
        else:
            length = y - self.y_position
            length = max(0, length)
            length = min(length, 0xFF)

            if self.is_4byte:
                self.data[3] = length
            else:
                raise ValueError("Resize impossible", self)

        self._calculate_lengths()

        self._render()

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
        if not isinstance(other, LevelObject):
            return False
        else:
            return self.to_bytes() == other.to_bytes()

    def __lt__(self, other):
        return self.index_in_level < other.index_in_level
