from typing import List, Optional, Tuple, Union
from warnings import warn

from PySide2.QtCore import QRect, QSize
from PySide2.QtGui import QImage, QPainter

from foundry.game.File import ROM
from foundry.game.ObjectDefinitions import EndType, GeneratorType
from foundry.game.ObjectSet import ObjectSet
from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx.Palette import PaletteGroup, bg_color_for_object_set
from foundry.game.gfx.drawable.Block import Block, get_block
from foundry.game.gfx.objects.EnemyItem import EnemyObject
from foundry.game.gfx.objects.ObjectLike import EXPANDS_BOTH, EXPANDS_HORIZ, EXPANDS_NOT, EXPANDS_VERT, ObjectLike
from smb3parse.objects.object_set import PLAINS_OBJECT_SET

SKY = 0
GROUND = 27

ENDING_STR = {
    EndType.UNIFORM: "Uniform",
    EndType.END_ON_TOP_OR_LEFT: "Top or Left",
    EndType.END_ON_BOTTOM_OR_RIGHT: "Bottom or Right",
    EndType.TWO_ENDS: "Top & Bottom/Left & Right",
}

ORIENTATION_TO_STR = {
    GeneratorType.HORIZONTAL: "Horizontal",
    GeneratorType.VERTICAL: "Vertical",
    GeneratorType.DIAG_DOWN_LEFT: "Diagonal ↙",
    GeneratorType.DESERT_PIPE_BOX: "Desert Pipe Box",
    GeneratorType.DIAG_DOWN_RIGHT: "Diagonal ↘",
    GeneratorType.DIAG_UP_RIGHT: "Diagonal ↗",
    GeneratorType.HORIZ_TO_GROUND: "Horizontal to the Ground",
    GeneratorType.HORIZONTAL_2: "Horizontal Alternative",
    GeneratorType.DIAG_WEIRD: "Diagonal Weird",  # up left?
    GeneratorType.SINGLE_BLOCK_OBJECT: "Single Block",
    GeneratorType.CENTERED: "Centered",
    GeneratorType.PYRAMID_TO_GROUND: "Pyramid to Ground",
    GeneratorType.PYRAMID_2: "Pyramid Alternative",
    GeneratorType.TO_THE_SKY: "To the Sky",
    GeneratorType.ENDING: "Ending",
}

# todo what is this, exactly?
ENDING_OBJECT_OFFSET = 0x1C8F9

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

    level_object.ground_level = 3

    while (
        any(block not in level_object.rendered_blocks for block in level_object.blocks) and level_object.length < 0x10
    ):
        level_object.length += 1

        if level_object.is_4byte:
            level_object.secondary_length += 1

        level_object.render()

    return level_object


class LevelObject(ObjectLike):
    def __init__(
        self,
        data: bytearray,
        object_set: int,
        palette_group: PaletteGroup,
        graphics_set: GraphicsSet,
        objects_ref: List["LevelObject"],
        is_vertical: bool,
        index: int,
        size_minimal: bool = False,
    ):
        self.object_set = ObjectSet(object_set)

        self.graphics_set = graphics_set
        self.tsa_data = ROM.get_tsa_data(object_set)

        self.x_position = 0
        self.y_position = 0

        self.rendered_base_x = 0
        self.rendered_base_y = 0

        self.palette_group = palette_group

        self.index_in_level = index
        self.objects_ref = objects_ref
        self.vertical_level = is_vertical

        self.data = data

        self.selected = False

        self.size_minimal = size_minimal

        if self.size_minimal:
            self.ground_level = 0
        else:
            self.ground_level = GROUND

        self._length = 0
        self.secondary_length = 0

        self._setup()

    def _setup(self):
        data = self.data

        # where to look for the graphic data?
        self.domain = (data[0] & 0b1110_0000) >> 5

        # position relative to the start of the level (top)
        self.original_y = data[0] & 0b0001_1111
        self.y_position = self.original_y

        # position relative to the start of the level (left)
        self.original_x = data[1]
        self.x_position = self.original_x

        if self.vertical_level:
            offset = (self.x_position // SCREEN_WIDTH) * SCREEN_HEIGHT

            self.y_position += offset
            self.x_position %= SCREEN_WIDTH

        # describes what object it is
        self._obj_index = 0x00

        self.obj_index = data[2]

        object_data = self.object_set.get_definition_of(self.type)

        self.width = object_data.bmp_width
        self.height = object_data.bmp_height
        self.orientation = GeneratorType(object_data.orientation)
        self.ending = EndType(object_data.ending)
        self.name = object_data.description

        self.blocks = [int(block) for block in object_data.rom_object_design]

        self.block_cache = {}

        self.is_4byte = object_data.is_4byte

        if self.is_4byte and len(self.data) == 3:
            self.data.append(0)
        elif not self.is_4byte and len(data) == 4:
            del self.data[3]

        self._length = 0
        self.secondary_length = 0

        self._calculate_lengths()

        self.rect = QRect()

        self._render()

    @property
    def obj_index(self):
        return self._obj_index

    @obj_index.setter
    def obj_index(self, value):
        self._obj_index = value

        self.is_single_block = self.obj_index <= 0x0F

        domain_offset = self.domain * 0x1F

        if self.is_single_block:
            self.type = self.obj_index + domain_offset
        else:
            self.type = (self.obj_index >> 4) + domain_offset + 16 - 1

    @property
    def object_info(self):
        return self.object_set.number, self.domain, self.obj_index

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, value):
        if not self.is_4byte and not self.is_single_block:
            self._obj_index &= 0xF0
            self._obj_index |= value & 0x0F

        self._length = value

    def _calculate_lengths(self):
        if self.is_single_block:
            self._length = 1
        else:
            self._length = self.obj_index & 0b0000_1111

        if self.is_4byte:
            self.secondary_length = self.length
            self.length = self.data[3]

    def render(self):
        self._render()

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

        if self.orientation == GeneratorType.TO_THE_SKY:
            base_x = self.x_position
            base_y = SKY

            for _ in range(self.y_position):
                blocks_to_draw.extend(self.blocks[0 : self.width])

            blocks_to_draw.extend(self.blocks[-self.width :])

            new_height = self.y_position + (self.height - 1)

        elif self.orientation == GeneratorType.DESERT_PIPE_BOX:
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

            # draw another last row
            new_height += 1

            if is_pipe_box_type_b:
                # draw another open row
                start = segment_width
            else:
                # draw the first row again to close the box
                start = 0

            stop = start + segment_width

            for segment_number in range(segments):
                blocks_to_draw.extend(self.blocks[start:stop])

            # every line repeats the last block again for some reason
            for end_of_line in range(len(blocks_to_draw), 0, -new_width):
                blocks_to_draw.insert(end_of_line, blocks_to_draw[end_of_line - 1])

            new_width += 1

        elif self.orientation in [
            GeneratorType.DIAG_DOWN_LEFT,
            GeneratorType.DIAG_DOWN_RIGHT,
            GeneratorType.DIAG_UP_RIGHT,
            GeneratorType.DIAG_WEIRD,
        ]:
            if self.ending == EndType.UNIFORM:
                new_height = (self.length + 1) * self.height
                new_width = (self.length + 1) * self.width

                left = [BLANK]
                right = [BLANK]
                slopes = self.blocks

            elif self.ending == EndType.END_ON_TOP_OR_LEFT:
                new_height = (self.length + 1) * self.height
                new_width = (self.length + 1) * (self.width - 1)  # without fill block

                if self.orientation in [GeneratorType.DIAG_DOWN_RIGHT, GeneratorType.DIAG_UP_RIGHT]:
                    fill_block = self.blocks[0:1]
                    slopes = self.blocks[1:]

                    left = fill_block
                    right = [BLANK]
                elif self.orientation == GeneratorType.DIAG_DOWN_LEFT:
                    fill_block = self.blocks[-1:]
                    slopes = self.blocks[0:-1]

                    right = fill_block
                    left = [BLANK]

                else:
                    fill_block = self.blocks[0:1]
                    slopes = self.blocks[1:]

                    right = [BLANK]
                    left = fill_block

            elif self.ending == EndType.END_ON_BOTTOM_OR_RIGHT:
                new_height = (self.length + 1) * self.height
                new_width = (self.length + 1) * (self.width - 1)  # without fill block

                fill_block = self.blocks[-1:]
                slopes = self.blocks[0:-1]

                left = [BLANK]
                right = fill_block
            else:
                # todo other two ends not used with diagonals?
                warn(f"{self.name} was not rendered.", RuntimeWarning)
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

                rows.append(amount_left * left + slopes[offset : offset + slope_width] + amount_right * right)

            if self.orientation in [GeneratorType.DIAG_UP_RIGHT]:
                for row in rows:
                    row.reverse()

            if self.orientation in [GeneratorType.DIAG_DOWN_RIGHT, GeneratorType.DIAG_UP_RIGHT]:
                if not self.height > self.width:
                    rows.reverse()

            if self.orientation == GeneratorType.DIAG_DOWN_RIGHT and self.height > self.width:
                # special case for 60 degree platform wire down right
                for row in rows:
                    row.reverse()

            if self.orientation in [GeneratorType.DIAG_UP_RIGHT]:
                base_y -= new_height - 1

            if self.orientation in [GeneratorType.DIAG_DOWN_LEFT]:
                base_x -= new_width - slope_width

            for row in rows:
                blocks_to_draw.extend(row)

        elif self.orientation in [GeneratorType.PYRAMID_TO_GROUND, GeneratorType.PYRAMID_2]:
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
                        for obj in self.objects_ref[0 : self.index_in_level]
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

        elif self.orientation == GeneratorType.ENDING:
            page_width = 16
            page_limit = page_width - self.x_position % page_width

            new_width = page_width + page_limit + 1
            new_height = (GROUND - 1) - SKY

            for y in range(SKY, GROUND - 1):
                blocks_to_draw.append(self.blocks[0])
                blocks_to_draw.extend([self.blocks[1]] * (new_width - 1))

            # todo magic number
            # ending graphics
            rom_offset = ENDING_OBJECT_OFFSET + self.object_set.get_ending_offset() * 0x60

            rom = ROM()

            ending_graphic_height = 6
            floor_height = 1

            y_offset = GROUND - floor_height - ending_graphic_height

            for y in range(ending_graphic_height):
                for x in range(page_width):
                    block_index = rom.get_byte(rom_offset + y * page_width + x - 1)

                    block_position = (y_offset + y) * new_width + x + page_limit + 1
                    blocks_to_draw[block_position] = block_index

            # the ending object is seemingly always 1 block too wide (going into the next screen)
            for end_of_line in range(len(blocks_to_draw) - 1, 0, -new_width):
                del blocks_to_draw[end_of_line]

            new_width -= 1

            # Mushroom/Fire flower/Star is categorized as an enemy

        elif self.orientation == GeneratorType.VERTICAL:
            new_height = self.length + 1
            new_width = self.width

            if self.ending == EndType.UNIFORM:
                if self.is_4byte:
                    # there is one VERTICAL 4-byte object: Vertically oriented X-blocks
                    # the width is the primary expansion
                    new_width = (self.obj_index & 0x0F) + 1

                for _ in range(new_height):
                    for y in range(self.height):
                        for x in range(new_width):
                            blocks_to_draw.append(self.blocks[y * self.height + x % self.width])

                # adjust height for giant blocks, so that the rect is correct
                new_height *= self.height

            elif self.ending == EndType.END_ON_TOP_OR_LEFT:
                # in case the drawn object is smaller than its actual size
                for y in range(min(self.height, new_height)):
                    offset = y * self.width
                    blocks_to_draw.extend(self.blocks[offset : offset + self.width])

                additional_rows = new_height - self.height

                # assume only the last row needs to repeat
                # todo true for giant blocks?
                if additional_rows > 0:
                    last_row = self.blocks[-self.width :]

                    for _ in range(additional_rows):
                        blocks_to_draw.extend(last_row)

            elif self.ending == EndType.END_ON_BOTTOM_OR_RIGHT:
                additional_rows = new_height - self.height

                # assume only the first row needs to repeat
                # todo true for giant blocks?
                if additional_rows > 0:
                    last_row = self.blocks[0 : self.width]

                    for _ in range(additional_rows):
                        blocks_to_draw.extend(last_row)

                # in case the drawn object is smaller than its actual size
                for y in range(min(self.height, new_height)):
                    offset = y * self.width
                    blocks_to_draw.extend(self.blocks[offset : offset + self.width])

            elif self.ending == EndType.TWO_ENDS:
                # object exists on ships
                top_row = self.blocks[0 : self.width]
                bottom_row = self.blocks[-self.width :]

                blocks_to_draw.extend(top_row)

                additional_rows = new_height - 2

                # repeat second to last row
                if additional_rows > 0:
                    for _ in range(additional_rows):
                        blocks_to_draw.extend(self.blocks[-2 * self.width : -self.width])

                if new_height > 1:
                    blocks_to_draw.extend(bottom_row)

        elif self.orientation in [GeneratorType.HORIZONTAL, GeneratorType.HORIZ_TO_GROUND, GeneratorType.HORIZONTAL_2]:
            new_width = self.length + 1

            if self.orientation == GeneratorType.HORIZ_TO_GROUND:
                # to the ground only, until it hits something
                for y in range(base_y, self.ground_level):
                    bottom_row = QRect(base_x, y, new_width, 1)

                    if any(
                        [
                            bottom_row.intersects(obj.get_rect()) and y == obj.get_rect().top()
                            for obj in self.objects_ref[0 : self.index_in_level]
                        ]
                    ):
                        new_height = y - base_y
                        break
                else:
                    # nothing underneath this object, extend to the ground
                    new_height = self.ground_level - base_y

                if self.is_single_block:
                    new_width = self.length

                min_height = min(self.height, 2)

                new_height = max(min_height, new_height)

            elif self.orientation == GeneratorType.HORIZONTAL_2 and self.ending == EndType.TWO_ENDS:
                # floating platforms seem to just be one shorter for some reason
                new_width -= 1
            else:
                new_height = self.height + self.secondary_length

            if self.ending == EndType.UNIFORM and not self.is_4byte:
                for y in range(new_height):
                    offset = (y % self.height) * self.width

                    for _ in range(0, new_width):
                        blocks_to_draw.extend(self.blocks[offset : offset + self.width])

                # in case of giant blocks
                new_width *= self.width

            elif self.ending == EndType.UNIFORM and self.is_4byte:
                # 4 byte objects
                top = self.blocks[0:1]
                bottom = self.blocks[-1:]

                new_height = self.height + self.secondary_length

                # ceilings are one shorter than normal
                if self.height > self.width:
                    new_height -= 1

                if self.orientation == GeneratorType.HORIZONTAL_2:
                    for _ in range(0, new_height - 1):
                        blocks_to_draw.extend(new_width * top)

                    blocks_to_draw.extend(new_width * bottom)
                else:
                    blocks_to_draw.extend(new_width * top)

                    for _ in range(1, new_height):
                        blocks_to_draw.extend(new_width * bottom)

            elif self.ending == EndType.END_ON_TOP_OR_LEFT:
                for y in range(new_height):
                    offset = y * self.width

                    blocks_to_draw.append(self.blocks[offset])

                    for x in range(1, new_width):
                        blocks_to_draw.append(self.blocks[offset + 1])

            elif self.ending == EndType.END_ON_BOTTOM_OR_RIGHT:
                for y in range(new_height):
                    offset = y * self.width

                    for x in range(new_width - 1):
                        blocks_to_draw.append(self.blocks[offset])

                    blocks_to_draw.append(self.blocks[offset + self.width - 1])

            elif self.ending == EndType.TWO_ENDS:
                if self.orientation == GeneratorType.HORIZONTAL and self.is_4byte:
                    # flat ground objects have an artificial limit of 2 lines
                    if (
                        self.object_set.number == PLAINS_OBJECT_SET
                        and self.domain == 0
                        and self.obj_index in range(0xC0, 0xE0)
                    ):
                        self.height = new_height = min(2, self.secondary_length + 1)
                    else:
                        new_height = self.secondary_length + 1

                if self.width > len(self.blocks):
                    raise ValueError(f"{self} does not provide enough blocks to fill a row.")
                else:
                    start = 0
                    end = self.width

                for y in range(self.height):
                    new_start = y * self.width
                    new_end = (y + 1) * self.width

                    if new_end > len(self.blocks):
                        # repeat the last line of blocks to fill the object
                        pass
                    else:
                        start = new_start
                        end = new_end

                    left, *middle, right = self.blocks[start:end]

                    blocks_to_draw.append(left)
                    blocks_to_draw.extend(middle * (new_width - 2))
                    blocks_to_draw.append(right)

                if not len(blocks_to_draw) % self.height == 0:
                    warn(f"Blocks to draw are not divisible by height. {self}", RuntimeWarning)

                new_width = int(len(blocks_to_draw) / self.height)

                top_row = blocks_to_draw[0:new_width]
                middle_blocks = blocks_to_draw[new_width : new_width * 2]
                bottom_row = blocks_to_draw[-new_width:]

                blocks_to_draw = top_row

                for y in range(1, new_height - 1):
                    blocks_to_draw.extend(middle_blocks)

                if new_height > 1:
                    blocks_to_draw.extend(bottom_row)
        else:
            if not self.orientation == GeneratorType.SINGLE_BLOCK_OBJECT:
                warn(f"Didn't render {self.name}", RuntimeWarning)
                # breakpoint()

            if self.name.lower() == "black boss room background":
                new_width = SCREEN_WIDTH
                new_height = SCREEN_HEIGHT

                base_x = self.x_position // SCREEN_WIDTH * SCREEN_WIDTH
                base_y = 0

                blocks_to_draw = SCREEN_WIDTH * SCREEN_HEIGHT * [self.blocks[0]]

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
            warn(
                f"Not enough Blocks for calculated height: {self.name}. "
                f"Blocks for height: {len(self.rendered_blocks) / new_width}. Rendered height: {self.rendered_height}",
                RuntimeWarning,
            )

            self.rendered_height = len(self.rendered_blocks) / new_width
        elif new_width == 0:
            warn(
                f"Calculated Width is 0, setting to 1: {self.name}. "
                f"Blocks to draw: {len(self.rendered_blocks)}. Rendered height: {self.rendered_height}",
                RuntimeWarning,
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
            self.block_cache[block_index] = get_block(block_index, self.palette_group, self.graphics_set, self.tsa_data)

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

        if self.orientation == GeneratorType.TO_THE_SKY:
            y = self.rendered_base_y + y
        else:
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

        elif self.orientation in [
            GeneratorType.HORIZONTAL,
            GeneratorType.HORIZONTAL_2,
            GeneratorType.HORIZ_TO_GROUND,
        ] or self.orientation in [
            GeneratorType.DIAG_DOWN_LEFT,
            GeneratorType.DIAG_DOWN_RIGHT,
            GeneratorType.DIAG_UP_RIGHT,
            GeneratorType.DIAG_WEIRD,
        ]:
            expands |= EXPANDS_HORIZ

        elif self.orientation in [GeneratorType.VERTICAL, GeneratorType.DIAG_WEIRD]:
            expands |= EXPANDS_VERT

        return expands

    def primary_expansion(self):
        if self.orientation in [
            GeneratorType.HORIZONTAL,
            GeneratorType.HORIZONTAL_2,
            GeneratorType.HORIZ_TO_GROUND,
        ] or self.orientation in [
            GeneratorType.DIAG_DOWN_LEFT,
            GeneratorType.DIAG_DOWN_RIGHT,
            GeneratorType.DIAG_UP_RIGHT,
            GeneratorType.DIAG_WEIRD,
        ]:
            if self.is_4byte:
                return EXPANDS_VERT
            else:
                return EXPANDS_HORIZ
        elif self.orientation in [GeneratorType.VERTICAL]:
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

        if self.orientation in [GeneratorType.PYRAMID_TO_GROUND, GeneratorType.PYRAMID_2]:
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
        return f"LevelObject {self.name} at {self.x_position}, {self.y_position}"

    def __eq__(self, other):
        if not isinstance(other, LevelObject):
            return False
        else:
            return self.to_bytes() == other.to_bytes()

    def __lt__(self, other):
        return self.index_in_level < other.index_in_level
