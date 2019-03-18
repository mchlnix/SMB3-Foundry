from File import ROM
from Sprite import Block
from m3idefs import TO_THE_SKY, HORIZ_TO_GROUND, HORIZONTAL, TWO_ENDS, UNIFORM, END_ON_TOP_OR_LEFT, \
    END_ON_BOTTOM_OR_RIGHT, HORIZONTAL_2, ENDING, VERTICAL

SKY = 0
GROUND = 26

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


class LevelObject:
    def __init__(self, data, object_set, object_definitions, palette_group):
        self.data = data

        self.object_set = object_set

        self.palette_group = palette_group

        # where to look for the graphic data?
        self.domain = (data[0] & 0b1110_0000) >> 5

        # position relative to the start of the level (top)
        self.y_position = data[0] & 0b0001_1111

        # position relative to the start of the level (left)
        self.x_position = data[1]

        # describes what object it is
        obj_index = data[2]

        domain_offset = self.domain * 0x1F

        if obj_index <= 0x0F:
            self.type = obj_index + domain_offset
            self.length = 1
        else:
            self.length = obj_index & 0b0000_1111
            self.type = (obj_index >> 4) + domain_offset + 16 - 1

        self.object_data = object_definitions[self.type]

        self.width = self.object_data.bmp_width
        self.height = self.object_data.bmp_height
        self.orientation = int(self.object_data.orientation)

        self.blocks = [int(block) for block in self.object_data.rom_object_design]

        self.block_cache = {}

        assert len(self.blocks) == self.width * self.height

    def draw(self, dc):
        base_x = self.x_position
        base_y = self.y_position

        blocks_to_draw = []

        if self.object_data.orientation == TO_THE_SKY:
            base_x = self.x_position
            base_y = SKY
            length = self.width

            for _ in range(self.y_position):
                blocks_to_draw.extend(self.blocks[0:self.width])

            blocks_to_draw.extend(self.blocks[-self.width:])

        elif self.object_data.orientation == ENDING:
            page_width = 16
            page_limit = page_width - self.x_position % page_width

            length = (page_width + page_limit)

            for y in range(SKY, GROUND):
                blocks_to_draw.append(self.blocks[0])
                blocks_to_draw.extend([self.blocks[1]] * (length - 1))

            # ending graphics
            offset = ENDING_OBJECT_OFFSET + OBJECT_SET_TO_ENDING[self.object_set] * 0x60

            rom = ROM()

            for y in range(6):
                for x in range(page_width):
                    block_index = rom.get_byte(offset + y * page_width + x - 1)
                    blocks_to_draw[(y + 20) * length + x + page_limit] = block_index

            # item is categorized as an enemy

        elif self.object_data.orientation == VERTICAL:
            length = self.length
            if self.object_data.ends == UNIFORM:
                for _ in range(length):
                    for x in range(self.width):
                        for y in range(self.height):
                            blocks_to_draw.append(self.blocks[x])

            elif self.object_data.ends == END_ON_TOP_OR_LEFT:
                pass

        elif self.object_data.orientation in [HORIZONTAL, HORIZ_TO_GROUND, HORIZONTAL_2]:
            # todo horizontal 2 seems to be one shorter than normal horizontal
            length = self.length + 1

            if self.object_data.orientation == HORIZ_TO_GROUND:
                height = GROUND - base_y
            else:
                height = self.height

            if self.object_data.ends == UNIFORM:
                # todo problems when 4byte object

                for y in range(height):
                    offset = y * self.width

                    for _ in range(0, length):
                        blocks_to_draw.extend(self.blocks[offset:offset + self.width])

                length *= self.width

            elif self.object_data.ends == END_ON_TOP_OR_LEFT:
                for y in range(height):
                    offset = y * self.width

                    blocks_to_draw.append(self.blocks[offset])

                    for x in range(1, length):
                        blocks_to_draw.append(self.blocks[offset + 1])

            elif self.object_data.ends == END_ON_BOTTOM_OR_RIGHT:
                for y in range(height):
                    offset = y * self.width

                    for x in range(length - 1):
                        blocks_to_draw.append(self.blocks[offset])

                    blocks_to_draw.append(self.blocks[offset + self.width - 1])

            elif self.object_data.ends == TWO_ENDS:
                top_and_bottom_line = 2

                for y in range(self.height):
                    offset = y * self.width
                    left, *middle, right = self.blocks[offset:offset + self.width]

                    blocks_to_draw.append(left)
                    blocks_to_draw.extend(middle * (length - top_and_bottom_line))
                    blocks_to_draw.append(right)

                assert len(blocks_to_draw) % self.height == 0

                new_width = int(len(blocks_to_draw) / self.height)

                middle_blocks = blocks_to_draw[new_width:-new_width]

                assert len(middle_blocks) == new_width or len(middle_blocks) == 0

                new_rows = height - top_and_bottom_line

                new_blocks = blocks_to_draw[0:new_width] + middle_blocks * new_rows + blocks_to_draw[-new_width:]

                blocks_to_draw = new_blocks
            else:
                breakpoint()
        else:
            for index, block_index in enumerate(self.blocks):
                x = base_x + (index % self.width)
                y = base_y + (index // self.width)

                self._draw_block(dc, block_index, x, y)

        for index, block_index in enumerate(blocks_to_draw):
            x = base_x + index % length
            y = base_y + index // length

            self._draw_block(dc, block_index, x, y)

    def _draw_block(self, dc, block_index, x, y):
        if block_index not in self.block_cache:
            if block_index > 0xFF:
                rom_block_index = ROM().get_byte(block_index)  # block_index is an offset into the graphic memory
                block = Block(ROM(), self.object_set, rom_block_index, self.palette_group)
            else:
                block = Block(ROM(), self.object_set, block_index, self.palette_group)

            self.block_cache[block_index] = block

        self.block_cache[block_index].draw(dc, x * Block.WIDTH, y * Block.HEIGHT, zoom=1)


class ThreeByteObject(LevelObject):
    def __init__(self, data, object_set, object_definitions, palette_group):
        super(ThreeByteObject, self).__init__(data, object_set, object_definitions, palette_group)


class FourByteObject(LevelObject):
    def __init__(self, data, object_set, object_definitions, palette_group):
        super(FourByteObject, self).__init__(data, object_set, object_definitions, palette_group)

        # some objects have variable lengths (ground tiles)
        self.length = data[3]


class EnemyObject:
    def __init__(self, data):
        self.type = data[0]
        self.x_position = data[1]
        self.y_position = data[2]
