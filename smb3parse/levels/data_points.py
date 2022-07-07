from builtins import NotImplementedError
from collections import defaultdict

from smb3parse.constants import BASE_OFFSET, MAPITEM_NOITEM, MAPOBJ_EMPTY, Map_List_Object_Ys, Map_Y_Starts
from smb3parse.levels import (
    FIRST_VALID_ROW,
    LAYOUT_LIST_OFFSET,
    LEVELS_IN_WORLD_LIST_OFFSET,
    LEVEL_ENEMY_LIST_OFFSET,
    LEVEL_X_POS_LISTS,
    LEVEL_Y_POS_LISTS,
    MAX_SCREEN_COUNT,
    OFFSET_BY_OBJECT_SET_A000,
    OFFSET_SIZE,
    STRUCTURE_DATA_OFFSETS,
    WORLD_MAP_BASE_OFFSET,
    WORLD_MAP_LAYOUT_DELIMITER,
    WORLD_MAP_SCREEN_SIZE,
    WORLD_MAP_SCREEN_WIDTH,
)
from smb3parse.util.rom import Rom

MAP_SPRITE_Y_POS_LIST = Map_List_Object_Ys
MAP_SPRITE_X_POS_SCREEN_LIST = MAP_SPRITE_Y_POS_LIST + 8 * OFFSET_SIZE
MAP_SPRITE_X_POS_LIST = MAP_SPRITE_X_POS_SCREEN_LIST + 8 * OFFSET_SIZE
MAP_SPRITE_TYPES_LIST = MAP_SPRITE_X_POS_LIST + 8 * OFFSET_SIZE
MAP_SPRITE_ITEMS_LIST = MAP_SPRITE_TYPES_LIST + 8 * OFFSET_SIZE


class DataPoint:
    def __init__(self, rom: Rom):
        self._rom = rom

        self.calculate_addresses()
        self.read_values()

    def calculate_addresses(self):
        raise NotImplementedError

    def read_values(self):
        raise NotImplementedError

    def write_back(self):
        raise NotImplementedError


class _PositionMixin:
    screen: int
    x: int
    y: int

    def __init__(self, *args, **kwargs):
        self.screen_address = 0x0
        self.screen = 0

        self.x_address = 0x0
        self.x = 0

        self.y_address = 0x0
        self.y = 0

        super(_PositionMixin, self).__init__(*args, **kwargs)

    def is_at(self, screen, row, column):
        return self.screen == screen - 1 and self.column == column and self.row == row + FIRST_VALID_ROW

    def set_pos(self, screen, row, column):
        self.screen = screen
        self.column = column
        self.row = row

    @property
    def row(self):
        return self.y

    @row.setter
    def row(self, value):
        self.y = value

    @property
    def column(self):
        return self.x

    @column.setter
    def column(self, value):
        self.x = value


class _IndexedMixin:
    index: int
    calculate_addresses: callable

    def change_index(self, index: int):
        self.index = index

        self.calculate_addresses()


class WorldMapData(_IndexedMixin, DataPoint):
    def __init__(self, rom: Rom, world_index: int):
        self.index = world_index

        self.tile_data_offset = 0x0
        self.tile_data_offset_address = 0x0

        self.tile_data = bytearray()

        self.structure_data_offset = 0x0
        self.structure_data_offset_address = 0x0

        self.pos_offsets_for_screen = bytearray(MAX_SCREEN_COUNT)

        self.y_pos_list_start = 0x0
        self.y_pos_list_start_address = 0x0
        self.x_pos_list_start = 0x0
        self.x_pos_list_start_address = 0x0

        self.map_start_y = 0
        self.map_start_y_address = 0x0

        self.enemy_offset_list_offset = 0
        self.enemy_offset_list_offset_address = 0x0
        self.level_offset_list_offset = 0
        self.level_offset_list_offset_address = 0x0

        self.level_pointers: list[LevelPointerData] = []

        super(WorldMapData, self).__init__(rom)

    @property
    def structure_block_address(self):
        return WORLD_MAP_BASE_OFFSET + self.structure_data_offset

    @structure_block_address.setter
    def structure_block_address(self, value):
        self.structure_data_offset = value - WORLD_MAP_BASE_OFFSET

    @property
    def layout_address(self):
        return WORLD_MAP_BASE_OFFSET + self.tile_data_offset

    @layout_address.setter
    def layout_address(self, value):
        self.tile_data_offset = value - WORLD_MAP_BASE_OFFSET

    @property
    def screen_count(self):
        return len(self.tile_data) // WORLD_MAP_SCREEN_SIZE

    @screen_count.setter
    def screen_count(self, new_screen_count):
        diff = new_screen_count - self.screen_count

        if new_screen_count > self.screen_count:
            new_tile_data = bytes(b"\xFE" * diff * WORLD_MAP_SCREEN_SIZE)
            self.tile_data.extend(new_tile_data)

        elif new_screen_count < self.screen_count:
            self.tile_data = self.tile_data[: new_screen_count * WORLD_MAP_SCREEN_SIZE]

        assert len(self.tile_data) == self.screen_count * WORLD_MAP_SCREEN_SIZE

    @property
    def level_count(self):
        return self.x_pos_list_start - self.y_pos_list_start

    # TODO: the level count influences the level data list, enemy data list, object set list,
    @property
    def level_count_screen_1(self):
        return self.pos_offsets_for_screen[1] - self.pos_offsets_for_screen[0]

    @level_count_screen_1.setter
    def level_count_screen_1(self, value):
        diff = value - self.level_count_screen_1

        self._update_level_counts(1, diff)

    @property
    def level_count_screen_2(self):
        return self.pos_offsets_for_screen[2] - self.pos_offsets_for_screen[1]

    @level_count_screen_2.setter
    def level_count_screen_2(self, value):
        diff = value - self.level_count_screen_2

        self._update_level_counts(2, diff)

    @property
    def level_count_screen_3(self):
        return self.pos_offsets_for_screen[3] - self.pos_offsets_for_screen[2]

    @level_count_screen_3.setter
    def level_count_screen_3(self, value):
        diff = value - self.level_count_screen_3

        self._update_level_counts(3, diff)

    @property
    def level_count_screen_4(self):
        return self.level_count - self.pos_offsets_for_screen[3]

    @level_count_screen_4.setter
    def level_count_screen_4(self, value):
        diff = value - self.level_count_screen_4

        self._update_level_counts(4, diff)

    def _update_level_counts(self, screen: int, diff: int):
        for i in range(MAX_SCREEN_COUNT):
            if i >= screen:
                self.pos_offsets_for_screen[i] += diff

        self.x_pos_list_start += diff

        self.level_offset_list_offset = self.enemy_offset_list_offset + self.level_count * OFFSET_SIZE

    def calculate_addresses(self):
        self.tile_data_offset_address = LAYOUT_LIST_OFFSET + OFFSET_SIZE * self.index
        self.structure_data_offset_address = STRUCTURE_DATA_OFFSETS + OFFSET_SIZE * self.index

        self.y_pos_list_start_address = LEVEL_Y_POS_LISTS + OFFSET_SIZE * self.index
        self.x_pos_list_start_address = LEVEL_X_POS_LISTS + OFFSET_SIZE * self.index

        self.enemy_offset_list_offset_address = LEVEL_ENEMY_LIST_OFFSET + self.index * OFFSET_SIZE
        self.level_offset_list_offset_address = LEVELS_IN_WORLD_LIST_OFFSET + self.index * OFFSET_SIZE

        self.map_start_y_address = Map_Y_Starts + self.index

    def read_values(self):
        self.tile_data_offset = self._rom.little_endian(self.tile_data_offset_address)
        self.tile_data = self._rom.read_until(self.layout_address, WORLD_MAP_LAYOUT_DELIMITER)

        self.structure_data_offset = self._rom.little_endian(self.structure_data_offset_address)

        self.pos_offsets_for_screen = self._rom.read(self.structure_block_address, MAX_SCREEN_COUNT)

        self.y_pos_list_start = WORLD_MAP_BASE_OFFSET + self._rom.little_endian(self.y_pos_list_start_address)
        self.x_pos_list_start = WORLD_MAP_BASE_OFFSET + self._rom.little_endian(self.x_pos_list_start_address)

        self.level_pointers = [LevelPointerData(self, index) for index in range(self.level_count)]

        self.enemy_offset_list_offset = self._rom.little_endian(self.enemy_offset_list_offset_address)
        self.level_offset_list_offset = self._rom.little_endian(self.level_offset_list_offset_address)

        assert self.level_offset_list_offset == self.enemy_offset_list_offset + self.level_count * OFFSET_SIZE

        self.map_start_y = self._rom.int(self.map_start_y_address)

    def write_back(self):
        # tile_data_offset
        self._rom.write_little_endian(self.tile_data_offset_address, self.tile_data_offset)

        # tile_data
        self._rom.write(self.layout_address, self.tile_data + WORLD_MAP_LAYOUT_DELIMITER)

        # structure_data_offset
        self._rom.write_little_endian(self.structure_data_offset_address, self.structure_data_offset)

        # values depending on amount of level pointers per screen
        self.level_pointers.sort()

        level_pointer_per_screen = defaultdict(int)

        for level_pointer in self.level_pointers:
            level_pointer_per_screen[level_pointer.screen] += 1

        self.level_count_screen_1 = level_pointer_per_screen[0]
        self.level_count_screen_2 = level_pointer_per_screen[1]
        self.level_count_screen_3 = level_pointer_per_screen[2]
        self.level_count_screen_4 = level_pointer_per_screen[3]

        # pos_offsets_for_screen
        self._rom.write(self.structure_block_address, self.pos_offsets_for_screen)

        # y_pos_list_start
        self._rom.write_little_endian(
            LEVEL_Y_POS_LISTS + OFFSET_SIZE * self.index, self.y_pos_list_start - WORLD_MAP_BASE_OFFSET
        )

        # x_pos_list_start
        self._rom.write_little_endian(
            LEVEL_X_POS_LISTS + OFFSET_SIZE * self.index, self.x_pos_list_start - WORLD_MAP_BASE_OFFSET
        )

        self._rom.write_little_endian(self.enemy_offset_list_offset_address, self.enemy_offset_list_offset)
        self._rom.write_little_endian(
            self.level_offset_list_offset_address, self.enemy_offset_list_offset + self.level_count * OFFSET_SIZE
        )

        for index, level_pointer in enumerate(self.level_pointers):
            level_pointer.change_index(index)
            level_pointer.write_back()

        self._rom.write(self.map_start_y_address, self.map_start_y)


class LevelPointerData(_PositionMixin, _IndexedMixin, DataPoint):
    def __init__(self, world_map_data: "WorldMapData", index: int):
        self.world = world_map_data
        self.index = index

        self.object_set_address = 0x0
        self.object_set = 0

        self.level_offset_address = 0x0
        self.level_offset = 0

        self.enemy_offset_address = 0x0
        self.enemy_offset = 0

        super(LevelPointerData, self).__init__(self.world._rom)

    def calculate_addresses(self):
        self.x_address = self.screen_address = self.world.x_pos_list_start + self.index
        self.y_address = self.object_set_address = self.world.y_pos_list_start + self.index

        self.level_offset_address = (
            WORLD_MAP_BASE_OFFSET
            + self._rom.little_endian(self.world.level_offset_list_offset_address)
            + OFFSET_SIZE * self.index
        )
        self.enemy_offset_address = (
            WORLD_MAP_BASE_OFFSET
            + self._rom.little_endian(self.world.enemy_offset_list_offset_address)
            + OFFSET_SIZE * self.index
        )

    @property
    def level_address(self):
        object_set_offset = (self._rom.int(OFFSET_BY_OBJECT_SET_A000 + self.object_set) * OFFSET_SIZE - 10) * 0x1000

        return BASE_OFFSET + object_set_offset + self.level_offset

    @level_address.setter
    def level_address(self, value):
        object_set_offset = (self._rom.int(OFFSET_BY_OBJECT_SET_A000 + self.object_set) * OFFSET_SIZE - 10) * 0x1000

        self.level_offset = (value - BASE_OFFSET - object_set_offset) & 0xFFFF

    @property
    def enemy_address(self):
        return BASE_OFFSET + self.enemy_offset

    @enemy_address.setter
    def enemy_address(self, value):
        self.enemy_offset = value - BASE_OFFSET

    def read_values(self):
        screen_and_x = self._rom.int(self.screen_address)

        self.screen = screen_and_x >> 4
        self.x = screen_and_x & 0x0F

        object_set_and_y = self._rom.int(self.y_address)
        self.y = object_set_and_y >> 4
        self.object_set = object_set_and_y & 0x0F

        self.level_offset = self._rom.little_endian(self.level_offset_address)
        self.enemy_offset = self._rom.little_endian(self.enemy_offset_address)

    def clear(self):
        self.screen = 0
        self.x = 0
        self.object_set = 0
        self.y = FIRST_VALID_ROW

        self.level_offset = 0x0
        self.enemy_offset = 0x0

    def write_back(self):
        screen_and_x = (self.screen << 4) + self.x
        self._rom.write(self.screen_address, screen_and_x)

        object_set_and_y = (self.y << 4) + self.object_set
        self._rom.write(self.y_address, object_set_and_y)

        self._rom.write_little_endian(self.level_offset_address, self.level_offset)
        self._rom.write_little_endian(self.enemy_offset_address, self.enemy_offset)

    def __lt__(self, other):
        self_result = self.screen * WORLD_MAP_SCREEN_SIZE + self.y * WORLD_MAP_SCREEN_WIDTH + self.x
        other_result = other.screen * WORLD_MAP_SCREEN_SIZE + other.y * WORLD_MAP_SCREEN_WIDTH + other.x

        return self_result < other_result


class SpriteData(_PositionMixin, DataPoint):
    def __init__(self, world_map_data: "WorldMapData", index: int):
        self.world = world_map_data
        self.index = index

        self._x_pos_screen_address = 0x0
        self.screen = 0

        self._x_pos_address = 0x0
        self.x = 0

        self._y_pos_address = 0x0
        self.y = 0

        self._type_address = 0x0
        self.type = MAPOBJ_EMPTY

        self._item_address = 0x0
        self.item = MAPITEM_NOITEM

        super(SpriteData, self).__init__(self.world._rom)

    def calculate_addresses(self):
        y_pos_offset_for_world = self._rom.little_endian(MAP_SPRITE_Y_POS_LIST + self.world.index * OFFSET_SIZE)
        self._y_pos_address = BASE_OFFSET + 0xC000 + y_pos_offset_for_world + self.index

        x_pos_screen_offset_for_world = self._rom.little_endian(
            MAP_SPRITE_X_POS_SCREEN_LIST + self.world.index * OFFSET_SIZE
        )
        x_pos_screen_address_for_world = BASE_OFFSET + 0xC000 + x_pos_screen_offset_for_world
        self._x_pos_screen_address = x_pos_screen_address_for_world + self.index

        x_pos_offset_for_world = self._rom.little_endian(MAP_SPRITE_X_POS_LIST + self.world.index * OFFSET_SIZE)
        x_pos_address_for_world = BASE_OFFSET + 0xC000 + x_pos_offset_for_world
        self._x_pos_address = x_pos_address_for_world + self.index

        types_offset_for_world = self._rom.little_endian(MAP_SPRITE_TYPES_LIST + self.world.index * OFFSET_SIZE)
        types_address_for_world = BASE_OFFSET + 0xC000 + types_offset_for_world
        self._type_address = types_address_for_world + self.index

        item_offset_for_world = self._rom.little_endian(MAP_SPRITE_ITEMS_LIST + self.world.index * OFFSET_SIZE)
        item_address_for_world = BASE_OFFSET + 0xC000 + item_offset_for_world
        self._item_address = item_address_for_world + self.index

    def read_values(self):
        self.screen = self._rom.int(self._x_pos_screen_address)
        self.x = self._rom.int(self._x_pos_address) >> 4
        self.y = self._rom.int(self._y_pos_address) >> 4
        self.type = self._rom.int(self._type_address)
        self.item = self._rom.int(self._item_address)

    def clear(self):
        self.screen = 0
        self.x = 0
        self.y = FIRST_VALID_ROW
        self.type = MAPOBJ_EMPTY
        self.item = MAPITEM_NOITEM

    def write_back(self):
        self._rom.write(self._x_pos_screen_address, self.screen)
        self._rom.write(self._x_pos_address, (self.x << 4) & 0xF0)
        self._rom.write(self._y_pos_address, (self.y << 4) & 0xF0)
        self._rom.write(self._type_address, self.type)
        self._rom.write(self._item_address, self.item)
