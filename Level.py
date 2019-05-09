import abc

import wx

from Data import Mario3Level, object_set_pointers, object_sets
from File import ROM
from Graphics import (
    LevelObject,
    PatternTable,
    MapObject,
    LevelObjectFactory,
    EnemyItemFactory,
)
from Palette import get_bg_color_for, load_palette
from Sprite import Block

ENEMY_POINTER_OFFSET = 0x10  # no idea why
LEVEL_POINTER_OFFSET = 0x10010  # also no idea

ENEMY_SIZE = 3

TIME_INF = -1

OBJECT_SET_COUNT = 16
OVERWORLD_OBJECT_SET = 0
OVERWORLD_GRAPHIC_SET = 0

LEVEL_DEFAULT_HEIGHT = 27


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


class LevelLike(abc.ABC):
    def __init__(self, world, level, object_set):
        self.world = world
        self.level = level
        self.object_set = object_set

        self.objects = []

        self.width = 1
        self.height = 1

        self.block_width = Block.WIDTH
        self.block_height = Block.HEIGHT

        self.name = "LevelLike object"

        self.object_pattern_table = None

        self.changed = False

    def to_level_point(self, x, y):
        level_x = x // self.block_width
        level_y = y // self.block_height

        return level_x, level_y

    @abc.abstractmethod
    def index_of(self, obj):
        pass

    @abc.abstractmethod
    def object_at(self, x, y):
        pass

    @abc.abstractmethod
    def get_object_names(self):
        pass

    @abc.abstractmethod
    def draw(self, dc, transparency):
        pass


class Level(LevelLike):
    scroll_types = [
        "Horizontal, up when flying",
        "Horizontal 1",
        "Free scrolling",
        "Horizontal 2",
        "Vertical only 1",
        "Horizontal 3",
        "Vertical only 2",
        "Horizontal 4",
    ]
    actions = [
        "None",
        "Sliding",
        "Out of pipe up",
        "Out of pipe down",
        "Out of pipe left",
        "Out of pipe right",
        "Climbing up ship",
        "Ship autoscroll",
    ]

    times = [300, 400, 200, TIME_INF]

    x_positions = [0x01, 0x07, 0x08, 0x0D]
    y_positions = [0x01, 0x05, 0x08, 0x0C, 0x10, 0x14, 0x17, 0x18]

    MIN_WIDTH = 0x10

    offsets = []
    world_indexes = []

    WORLDS = 0

    HEADER_LENGTH = 9  # bytes

    palettes = []

    def __init__(self, world, level, object_set=None):
        super(Level, self).__init__(world, level, object_set)
        if not Level.offsets:
            _load_level_offsets()

        self.object_set = object_set

        level_index = Level.world_indexes[world - 1] + level - 1

        level_data: Mario3Level = Level.offsets[level_index]

        if world == 0:
            self.name = level_data.name
        else:
            self.name = f"Level {world}-{level}, '{level_data.name}'"

        self.offset = level_data.rom_level_offset - Level.HEADER_LENGTH
        self.enemy_offset = level_data.enemy_offset

        print(f"Loading {self.name} @ {hex(self.offset)}/{hex(self.enemy_offset)}")

        rom = ROM()

        self._parse_header(rom)

        self.object_factory = LevelObjectFactory(
            self.object_set, self.graphic_set_index, self.object_palette_index
        )
        self.enemy_item_factory = EnemyItemFactory(
            self.object_set, self.enemy_palette_index
        )

        # self.enemy_palette_group = Level.palettes[ENEMY_BANK][self.enemy_palette_index]

        self._load_objects(rom)
        self._load_enemies()

        self.changed = False

        self.size = (self.width * Block.WIDTH, self.height * Block.HEIGHT)

        self.object_size_on_disk = self._calc_size_on_disk()
        self.enemy_size_on_disk = self.enemies * ENEMY_SIZE

    def _calc_size_on_disk(self):
        size = 0

        for obj in self.objects:
            if obj.is_4byte:
                size += 4
            else:
                size += 3

        return size

    def _parse_header(self, rom):
        self.header = rom.bulk_read(Level.HEADER_LENGTH, self.offset)

        self.start_y = Level.y_positions[(self.header[4] & 0b1110_0000) >> 5]
        self.width = Level.MIN_WIDTH + (self.header[4] & 0b0000_1111) * 0x10
        self.height = LEVEL_DEFAULT_HEIGHT

        self.start_x = Level.x_positions[(self.header[5] & 0b0110_0000) >> 5]
        self.enemy_palette_index = (self.header[5] & 0b0001_1000) >> 3
        self.object_palette_index = self.header[5] & 0b0000_0111

        self.scroll_type = Level.scroll_types[(self.header[6] & 0b0111_0000) >> 4]
        self.is_vertical = self.header[6] & 0b0001_0000
        # todo make length and height vertical flag dependent

        if self.object_set is None:
            self.object_set = self.header[6] & 0b0000_1111  # for indexing purposes

        self.start_action = (self.header[7] & 0b1110_0000) >> 5

        self.graphic_set_index = self.header[7] & 0b0001_1111

        self.time = Level.times[(self.header[8] & 0b1100_0000) >> 6]
        self.music_index = self.header[8] & 0b0000_1111

        # if there is a bonus area or other secondary level, this pointer points to it

        object_set_pointer = object_set_pointers[self.object_set]

        self.level_pointer = (
            (self.header[1] << 8)
            + self.header[0]
            + LEVEL_POINTER_OFFSET
            + object_set_pointer.type
        )
        self.enemy_pointer = (
            (self.header[3] << 8) + self.header[2] + ENEMY_POINTER_OFFSET
        )

        self.has_bonus_area = (
            object_set_pointer.min <= self.level_pointer <= object_set_pointer.max
        )

    def _load_enemies(self):
        self.enemies = []

        rom = ROM()

        rom.seek(self.enemy_offset)

        enemy_data = rom.bulk_read(ENEMY_SIZE)

        def data_left(data):
            return not (data[0] == 0xFF and data[1] in [0x00, 0x01])

        while data_left(enemy_data):
            enemy = self.enemy_item_factory.make_object(enemy_data, 0)

            self.enemies.append(enemy)

            enemy_data = rom.bulk_read(ENEMY_SIZE)

    def _load_objects(self, rom: ROM):
        self.objects = []

        object_offset = self.offset + Level.HEADER_LENGTH

        rom.seek(object_offset)

        object_order = object_sets[self.object_set]  # ordered by domain

        LevelObject.ground_map = []

        while True:
            obj_data = bytearray(rom.bulk_read(3))

            domain = (obj_data[0] & 0b1110_0000) >> 5

            obj_index = obj_data[2]
            has_length = object_order[domain][(obj_index & 0b1111_0000) >> 4] == 4

            if has_length:
                obj_data.append(rom.get_byte())

            level_object = self.object_factory.from_data(obj_data, len(self.objects))

            self.objects.append(level_object)

            if rom.peek_byte() == 0xFF:
                break

    def is_too_big(self):
        too_many_enemies = self.enemy_size_on_disk < self.enemies * ENEMY_SIZE
        too_many_objects = self._calc_size_on_disk() > self.object_size_on_disk

        return too_many_enemies or too_many_objects

    def get_all_objects(self):
        return self.objects + self.enemies

    def get_object_names(self):
        return [obj.description for obj in self.objects + self.enemies]

    def object_at(self, x, y):
        level_point = self.to_level_point(x, y)

        for obj in reversed(self.objects + self.enemies):
            if level_point in obj:
                return obj
        else:
            return None

    def draw(self, dc, transparency):
        bg_color = get_bg_color_for(self.object_set, self.object_palette_index)

        dc.SetBackground(wx.Brush(wx.Colour(bg_color)))

        dc.Clear()

        for level_object in self.objects:
            level_object.draw(dc, transparent=transparency)

        for enemy in self.enemies:
            enemy.draw(dc, transparent=transparency)

    def create_object_at(self, x, y):
        self.add_object(0, 0, x, y, None, len(self.objects))

    def create_enemy_at(self, x, y):
        # goomba to have something to display
        self.add_enemy(0x72, x, y, len(self.enemies))

    def add_object(self, domain, object_index, x, y, length, index=-1):
        if index == -1:
            index = len(self.objects)

        obj = self.object_factory.from_properties(
            domain, object_index, x, y, length, index
        )
        self.objects.insert(index, obj)

        self.changed = True

    def add_enemy(self, object_index, x, y, index=-1):
        if index == -1:
            index = len(self.enemies)
        else:
            index %= len(self.objects)

        enemy = self.enemy_item_factory.make_object([object_index, x, y], -1)

        self.enemies.insert(index, enemy)

        self.changed = True

    def index_of(self, obj):
        if obj in self.objects:
            return self.objects.index(obj)
        else:
            return len(self.objects) + self.enemies.index(obj)

    def get_object(self, index):
        if index < len(self.objects):
            return self.objects[index]
        else:
            return self.enemies[index % len(self.objects)]

    def remove_object(self, obj):
        try:
            LevelObject.ground_map.remove(obj.rect)
            self.objects.remove(obj)
        except ValueError:
            self.enemies.remove(obj)

        self.changed = True

    def to_bytes(self):
        data = bytearray()

        data.extend(self.header)

        for obj in self.objects:
            data.extend(obj.to_bytes())

        data.append(0xFF)

        enemies = bytearray()

        for enemy in sorted(self.enemies, key=lambda _enemy: _enemy.x_position):
            enemies.extend(enemy.to_bytes())

        enemies.append(0xFF)

        return [(self.offset, data), (self.enemy_offset, enemies)]


class WorldMap(LevelLike):
    WIDTH = 16
    HEIGHT = 9

    VISIBLE_BLOCKS = WIDTH * HEIGHT

    def __init__(self, world_index):
        super(WorldMap, self).__init__(0, world_index, None)

        self.name = f"World {world_index} - Overworld"

        self.pattern_table = PatternTable(OVERWORLD_GRAPHIC_SET)
        self.palette_group = load_palette(OVERWORLD_OBJECT_SET, 0)

        start = ROM.W_LAYOUT_OS_LIST[world_index - 1]
        end = ROM.rom_data.find(0xFF, start)

        self.offset = start

        self.zoom = 4

        self.block_width = Block.WIDTH * self.zoom
        self.block_height = Block.HEIGHT * self.zoom

        self.object_set = OVERWORLD_OBJECT_SET
        self.tsa_data = ROM.get_tsa_data(self.object_set)

        self.objects = []

        for index, block_index in enumerate(ROM().bulk_read(end - start, start)):
            screen_offset = (index // WorldMap.VISIBLE_BLOCKS) * WorldMap.WIDTH

            x = screen_offset + (index % WorldMap.WIDTH)
            y = (index // WorldMap.WIDTH) % WorldMap.HEIGHT

            block = Block(
                block_index, self.palette_group, self.pattern_table, self.tsa_data
            )

            self.objects.append(
                MapObject(block, x * self.block_width, y * self.block_height, self.zoom)
            )

        assert len(self.objects) % WorldMap.HEIGHT == 0

        self.width = len(self.objects) // WorldMap.HEIGHT
        self.height = WorldMap.HEIGHT

        self.size = (self.width * self.block_width, self.height * self.block_height)

    def add_object(self, obj, _):
        self.objects.append(obj)

        self.objects.sort(key=WorldMap._array_index)

    @staticmethod
    def _array_index(obj):
        return obj.level_y * WorldMap.WIDTH + obj.level_x

    def get_object_names(self):
        return [obj.name for obj in self.objects]

    def draw(self, dc, transparency=None):
        for obj in self.objects:
            obj.draw(dc)

    def index_of(self, obj):
        return self.objects.index(obj)

    def object_at(self, x, y):
        point = wx.Point(*self.to_level_point(x, y))

        for obj in reversed(self.objects):
            if obj.rect.Contains(point):
                return obj

        return None

    def to_bytes(self):
        return_array = bytearray(len(self.objects))

        for obj in self.objects:
            index = obj.level_y * WorldMap.WIDTH + obj.level_x
            return_array[index] = obj.to_bytes()

        return [(self.offset, return_array)]
