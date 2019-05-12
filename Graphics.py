import abc

import wx

from Data import ENEMY_OBJ_DEF, NESPalette, enemy_handle_x, enemy_handle_y
from File import ROM
from ObjectDefinitions import load_object_definition
from Palette import load_palette
from Sprite import Block
from m3idefs import (
    TO_THE_SKY,
    HORIZ_TO_GROUND,
    HORIZONTAL,
    TWO_ENDS,
    UNIFORM,
    END_ON_TOP_OR_LEFT,
    END_ON_BOTTOM_OR_RIGHT,
    HORIZONTAL_2,
    ENDING,
    VERTICAL,
    DIAG_DOWN_LEFT,
    DIAG_DOWN_RIGHT,
    DIAG_UP_RIGHT,
    PYRAMID_TO_GROUND,
    PYRAMID_2,
    SINGLE_BLOCK_OBJECT,
    ObjectDefinition,
)

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

# todo what is this, and where should we put it?
OBJECT_SET_TO_ENDING = {
    0: 0,
    1: 0,
    2: 0,
    3: 0,
    7: 0,
    10: 0,
    13: 0,
    14: 0,  # Underground
    15: 0,
    16: 0,
    114: 0,
    4: 1,
    12: 1,
    5: 2,
    9: 2,
    11: 2,
    6: 3,
    8: 3,
}

# todo what is this, exactly?
ENDING_OBJECT_OFFSET = 0x1C8F9

# not all objects provide a block index for blank block
BLANK = -1

graphic_set2chr_index = {
    0: 0x00,  # not used
    1: 0x08,  # Plains
    2: 0x10,  # Fortress
    3: 0x1C,  # Hills / Underground
    4: 0x0C,  # Sky
    5: 0x58,  # Piranha Plant
    6: 0x58,  # Water
    7: 0x5C,  # Mushroom
    8: 0x58,  # Pipe
    9: 0x30,  # Desert
    10: 0x34,  # Ship
    11: 0x6E,  # Giant
    12: 0x18,  # Ice
    13: 0x38,  # Cloudy
    14: 0x1C,  # Not Used (same as 3)
    15: 0x24,  # Bonus Room
    16: 0x2C,  # Spade (Roulette)
    17: 0x5C,  # N-Spade (Card)
    18: 0x58,  # 2P vs.
    19: 0x6C,  # Hills / Underground alternative
    20: 0x68,  # 3-7 only
    21: 0x34,  # World 8 War Vehicle
    22: 0x28,  # Throne Room
}

common_set2chr_index = {
    0: 0x00,  # not used
    1: 0x60,  # Plains
    2: 0x60,  # Fortress
    3: 0x60,  # Hills / Underground
    4: 0x60,  # Sky
    5: 0x3E,  # Piranha Plant
    6: 0x60,  # Water
    7: 0x5E,  # Mushroom
    8: 0x60,  # Pipe
    9: 0x60,  # Desert
    10: 0x6A,  # Ship
    11: 0x60,  # Giant
    12: 0x60,  # Ice
    13: 0x60,  # Cloudy
    14: 0x60,  # Not Used (same as 3)
    15: 0x5E,  # Bonus Room
    16: 0x2E,  # Spade (Roulette)
    17: 0x5E,  # N-Spade (Card)
    18: 0x60,  # 2P vs.
    19: 0x60,  # Hills / Underground alternative
    20: 0x60,  # 3-7 only
    21: 0x70,  # World 8 War Vehicle
    22: 0x60,  # Throne Room
}


CHR_ROM_OFFSET = 0x40010
CHR_ROM_SEGMENT_SIZE = 0x400

WORLD_MAP = 0
SPADE_ROULETTE = 16
N_SPADE = 17
VS_2P = 18


class PatternTable:
    def __init__(self, graphic_set):
        self.data = bytearray()

        segments = []

        if graphic_set == WORLD_MAP:
            segments = [0x14, 0x16, 0x20, 0x21, 0x22, 0x23]
        if (
            graphic_set not in graphic_set2chr_index
            and graphic_set not in common_set2chr_index
        ):
            self._read_in([graphic_set, graphic_set + 2])
        else:
            gfx_index = graphic_set2chr_index[graphic_set]
            common_index = common_set2chr_index[graphic_set]

            segments.append(gfx_index)
            segments.append(common_index)

            if graphic_set == SPADE_ROULETTE:
                segments.extend([0x20, 0x21, 0x22, 0x23])
            elif graphic_set == N_SPADE:
                segments.extend([0x28, 0x29, 0x5A, 0x31])
            elif graphic_set == VS_2P:
                segments.extend([0x04, 0x05, 0x06, 0x07])
            else:
                segments.extend([0x00, 0x00, 0x00, 0x00])

        self._read_in(segments)

    def _read_in(self, segments):
        for segment in segments:
            self._read_in_chr_rom_segment(segment)

    def _read_in_chr_rom_segment(self, index):
        offset = CHR_ROM_OFFSET + index * CHR_ROM_SEGMENT_SIZE
        chr_rom_data = ROM().bulk_read(2 * CHR_ROM_SEGMENT_SIZE, offset)

        self.data.extend(chr_rom_data)


class LevelObjectFactory:
    object_set: int
    graphic_set: int
    palette_group_index: int

    object_definitions: list = []
    pattern_table: PatternTable = None
    palette_group: list = []

    def __init__(self, object_set, graphic_set, palette_group_index):
        self.set_object_set(object_set)
        self.set_graphic_set(graphic_set)
        self.set_palette_group_index(palette_group_index)

    def set_object_set(self, object_set):
        self.object_set = object_set
        self.object_definitions = load_object_definition(self.object_set)

    def set_graphic_set(self, graphic_set):
        self.graphic_set = graphic_set
        self.pattern_table = PatternTable(self.graphic_set)

    def set_palette_group_index(self, palette_group_index):
        self.palette_group_index = palette_group_index
        self.palette_group = load_palette(self.object_set, self.palette_group_index)

    # todo get rid of index by fixing ground map
    def from_data(self, data, index):
        return LevelObject(
            data,
            self.object_set,
            self.object_definitions,
            self.palette_group,
            self.pattern_table,
            index,
        )

    def from_properties(self, domain, object_index, x, y, length, index):
        data = bytearray(3)

        data[0] = domain << 5 | y
        data[1] = x
        data[2] = object_index

        if length is not None:
            data.append(length)

        return self.from_data(data, index)


class EnemyItemFactory:
    object_set: int
    graphic_set: int

    definitions: list = []

    def __init__(self, object_set, palette_index):
        wx.InitAllImageHandlers()
        png = wx.Image("data/gfx.png")

        rows_per_object_set = 256 // 64

        y_offset = 12 * rows_per_object_set * Block.HEIGHT

        self.png_data = png.GetSubImage(
            wx.Rect(0, y_offset, png.GetWidth(), png.GetHeight() - y_offset)
        )

        self.palette_group = load_palette(object_set, palette_index)

    # todo get rid of index by fixing ground map
    def make_object(self, data, _):
        return EnemyObject(data, self.png_data, self.palette_group)


class Drawable(abc.ABC):
    @abc.abstractmethod
    def draw(self, dc, transparent):
        pass

    @abc.abstractmethod
    def get_status_info(self):
        pass

    @abc.abstractmethod
    def set_position(self, x, y):
        pass

    @abc.abstractmethod
    def resize_to(self, x, y):
        pass

    @abc.abstractmethod
    def point_in(self, x, y):
        pass

    @abc.abstractmethod
    def get_rect(self):
        pass

    @abc.abstractmethod
    def __contains__(self, point):
        pass

    @abc.abstractmethod
    def to_bytes(self):
        pass


MASK_COLOR = [0xFF, 0x33, 0xFF]


class EnemyObject(Drawable):
    def __init__(self, data, png_data, palette_group):
        self.is_4byte = False

        self.obj_index = data[0]
        self.x_position = data[1]
        self.y_position = data[2]

        self.pattern_table = PatternTable(0x4C)
        self.palette_group = palette_group

        self.bg_color = NESPalette[palette_group[0][0]]

        self.png_data = png_data

        obj_data: ObjectDefinition = load_object_definition(ENEMY_OBJ_DEF)[
            self.obj_index
        ]

        self.description = obj_data.description

        self.width = obj_data.bmp_width
        self.height = obj_data.bmp_height

        self.rect = wx.Rect(self.x_position, self.y_position, self.width, self.height)

        self.selected = False

        self._render(obj_data)

    def _render(self, obj_data):
        self.blocks = []

        block_ids = obj_data.object_design

        for block_id in block_ids:
            x = (block_id % 64) * Block.WIDTH
            y = (block_id // 64) * Block.WIDTH

            self.blocks.append(
                self.png_data.GetSubImage(wx.Rect(x, y, Block.WIDTH, Block.HEIGHT))
            )

    def draw(self, dc, transparent):
        for i, image in enumerate(self.blocks):
            x = self.x_position + (i % self.width)
            y = self.y_position + (i // self.width)

            x_offset = int(enemy_handle_x[self.obj_index])
            y_offset = int(enemy_handle_y[self.obj_index])

            x += x_offset
            y += y_offset

            block = image.Copy()
            block.SetMaskColour(*MASK_COLOR)

            if not transparent:
                block.Replace(*MASK_COLOR, *self.bg_color)

            # todo better effect
            if self.selected:
                block = block.ConvertToDisabled(127)

            dc.DrawBitmap(
                block.ConvertToBitmap(),
                x * Block.WIDTH,
                y * Block.HEIGHT,
                useMask=transparent,
            )

    def get_status_info(self):
        return [
            ("Name", self.description),
            ("X", self.x_position),
            ("Y", self.y_position),
        ]

    def __contains__(self, item):
        x, y = item

        return self.point_in(x, y)

    def point_in(self, x, y):
        return self.rect.Contains(x, y)

    def set_position(self, x, y):
        # todo also check for the upper bounds
        x = max(0, x)
        y = max(0, y)

        self.x_position = x
        self.y_position = y

        self.rect = wx.Rect(self.x_position, self.y_position, self.width, self.height)

    def resize_to(self, _, __):
        pass

    def get_rect(self):
        return self.rect

    def to_bytes(self):
        return bytearray([self.obj_index, self.x_position, self.y_position])


class LevelObject(Drawable):
    # todo better way of saving this information?
    ground_map = []

    def __init__(
        self, data, object_set, object_definitions, palette_group, pattern_table, index
    ):
        self.pattern_table = pattern_table
        self.tsa_data = ROM.get_tsa_data(object_set)

        self.data = data

        self.object_set = object_set

        self.palette_group = palette_group

        self.index = index

        # where to look for the graphic data?
        self.domain = (data[0] & 0b1110_0000) >> 5

        # position relative to the start of the level (top)
        self.original_y = data[0] & 0b0001_1111
        self.y_position = self.original_y

        # position relative to the start of the level (left)
        self.original_x = data[1]
        self.x_position = self.original_x

        # describes what object it is
        self.obj_index = data[2]

        self.is_single_block = self.obj_index <= 0x0F

        domain_offset = self.domain * 0x1F

        if self.is_single_block:
            self.type = self.obj_index + domain_offset
        else:
            self.type = (self.obj_index >> 4) + domain_offset + 16 - 1

        object_data = object_definitions[self.type]

        self.width = object_data.bmp_width
        self.height = object_data.bmp_height
        self.orientation = object_data.orientation
        self.ending = object_data.ending
        self.description = object_data.description

        self.blocks = [int(block) for block in object_data.rom_object_design]

        self.block_cache = {}

        self.is_4byte = object_data.is_4byte

        self.secondary_length = 0

        self._calculate_lengths()

        self.rect = wx.Rect()

        self._render()

        self.selected = False

    def _calculate_lengths(self):
        if self.is_single_block:
            self.length = 1
        else:
            self.length = self.obj_index & 0b0000_1111

        if self.is_4byte:
            self.secondary_length = self.length
            self.length = self.data[3]

    def _render(self):
        if self.index < len(LevelObject.ground_map):
            del LevelObject.ground_map[self.index]

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
                        bottom_row.Intersects(rect) and y == rect.GetTop()
                        for rect in LevelObject.ground_map[0 : self.index]
                    ]
                ):
                    break

            base_x = base_x - (new_width / 2)

            # todo indexes work for all objects? No, there are left and right fill blocks
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

            # ending graphics
            rom_offset = (
                ENDING_OBJECT_OFFSET + OBJECT_SET_TO_ENDING[self.object_set] * 0x60
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
                            bottom_row.Intersects(rect) and y == rect.GetTop()
                            for rect in LevelObject.ground_map[0 : self.index]
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

                assert len(blocks_to_draw) % self.height == 0

                new_width = int(len(blocks_to_draw) / self.height)

                top_row = blocks_to_draw[0:new_width]
                bottom_row = blocks_to_draw[-new_width:]

                middle_blocks = blocks_to_draw[new_width:-new_width]

                assert len(middle_blocks) == new_width or len(middle_blocks) == 0

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
        self.x_position = self.rendered_base_x = base_x
        self.y_position = self.rendered_base_y = base_y

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

        LevelObject.ground_map.insert(self.index, self.rect)

    def draw(self, dc, transparent):
        for index, block_index in enumerate(self.rendered_blocks):
            if block_index == BLANK:
                continue

            x = self.rendered_base_x + index % self.rendered_width
            y = self.rendered_base_y + index // self.rendered_width

            self._draw_block(dc, block_index, x, y, transparent)

    def _draw_block(self, dc, block_index, x, y, transparent):
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
            x * Block.WIDTH,
            y * Block.HEIGHT,
            zoom=1,
            selected=self.selected,
            transparent=transparent,
        )

    def set_position(self, x, y):
        # todo also check for the upper bounds
        x = max(0, x)
        y = max(0, y)

        self.x_position = x
        self.y_position = y

        self._render()

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

        data.append((self.domain << 5) | self.y_position)
        data.append(self.x_position)
        data.append(self.obj_index)

        if self.is_4byte:
            data.append(self.length)

        return data


map_object_names = {
    0x00: "Mario Clear (Blue)",
    0x01: "Luigi Clear (Blue)",
    0x02: "Black Square",
    0x03: "Level 1",
    0x04: "Level 2",
    0x05: "Level 3",
    0x06: "Level 4",
    0x07: "Level 5",
    0x08: "Level 6",
    0x09: "Level 7",
    0x0A: "Level 8",
    0x0B: "Level 9",
    0x0C: "Level 10",
    0x0D: "Level 1 (Broken)",
    0x0E: "Level 2 (Broken)",
    0x0F: "Level 3 (Broken)",
    0x10: "Level 4 (Broken)",
    0x11: "Level 5 (Broken)",
    0x12: "Level 6 (Broken)",
    0x13: "Level 7 (Broken)",
    0x14: "Level 8 (Broken)",
    0x15: "Level 9 (Broken)",
    0x40: "Mario Clear (Orange)",
    0x41: "Luigi Clear (Orange)",
    0x42: "Desert Background",
    0x43: "Sand",
    0x44: "Path Upper Left",
    0x45: "Path Horizontal",
    0x46: "Path Vertical",
    0x47: "Path Upper Right",
    0x48: "Path Lower Left",
    0x49: "Path Horizontal 2",
    0x4A: "Path Lower Right",
    0x4B: "Pier",
    0x4C: "I's",
    0x4D: "Z's",
    0x4E: "? 1",
    0x4F: "? 2",
    0x50: "Mushroom House (Orange)",
    0x51: "Rock 1",
    0x52: "Rock 2",
    0x53: "Rock 3",
    0x54: "Key Door 1",
    0x55: "Star",
    0x56: "Key Door 2",
    0x57: "Miniature Path Lower Right",
    0x58: "Miniature Path Lower Left",
    0x59: "Miniature Path Horizontal",
    0x5A: "Miniature Tower",
    0x5B: "Miniature Path Point Horizontal",
    0x5C: "Miniature Path Lower Left 2",
    0x5D: "Miniature Cacti",
    0x5E: "Miniature Cacti 2",
    0x5F: "Tower",
    0x60: "Fortress Ruins",
    0x61: "Bowsers Castle Wall Tower",
    0x62: "Bowsers Castle Wall Side",
    0x63: "Bowsers Castle Wall Top 1",
    0x64: "Bowsers Castle Wall",
    0x65: "Bowsers Castle Wall Top 2",
    0x66: "Path Upper Right 2",
    0x67: "Fortress",
    0x68: "Quicksand",
    0x69: "Pyramid",
    0x6A: "Barracks",
    0x80: "Mario Clear (Green)",
    0x81: "Luigi Clear (Green)",
    0x82: "Water Three-Way Up",
    0x83: "Water Three-Way Down",
    # TODO continue
    0xB1: "Switchable Bridge Vertical",
    0xB2: "Switchable Bridge Horizontal",
    0xB3: "Round Bridge",
    0xB4: "Bushes",
    # TODO continue
    0xBB: "Palm Tree",
    0xBC: "Pipe",
    0xBD: "Fire Flower",
    0xBE: "Piranha Plant",
    0xBF: "Pond",
    0xC0: "Mario Clear (Red)",
    0xC1: "Luigi Clear (Red)",
    0xC2: "Cloud Upper Left",
    0xC3: "Cloud Top Left",
    0xC4: "Cloud Top Right",
    0xC5: "Cloud Upper Right",
    0xC6: "? 3",
    0xC7: "? 4",
    0xC8: "End Castle Top",
    0xC9: "End Castle Bottom",
    0xCA: "Bowsers Lair Top Left",
    0xCB: "Bowsers Lair Top Right",
    0xCC: "Bowsers Lair Bottom Left",
    0xCD: "Bowsers Lair Bottom Right",
    0xCE: "Cloud Left 1",
    0xCF: "? 5",
    0xD0: "Cloud Diagnoal",
    0xD1: "Flame",
    0xD2: "Cloud Left 2",
    0xD3: "Cloud Bottom",
    0xD4: "Cloud Lower Right",
    0xD5: "I's 2",
    0xD6: "Red Background ?",
    0xD7: "Desert Background 2 ?",
    0xD8: "Black Square",
    0xD9: "Path Upper Left 2",
    0xDA: "Path Horizontal 3",
    0xDB: "Path Vertical 2",
    0xDC: "Path Upper Right 2",
    0xDD: "Path Lower Left 2",
    0xDE: "Path Lower Right 2",
    0xDF: "Tower 2",
    0xE0: "Mushroom House 2",
    0xE1: "Mushroom",
    0xE2: "Skull",
    0xE3: "Fortress Ruins 2",
    0xE4: "Key Door 3",
    0xE5: "Start Field",
    0xE6: "Hand Field",
    0xE7: "? 6",
    0xE8: "Spade Bonus",
    0xE9: "Star 2",
    0xEA: "Rock Alternative",
    0xEB: "Fortress 2",
}


class MapObject:
    def __init__(self, block, x, y, zoom):
        self.x = x
        self.y = y
        self.zoom = zoom

        self.level_x = self.x // (Block.WIDTH * self.zoom)
        self.level_y = self.y // (Block.HEIGHT * self.zoom)

        self.block = block

        self.rect = wx.Rect(self.level_x, self.level_y, 1, 1)

        if self.block.index in map_object_names:
            self.name = map_object_names[self.block.index]
        else:
            self.name = str(hex(self.block.index))

        self.selected = False

    def set_position(self, x, y):
        self.level_x = x
        self.level_y = y

        self.rect = wx.Rect(x, y, 1, 1)

        self.x = x * Block.WIDTH * self.zoom
        self.y = y * Block.HEIGHT * self.zoom

    def draw(self, dc):
        self.block.draw(
            dc,
            self.x,
            self.y,
            zoom=self.zoom,
            selected=self.selected,
            transparent=False,
        )

    def get_status_info(self):
        return ("x", self.x), ("y", self.y), ("Block Type", self.name)

    def to_bytes(self):
        return self.block.index
