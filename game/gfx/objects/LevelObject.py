import wx

from File import ROM
from game.ObjectDefinitions import (
    HORIZONTAL,
    VERTICAL,
    DIAG_DOWN_LEFT,
    DIAG_DOWN_RIGHT,
    DIAG_UP_RIGHT,
    HORIZ_TO_GROUND,
    HORIZONTAL_2,
    SINGLE_BLOCK_OBJECT,
    PYRAMID_TO_GROUND,
    PYRAMID_2,
    TO_THE_SKY,
    ENDING,
    UNIFORM,
    END_ON_TOP_OR_LEFT,
    END_ON_BOTTOM_OR_RIGHT,
    TWO_ENDS,
    DESERT_PIPE_BOX,
)
from game.ObjectSet import ObjectSet
from game.gfx.drawable.Block import Block
from game.gfx.objects.ObjectLike import ObjectLike

SKY = 0
GROUND = 27

ENDING_STR = {
    0: "Uniform",
    1: "Top or Left",
    2: "Bottom or Right",
    3: "Top & Bottom/Left & Right",
}

ORIENTATION_TO_STR = {
    0: "Horizontal",
    1: "Vertical",
    2: "Diagonal ↙",
    3: "Desert Pipe Box",
    4: "Diagonal ↘",
    5: "Diagonal ↗",
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

# todo what is this, exactly?
ENDING_OBJECT_OFFSET = 0x1C8F9

# not all objects provide a block index for blank block
BLANK = -1

SCREEN_HEIGHT = 15
SCREEN_WIDTH = 16


class LevelObject(ObjectLike):
    def __init__(
        self,
        data,
        object_set,
        object_definitions,
        palette_group,
        pattern_table,
        objects_ref,
        is_vertical,
        index,
    ):
        self.object_set = ObjectSet(object_set)

        self.pattern_table = pattern_table
        self.tsa_data = ROM.get_tsa_data(object_set)

        self.x_position = 0
        self.y_position = 0

        self.rendered_base_x = 0
        self.rendered_base_y = 0

        self.palette_group = palette_group

        self.index = index
        self.objects_ref = objects_ref
        self.vertical_level = is_vertical

        self.data = data

        self.selected = False

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
        self.obj_index = data[2]

        self.is_single_block = self.obj_index <= 0x0F

        domain_offset = self.domain * 0x1F

        if self.is_single_block:
            self.type = self.obj_index + domain_offset
        else:
            self.type = (self.obj_index >> 4) + domain_offset + 16 - 1

        object_data = self.object_set.get_definition_of(self.type)

        self.width = object_data.bmp_width
        self.height = object_data.bmp_height
        self.orientation = object_data.orientation
        self.ending = object_data.ending
        self.description = object_data.description

        self.blocks = [int(block) for block in object_data.rom_object_design]

        self.block_cache = {}

        self.is_4byte = object_data.is_4byte

        if self.is_4byte and len(self.data) == 3:
            self.data.append(0)
        elif not self.is_4byte and len(data) == 4:
            del self.data[3]

        self.secondary_length = 0

        self._calculate_lengths()

        self.rect = wx.Rect()

        self._render()

    def _calculate_lengths(self):
        if self.is_single_block:
            self.length = 1
        else:
            self.length = self.obj_index & 0b0000_1111

        if self.is_4byte:
            self.secondary_length = self.length
            self.length = self.data[3]

    def render(self):
        self._render()

    def _render(self):
        try:
            self.index = self.objects_ref.index(self)
        except ValueError:
            # the object has not been added yet, so stick with the one given in the constructor
            pass

        base_x = self.x_position
        base_y = self.y_position

        new_width = self.width
        new_height = self.height

        blocks_to_draw = []

        if self.orientation == TO_THE_SKY:
            base_x = self.x_position
            base_y = SKY

            for _ in range(self.y_position):
                blocks_to_draw.extend(self.blocks[0 : self.width])

            blocks_to_draw.extend(self.blocks[-self.width :])

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

        elif self.orientation in [DIAG_DOWN_LEFT, DIAG_DOWN_RIGHT, DIAG_UP_RIGHT]:
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
                else:
                    fill_block = self.blocks[-1:]
                    slopes = self.blocks[0:-1]

                    left = [BLANK]
                    right = fill_block
            elif self.ending == END_ON_BOTTOM_OR_RIGHT:
                new_height = (self.length + 1) * self.height
                new_width = (self.length + 1) * (self.width - 1)  # without fill block

                fill_block = self.blocks[1:]
                slopes = self.blocks[0:1]

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
                r = (y // self.height) * slope_width
                l = new_width - slope_width - r

                offset = y % self.height

                rows.append(
                    l * left + slopes[offset : offset + slope_width] + r * right
                )

            if self.orientation in [DIAG_UP_RIGHT]:
                for row in rows:
                    row.reverse()

            if self.orientation in [DIAG_DOWN_RIGHT, DIAG_UP_RIGHT]:
                if (
                    not self.height > self.width
                ):  # special case for 60 degree platform wire down right
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

            for y in range(base_y, GROUND):
                new_height = y - base_y
                new_width = 2 * new_height

                bottom_row = wx.Rect(base_x, y, new_width, 1)

                if any(
                    [
                        bottom_row.Intersects(obj.get_rect())
                        and y == obj.get_rect().GetTop()
                        for obj in self.objects_ref[0 : self.index]
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
                blocks_to_draw.extend(
                    middle_blocks * [left_fill] + middle_blocks * [right_fill]
                )
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

            # todo magic number
            # ending graphics
            rom_offset = (
                ENDING_OBJECT_OFFSET + self.object_set.get_ending_offset() * 0x60
            )

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
                for _ in range(new_height):
                    for x in range(self.width):
                        for y in range(self.height):
                            blocks_to_draw.append(self.blocks[x])

            elif self.ending == END_ON_TOP_OR_LEFT:
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

            elif self.ending == END_ON_BOTTOM_OR_RIGHT:
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

            elif self.ending == TWO_ENDS:
                # object exists on ships
                top_row = self.blocks[0 : self.width]
                bottom_row = self.blocks[-self.width :]

                blocks_to_draw.extend(top_row)

                additional_rows = new_height - 2

                # repeat second to last row
                if additional_rows > 0:
                    for _ in range(additional_rows):
                        blocks_to_draw.extend(
                            self.blocks[-2 * self.width : -self.width]
                        )

                if new_height > 1:
                    blocks_to_draw.extend(bottom_row)

        elif self.orientation in [HORIZONTAL, HORIZ_TO_GROUND, HORIZONTAL_2]:
            new_width = self.length + 1

            if self.orientation == HORIZ_TO_GROUND:

                # to the ground only, until it hits something
                for y in range(base_y, GROUND):
                    bottom_row = wx.Rect(base_x, y, new_width, 1)

                    if any(
                        [
                            bottom_row.Intersects(obj.get_rect())
                            and y == obj.get_rect().GetTop()
                            for obj in self.objects_ref[0 : self.index]
                        ]
                    ):
                        new_height = y - base_y
                        break
                else:
                    # nothing underneath this object, extend to the ground
                    new_height = GROUND - base_y

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
                        blocks_to_draw.extend(self.blocks[offset : offset + self.width])

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
                    left, *middle, right = self.blocks[offset : offset + self.width]

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

        if not self.rendered_height == len(self.rendered_blocks) / new_width:
            print(
                f"Not enough Blocks for calculated height: {self.description}. "
                f"Blocks for height: {len(self.rendered_blocks) / new_width}. Rendered height: {self.rendered_height}"
            )

            self.rendered_height = len(self.rendered_blocks) / new_width

        self.rect = wx.Rect(
            self.rendered_base_x,
            self.rendered_base_y,
            self.rendered_width,
            self.rendered_height,
        )

    def draw(self, dc, block_length, transparent):
        for index, block_index in enumerate(self.rendered_blocks):
            if block_index == BLANK:
                continue

            x = self.rendered_base_x + index % self.rendered_width
            y = self.rendered_base_y + index // self.rendered_width

            self._draw_block(dc, block_index, x, y, block_length, transparent)

    def _draw_block(self, dc, block_index, x, y, block_length, transparent):
        if block_index not in self.block_cache:
            if block_index > 0xFF:
                rom_block_index = ROM().get_byte(
                    block_index
                )  # block_index is an offset into the graphic memory
                block = Block(
                    rom_block_index,
                    self.palette_group,
                    self.pattern_table,
                    self.tsa_data,
                )
            else:
                block = Block(
                    block_index, self.palette_group, self.pattern_table, self.tsa_data
                )

            self.block_cache[block_index] = block

        self.block_cache[block_index].draw(
            dc,
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

    def move_by(self, dx, dy):
        new_x = self.rendered_base_x + dx
        new_y = self.rendered_base_y + dy

        self.set_position(new_x, new_y)

    def get_position(self):
        return self.x_position, self.y_position

    def resize_to(self, x, y):
        if not self.is_single_block:
            if self.is_4byte:
                max_width = 0xFF
            else:
                max_width = 0x0F

            # don't get negative
            width = max(0, x - self.x_position)

            # stay under maximum width
            width = min(width, max_width)

            if self.is_4byte:
                self.data[3] = width
            else:
                base_index = (self.obj_index // 0x10) * 0x10

                self.obj_index = base_index + width
                self.data[2] = self.obj_index

            self._calculate_lengths()

            self._render()

    def resize_by(self, dx, dy):
        new_x = self.x_position + dx
        new_y = self.y_position + dy

        self.resize_to(new_x, new_y)

    def increment_type(self):
        self.change_type(True)

    def decrement_type(self):
        self.change_type(False)

    def change_type(self, increment):
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

    def __contains__(self, item):
        x, y = item

        return self.point_in(x, y)

    def point_in(self, x, y):
        return self.rect.Contains(x, y)

    def get_status_info(self):
        return [
            ("x", self.rendered_base_x),
            ("y", self.rendered_base_y),
            ("Width", self.rendered_width),
            ("Height", self.rendered_height),
            ("Orientation", ORIENTATION_TO_STR[self.orientation]),
            ("Ending", ENDING_STR[self.ending]),
        ]

    def get_rect(self):
        return self.rect

    def to_bytes(self):
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
        data.append(self.obj_index)

        if self.is_4byte:
            data.append(self.length)

        return data

    def __repr__(self):
        return f"LevelObject {self.description} at {self.x_position}, {self.y_position}"
