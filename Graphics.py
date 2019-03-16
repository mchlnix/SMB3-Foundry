from File import ROM
from Sprite import Block


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
        else:
            self.type = (obj_index >> 4) + domain_offset + 16 - 1

        self.object_data = object_definitions[self.type]

        self.width = self.object_data.bmp_width
        self.height = self.object_data.bmp_height

        self.blocks = [int(block) for block in self.object_data.rom_object_design]

        self.block_cache = {}

        assert len(self.blocks) == self.width * self.height

    def draw(self, dc):
        base_x = self.x_position
        base_y = self.y_position

        for index, block_index in enumerate(self.blocks):
            x = base_x + (index % self.width)
            y = base_y + (index // self.width)

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


