import wx

from Data import Mario3Level, object_set_pointers, object_ranges, plains_level, NESPalette
from File import ROM
from Graphics import FourByteObject, ThreeByteObject
from Sprite import Block
from m3idefs import ObjectDefinition

ENEMY_POINTER_OFFSET = 0x10  # no idea why
LEVEL_POINTER_OFFSET = 0x10010  # also no idea

TIME_INF = -1

OBJECT_SET_COUNT = 15
OVERWORLD_OBJECT_SET = 14

MAP_PALETTE_ADDRESS = 0x36BE2
PALETTE_ADDRESS = 0x36CA2

LEVEL_PALETTE_GROUPS_PER_OBJECT_SET = 8
ENEMY_PALETTE_GROUPS_PER_OBJECT_SET = 4
PALETTES_PER_PALETTES_GROUP = 4
COLORS_PER_PALETTE = 4
COLOR_SIZE = 1  # byte

PALETTE_DATA_SIZE = (LEVEL_PALETTE_GROUPS_PER_OBJECT_SET + ENEMY_PALETTE_GROUPS_PER_OBJECT_SET) *\
                    PALETTES_PER_PALETTES_GROUP * COLORS_PER_PALETTE


class Level:
    scroll_types = ["Horizontal, up when flying", "Horizontal 1", "Free scrolling", "Horizontal 2",
                    "Vertical only 1", "Horizontal 3", "Vertical only 2", "Horizontal 4"]
    actions = ["None", "Sliding", "Out of pipe up", "Out of pipe down",
               "Out of pipe left", "Out of pipe right", "Climbing up ship", "Ship autoscroll"]

    times = [300, 400, 200, TIME_INF]

    x_positions = [0x01, 0x07, 0x08, 0x0D]
    y_positions = [0x01, 0x05, 0x08, 0x0C, 0x10, 0x14, 0x17, 0x18]

    offsets = []
    world_indexes = []

    WORLDS = 0

    HEADER_LENGTH = 9  # bytes

    palettes = []

    def __init__(self, rom, world, level, object_set=None):
        if not Level.offsets:
            Level._load_level_offsets()

        if not Level.palettes:
            Level._load_palettes(rom)

        self.object_set = object_set

        self.block_cache = dict()

        level_index = Level.world_indexes[world - 1] + level - 1

        level_data: Mario3Level = Level.offsets[level_index]

        self.name = level_data.name

        self.offset = level_data.rom_level_offset - Level.HEADER_LENGTH

        print(f"Loading level {world}-{level} '{self.name}' @ {hex(self.offset)}")

        self.plains_level = plains_level.copy()

        self._parse_header(rom)

        self.object_palette_group = Level.palettes[self.object_set][self.object_palette_index]

        self._load_objects(rom)

        self._load_rom_object_definition()

        print(self.__dict__)

    def _parse_header(self, rom):
        header = rom.bulk_read(Level.HEADER_LENGTH, self.offset)

        self.start_y = Level.y_positions[(header[4] & 0b1110_0000) >> 5]
        self.length = (header[4] & 0b0000_1111) * 0x10 + 0x0F

        self.start_x = Level.x_positions[(header[5] & 0b0110_0000) >> 5]
        self.enemy_palette_index = (header[5] & 0b0001_1000) >> 3
        self.object_palette_index = header[5] & 0b0000_0111

        self.scroll_type = Level.scroll_types[(header[6] & 0b0111_0000) >> 4]
        self.is_vertical = header[6] & 0b0001_0000
        # todo make length and height vertical flag dependent

        if self.object_set is None:
            self.object_set = (header[6] & 0b0000_1111)  # for indexing purposes

        self.start_action = (header[7] & 0b1110_0000) >> 5

        # todo what is this for?
        self.graphic_set_index = header[7] & 0x0001_1111

        self.time = Level.times[(header[8] & 0b1100_0000) >> 6]
        self.music_index = header[8] & 0b0000_1111

        # if there is a bonus area or other secondary level, this pointer points to it

        object_set_pointer = object_set_pointers[self.object_set]

        self.level_pointer = (header[1] << 8) + header[0] + LEVEL_POINTER_OFFSET + object_set_pointer.type
        self.enemy_pointer = (header[3] << 8) + header[2] + ENEMY_POINTER_OFFSET

        self.has_bonus_area = object_set_pointer.min <= self.level_pointer <= object_set_pointer.max

    def _load_objects(self, rom: ROM):
        self.objects = []

        object_offset = self.offset + Level.HEADER_LENGTH

        rom.seek(object_offset)

        object_order = object_ranges[self.object_set]  # ordered by domain

        while True:
            obj_data = bytearray(rom.bulk_read(3))

            domain = (obj_data[0] & 0b1110_0000) >> 5

            obj_index = obj_data[2]
            has_length = object_order[domain][(obj_index & 0b1111_0000) >> 4] == 4

            if has_length:
                obj_data.append(rom.get_byte())
                level_object = FourByteObject(obj_data)
            else:
                level_object = ThreeByteObject(obj_data)

            self.objects.append(level_object)

            if rom.peek_byte() == 0xFF:
                break

    def draw(self, dc: wx.AutoBufferedPaintDC):
        bg_color = NESPalette[self.object_palette_group[0][0]]
        dc.SetBackground(wx.Brush(wx.Colour(bg_color)))

        dc.Clear()

        for level_object in self.objects:

            domain_offset = level_object.domain * 0x1F
            obj_index = level_object.type
            base_x = level_object.x_position
            base_y = level_object.y_position

            if obj_index < 0x0F:
                obj_index += domain_offset
            else:
                obj_index = (obj_index >> 4) + domain_offset + 16 - 1

            object_data: ObjectDefinition = self.plains_level[self.object_set + 1][obj_index]

            obj_width = int(object_data.bmp_width)
            obj_height = int(object_data.bmp_height)

            blocks = obj_width * obj_height

            for block in range(blocks):
                x = base_x + (block % obj_width)
                y = base_y + (block // obj_width)

                block_index = int(object_data.rom_object_design[block])

                if block_index not in self.block_cache:
                    if block_index > 0xFF:
                        rom_block_index = ROM().get_byte(block_index) # block_index is an offset into the graphic memory
                        block = Block(ROM(), self.object_set, rom_block_index, self.object_palette_group)
                    else:
                        block = Block(ROM(), self.object_set, block_index, self.object_palette_group)

                    self.block_cache[block_index] = block

                self.block_cache[block_index].draw(dc, x * Block.WIDTH, y * Block.HEIGHT, zoom=1)

    def _load_rom_object_definition(self):
        with open(f"data/romobjs{self.object_set + 1}.dat", "rb") as f:
            data = f.read()

        assert len(data) > 0

        object_count = data[0]

        if object_count < 0xF7:
            # first byte did not represent the object_count
            object_count = 0xFF
            position = 0
        else:
            position = 1

        for object_index in range(object_count):
            object_design_length = data[position]

            self.plains_level[self.object_set + 1][object_index].object_design_length = object_design_length

            position += 1

            for i in range(object_design_length):
                block_index = data[position]

                if block_index == 0xFF:
                    block_index = (data[position+1] << 16) + (data[position+2] << 8) + data[position+3]

                    position += 3

                self.plains_level[self.object_set + 1][object_index].rom_object_design[i] = block_index

                position += 1

        # read overlay data
        if position >= len(data):
            return

        for object_index in range(object_count):
            object_design_length = self.plains_level[self.object_set + 1][object_index].object_design_length

            self.plains_level[self.object_set + 1][object_index].object_design2 = []

            for i in range(object_design_length):
                if i <= object_design_length:
                    self.plains_level[self.object_set + 1][object_index].object_design2.append(data[position])
                    position += 1

    @staticmethod
    def _load_level_offsets():
        with open("data/levels.dat", "r") as level_data:
            for line_no, line in enumerate(level_data.readlines()):
                data = line.rstrip("\n").split(",")

                numbers = [int(_hex, 16) for _hex in data[0:5]]
                level_name = data[5]

                Level.offsets.append(Mario3Level(*numbers, level_name))

                world_index, level_index = numbers[0], numbers[1]

                if world_index > 0 and level_index == 1:
                    Level.world_indexes.append(line_no)

        Level.WORLDS = len(Level.world_indexes)

    @staticmethod
    def _load_palettes(rom):
        for os in range(OBJECT_SET_COUNT):
            if os == OVERWORLD_OBJECT_SET:
                palette_offset = MAP_PALETTE_ADDRESS
            else:
                palette_offset = MAP_PALETTE_ADDRESS + (os * PALETTE_DATA_SIZE)
            rom.seek(palette_offset)

            Level.palettes.append([])
            for lg in range(LEVEL_PALETTE_GROUPS_PER_OBJECT_SET):
                Level.palettes[os].append([])
                for pl in range(PALETTES_PER_PALETTES_GROUP):
                    Level.palettes[os][lg].append([])
                    for _ in range(COLORS_PER_PALETTE):
                        Level.palettes[os][lg][pl].append(rom.get_byte())
