from File import ROM
from Sprite import Block
from m3idefs import TO_THE_SKY, HORIZ_TO_GROUND, HORIZONTAL, TWO_ENDS, UNIFORM

GROUND = 26


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

        if self.object_data.orientation == TO_THE_SKY:
            self._draw_block(dc, self.blocks[-1], base_x, base_y)

            for base_y in range(self.y_position):
                for index, block_index in enumerate(self.blocks[:-1]):
                    x = base_x + (index % self.width)
                    y = base_y + (index // self.width)

                    self._draw_block(dc, block_index, x, y)

        elif self.object_data.orientation == HORIZONTAL:
            length = self.length

            if self.object_data.ends == UNIFORM:
                # todo problems when 4byte object
                for index in range(length + 1):
                    x = base_x + index
                    y = base_y

                    self._draw_block(dc, self.blocks[0], x, y)

            if self.object_data.ends == TWO_ENDS:
                left_blocks = []
                middle_blocks = []
                right_blocks = []

                assert self.width == 3

                for i in range(0, len(self.blocks), 3):
                    left_blocks.append(self.blocks[i])
                    middle_blocks.append(self.blocks[i + 1])
                    right_blocks.append(self.blocks[i + 2])

                for index, block_index in enumerate(left_blocks):
                    x = base_x
                    y = base_y + index

                    self._draw_block(dc, block_index, x, y)

                for x_index in range(1, length):
                    x = base_x + x_index
                    y = base_y

                    for y_index, block_index in enumerate(middle_blocks):
                        y += y_index
                        self._draw_block(dc, block_index, x, y)

                for index, block_index in enumerate(right_blocks):
                    x = base_x + length
                    y = base_y + index

                    self._draw_block(dc, block_index, x, y)

        elif self.object_data.orientation == HORIZ_TO_GROUND:
            top_blocks = self.blocks[0:self.width]
            bottom_blocks = self.blocks[-self.width:]

            for index, block_index in enumerate(top_blocks):
                x = base_x + (index % self.width)
                y = self.y_position + (index // self.width)

                self._draw_block(dc, block_index, x, y)

            for base_y in range(self.y_position, GROUND - 1):
                for index in range(self.width, len(self.blocks) - self.width):
                    x = base_x + (index % self.width)
                    y = base_y + (index // self.width)

                    block_index = self.blocks[index]

                    self._draw_block(dc, block_index, x, y)

            for index, block_index in enumerate(bottom_blocks):
                x = base_x + (index % self.width)
                y = GROUND - 1 + (index // self.width)

                self._draw_block(dc, block_index, x, y)
        else:
            for index, block_index in enumerate(self.blocks):
                x = base_x + (index % self.width)
                y = base_y + (index // self.width)

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
