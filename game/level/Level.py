import wx

from Data import Mario3Level, object_set_pointers, object_sets
from File import ROM
from game.gfx.objects.LevelObject import LevelObject
from game.gfx.objects.LevelObjectFactory import LevelObjectFactory
from game.gfx.objects.EnemyItemFactory import EnemyItemFactory
from game.gfx.objects.EnemyItem import EnemyObject
from game.gfx.Palette import get_bg_color_for
from game.level import _load_level_offsets
from game.level.LevelLike import LevelLike

ENEMY_POINTER_OFFSET = 0x10  # no idea why
LEVEL_POINTER_OFFSET = 0x10010  # also no idea

ENEMY_SIZE = 3

TIME_INF = -1

LEVEL_DEFAULT_HEIGHT = 27
LEVEL_DEFAULT_WIDTH = 16


class Level(LevelLike):
    MIN_LENGTH = 0x10

    offsets = []
    world_indexes = []

    WORLDS = 0

    HEADER_LENGTH = 9  # bytes

    palettes = []

    def __init__(self, world, level, object_set=None):
        super(Level, self).__init__(world, level, object_set)
        if not Level.offsets:
            Level.offsets, Level.world_indexes = _load_level_offsets()

            Level.WORLDS = len(Level.world_indexes)

        self.attached_to_rom = True

        self.object_set = object_set

        level_index = Level.world_indexes[world - 1] + level - 1

        level_data: Mario3Level = Level.offsets[level_index]

        if world == 0:
            self.name = level_data.name
        else:
            self.name = f"Level {world}-{level}, '{level_data.name}'"

        self.offset = level_data.rom_level_offset - Level.HEADER_LENGTH
        self.enemy_offset = level_data.enemy_offset

        self.objects = []
        self.enemies = []

        print(f"Loading {self.name} @ {hex(self.offset)}/{hex(self.enemy_offset)}")

        rom = ROM()

        self.header = rom.bulk_read(Level.HEADER_LENGTH, self.offset)
        self._parse_header()

        object_offset = self.offset + Level.HEADER_LENGTH

        object_data = ROM.rom_data[object_offset:]
        enemy_data = ROM.rom_data[self.enemy_offset :]

        self._load_level(object_data, enemy_data)

        self.changed = False

    def _load_level(self, object_data, enemy_data):
        self.object_factory = LevelObjectFactory(
            self.object_set,
            self.graphic_set_index,
            self.object_palette_index,
            self.objects,
            self.is_vertical,
        )
        self.enemy_item_factory = EnemyItemFactory(
            self.object_set, self.enemy_palette_index
        )

        self._load_objects(object_data)
        self._load_enemies(enemy_data)

        self.object_size_on_disk = self._calc_objects_size()
        self.enemy_size_on_disk = len(self.enemies) * ENEMY_SIZE

    def reload(self):
        header_and_object_data, enemy_data = self.to_bytes()

        object_data = header_and_object_data[1][Level.HEADER_LENGTH :]

        self._load_level(object_data, enemy_data[1])

    def _calc_objects_size(self):
        size = 0

        for obj in self.objects:
            if obj.is_4byte:
                size += 4
            else:
                size += 3

        return size

    def _parse_header(self):
        self.start_y_index = (self.header[4] & 0b1110_0000) >> 5

        self.length = Level.MIN_LENGTH + (self.header[4] & 0b0000_1111) * 0x10
        self.width = self.length
        self.height = LEVEL_DEFAULT_HEIGHT

        self.start_x_index = (self.header[5] & 0b0110_0000) >> 5

        self.enemy_palette_index = (self.header[5] & 0b0001_1000) >> 3
        self.object_palette_index = self.header[5] & 0b0000_0111

        self.pipe_ends_level = not (self.header[6] & 0b1000_0000)
        self.scroll_type_index = (self.header[6] & 0b0110_0000) >> 5
        self.is_vertical = self.header[6] & 0b0001_0000

        if self.is_vertical:
            self.height = self.length
            self.width = LEVEL_DEFAULT_WIDTH

        # todo isn't that the object set for the "next area"?
        if self.object_set is None:
            self.object_set = self.header[6] & 0b0000_1111  # for indexing purposes

        self.start_action = (self.header[7] & 0b1110_0000) >> 5

        self.graphic_set_index = self.header[7] & 0b0001_1111

        self.time_index = (self.header[8] & 0b1100_0000) >> 6

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

        self.size = self.width, self.height

        self.changed = True

    def _load_enemies(self, data):
        self.enemies.clear()

        def data_left(_data):
            return data and not (_data[0] == 0xFF and _data[1] in [0x00, 0x01])

        enemy_data, data = data[0:ENEMY_SIZE], data[ENEMY_SIZE:]

        while data_left(enemy_data):
            enemy = self.enemy_item_factory.make_object(enemy_data, 0)

            self.enemies.append(enemy)

            enemy_data, data = data[0:ENEMY_SIZE], data[ENEMY_SIZE:]

    def _load_objects(self, data):
        self.objects.clear()

        if not data or data[0] == 0xFF:
            return

        object_order = object_sets[self.object_set]  # ordered by domain

        while True:
            obj_data, data = data[0:3], data[3:]

            domain = (obj_data[0] & 0b1110_0000) >> 5

            obj_index = obj_data[2]
            has_length = object_order[domain][(obj_index & 0b1111_0000) >> 4] == 4

            if has_length:
                fourth_byte, data = data[0], data[1:]
                obj_data.append(fourth_byte)

            level_object = self.object_factory.from_data(obj_data, len(self.objects))

            self.objects.append(level_object)

            if data[0] == 0xFF:
                break

    def set_length(self, length):
        if length + 1 == self.length:
            return

        self.header[4] &= 0b1111_0000
        self.header[4] |= length // 0x10

        self._parse_header()

    def set_object_palette_index(self, index):
        if index == self.object_palette_index:
            return

        self.header[5] &= 0b1111_1000
        self.header[5] |= index

        self._parse_header()

    def set_enemy_palette_index(self, index):
        if index == self.enemy_palette_index:
            return

        self.header[5] &= 0b1110_0111
        self.header[5] |= index << 3

        self._parse_header()

    def set_music_index(self, index):
        if index == self.music_index:
            return

        self.header[8] &= 0b1111_0000
        self.header[8] |= index

        self._parse_header()

    def set_time_index(self, index):
        if index == self.time_index:
            return

        self.header[8] &= 0b0011_1111
        self.header[8] |= index << 6

        self._parse_header()

    def set_x_position_index(self, index):
        if index == self.start_x_index:
            return

        self.header[5] &= 0b1001_1111
        self.header[5] |= index << 5

        self._parse_header()

    def set_y_position_index(self, index):
        if index == self.start_y_index:
            return

        self.header[4] &= 0b0001_1111
        self.header[4] |= index << 5

        self._parse_header()

    def set_action_index(self, index):
        if index == self.start_action:
            return

        self.header[7] &= 0b0001_1111
        self.header[7] |= index << 5

        self._parse_header()

    def set_gfx_index(self, index):
        if index == self.graphic_set_index:
            return

        self.header[7] &= 0b1110_0000
        self.header[7] |= index

        self._parse_header()

    def set_pipe_ends_level(self, truth_value):
        if truth_value == self.pipe_ends_level:
            return

        self.header[6] &= 0b0111_1111
        self.header[6] |= int(not truth_value) << 7

        self._parse_header()

    def set_scroll_type(self, index):
        if index == self.scroll_type_index:
            return

        self.header[6] &= 0b1001_1111
        self.header[6] |= index << 5

        self._parse_header()

    def set_is_vertical(self, truth_value):
        if truth_value == self.is_vertical:
            return

        self.header[6] &= 0b1110_1111
        self.header[6] |= int(truth_value) << 4

        self._parse_header()

    def is_too_big(self):
        too_many_enemies = self.enemy_size_on_disk < len(self.enemies) * ENEMY_SIZE
        too_many_objects = self._calc_objects_size() > self.object_size_on_disk

        return too_many_enemies or too_many_objects

    def get_all_objects(self):
        return self.objects + self.enemies

    def get_object_names(self):
        return [obj.description for obj in self.objects + self.enemies]

    def object_at(self, x, y):
        for obj in reversed(self.objects + self.enemies):
            if (x, y) in obj:
                return obj
        else:
            return None

    def draw(self, dc, block_length, transparency):
        bg_color = get_bg_color_for(self.object_set, self.object_palette_index)

        dc.SetBackground(wx.Brush(wx.Colour(bg_color)))
        dc.SetPen(wx.Pen(wx.Colour(0x00, 0x00, 0x00, 0x80), width=1))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)

        dc.Clear()

        for level_object in self.objects:
            level_object.draw(dc, block_length, transparency)

            if level_object.selected:
                x, y, w, h = level_object.get_rect().Get()

                x *= block_length
                w *= block_length
                y *= block_length
                h *= block_length

                dc.DrawRectangle(wx.Rect(x, y, w, h))

        for enemy in self.enemies:
            enemy.draw(dc, block_length, transparency)

            if enemy.selected:
                x, y, w, h = enemy.get_rect().Get()

                x *= block_length
                w *= block_length
                y *= block_length
                h *= block_length

                dc.DrawRectangle(wx.Rect(x, y, w, h))

    def paste_object_at(self, x, y, obj):
        if isinstance(obj, EnemyObject):
            return self.add_enemy(obj.obj_index, x, y)
        elif isinstance(obj, LevelObject):
            if obj.is_4byte:
                length = obj.data[3]
            else:
                length = None

            return self.add_object(obj.domain, obj.obj_index, x, y, length)

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

        return obj

    def add_enemy(self, object_index, x, y, index=-1):
        if index == -1:
            index = len(self.enemies)
        else:
            index %= len(self.objects)

        enemy = self.enemy_item_factory.make_object([object_index, x, y], -1)

        self.enemies.insert(index, enemy)

        self.changed = True

        return enemy

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
        if obj is None:
            return

        try:
            self.objects.remove(obj)
        except ValueError:
            self.enemies.remove(obj)

        self.changed = True

    def to_m3l(self):
        m3l_bytes = bytearray()

        m3l_bytes.append(self.world)
        m3l_bytes.append(self.level)
        m3l_bytes.append(self.object_set)

        m3l_bytes.extend(self.header)

        for obj in self.objects:
            m3l_bytes.extend(obj.to_bytes())

        m3l_bytes.append(0xFF)
        m3l_bytes.append(0x01)

        for enemy in sorted(self.enemies, key=lambda _enemy: _enemy.x_position):
            m3l_bytes.extend(enemy.to_bytes())

        m3l_bytes.append(0xFF)

        return m3l_bytes

    def from_m3l(self, m3l_bytes):
        self.world, self.level, self.object_set = m3l_bytes[:3]

        # reload level with new parameters
        self._load_level(b"", b"")

        m3l_bytes = m3l_bytes[3:]

        self.header = m3l_bytes[: Level.HEADER_LENGTH]
        self._parse_header()

        m3l_bytes = m3l_bytes[Level.HEADER_LENGTH :]

        self._load_objects(m3l_bytes)

        object_size = self._calc_objects_size() + 2

        object_bytes = m3l_bytes[:object_size]
        enemy_bytes = m3l_bytes[object_size:]

        self._load_level(object_bytes, enemy_bytes)

        self.attached_to_rom = False

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

    def from_bytes(self, object_data, enemy_data):

        self.offset, object_bytes = object_data
        self.enemy_offset, enemies = enemy_data

        self.header = object_bytes[0 : Level.HEADER_LENGTH]
        objects = object_bytes[Level.HEADER_LENGTH :]

        self._parse_header()
        self._load_level(objects, enemies)
