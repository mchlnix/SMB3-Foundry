from builtins import NotImplementedError

from smb3parse.constants import BASE_OFFSET, MAPITEM_NOITEM, MAPOBJ_EMPTY, Map_List_Object_Ys
from smb3parse.levels import (
    FIRST_VALID_ROW,
    LAYOUT_LIST_OFFSET,
    LEVELS_IN_WORLD_LIST_OFFSET,
    LEVEL_ENEMY_LIST_OFFSET,
    LEVEL_X_POS_LISTS,
    LEVEL_Y_POS_LISTS,
    OFFSET_BY_OBJECT_SET_A000,
    OFFSET_SIZE,
    STRUCTURE_DATA_OFFSETS,
    WORLD_MAP_BASE_OFFSET,
    WORLD_MAP_LAYOUT_DELIMITER,
)
from smb3parse.util.rom import Rom

MAP_SPRITE_Y_POS_LIST = Map_List_Object_Ys
MAP_SPRITE_X_POS_SCREEN_LIST = MAP_SPRITE_Y_POS_LIST + 8 * OFFSET_SIZE
MAP_SPRITE_X_POS_LIST = MAP_SPRITE_X_POS_SCREEN_LIST + 8 * OFFSET_SIZE
MAP_SPRITE_TYPES_LIST = MAP_SPRITE_X_POS_LIST + 8 * OFFSET_SIZE
MAP_SPRITE_ITEMS_LIST = MAP_SPRITE_TYPES_LIST + 8 * OFFSET_SIZE


class DataPoint:
    def __init__(self, rom: "Rom"):
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


class WorldMapData(DataPoint):
    def __init__(self, rom: "Rom", world_index: int):
        self.index = world_index

        self.tile_data_offset = 0x0
        self.tile_data_offset_address = 0x0

        self.tile_data = bytearray()

        self.structure_data_offset = 0x0
        self.structure_data_offset_address = 0x0

        self.pos_offsets_for_screen = bytearray(4)
        self.y_pos_list_start_address = 0x0

        self.x_pos_list_start_address = 0x0

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
    def level_count(self):
        return self.x_pos_list_start_address - self.y_pos_list_start_address

    @property
    def level_count_screen_1(self):
        return self.pos_offsets_for_screen[1] - self.pos_offsets_for_screen[0]

    @property
    def level_count_screen_2(self):
        return self.pos_offsets_for_screen[2] - self.pos_offsets_for_screen[1]

    @property
    def level_count_screen_3(self):
        return self.pos_offsets_for_screen[3] - self.pos_offsets_for_screen[2]

    @property
    def level_count_screen_4(self):
        return self.level_count - self.pos_offsets_for_screen[3]

    def calculate_addresses(self):
        self.tile_data_offset_address = LAYOUT_LIST_OFFSET + OFFSET_SIZE * self.index
        self.structure_data_offset_address = STRUCTURE_DATA_OFFSETS + OFFSET_SIZE * self.index

        self.y_pos_list_start_address = WORLD_MAP_BASE_OFFSET + self._rom.little_endian(
            LEVEL_Y_POS_LISTS + OFFSET_SIZE * self.index
        )
        self.x_pos_list_start_address = WORLD_MAP_BASE_OFFSET + self._rom.little_endian(
            LEVEL_X_POS_LISTS + OFFSET_SIZE * self.index
        )

    def read_values(self):
        self.tile_data_offset = self._rom.little_endian(self.tile_data_offset_address)
        self.tile_data = self._rom.read_until(self.layout_address, WORLD_MAP_LAYOUT_DELIMITER)

        self.structure_data_offset = self._rom.little_endian(self.structure_data_offset_address)

        self.pos_offsets_for_screen = self._rom.read(self.structure_block_address, 4)

    def write_back(self):
        self._rom.write_little_endian(self.tile_data_offset_address, self.tile_data_offset)
        self._rom.write(self.layout_address, self.tile_data + WORLD_MAP_LAYOUT_DELIMITER)

        self._rom.write_little_endian(self.structure_data_offset_address, self.structure_data_offset)
        self._rom.write(self.structure_block_address, self.pos_offsets_for_screen)


class LevelPointerData(_PositionMixin, DataPoint):
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
        level_y_pos_list_start = WORLD_MAP_BASE_OFFSET + self._rom.little_endian(
            LEVEL_Y_POS_LISTS + OFFSET_SIZE * self.world.index
        )

        level_x_pos_list_start = WORLD_MAP_BASE_OFFSET + self._rom.little_endian(
            LEVEL_X_POS_LISTS + OFFSET_SIZE * self.world.index
        )

        self.x_address = self.screen_address = level_x_pos_list_start + self.index
        self.y_address = self.object_set_address = level_y_pos_list_start + self.index

        # get level offset
        level_list_offset_position = LEVELS_IN_WORLD_LIST_OFFSET + self.world.index * OFFSET_SIZE
        level_list_address = WORLD_MAP_BASE_OFFSET + self._rom.little_endian(level_list_offset_position)

        self.level_offset_address = level_list_address + OFFSET_SIZE * self.index

        enemy_list_start_offset = LEVEL_ENEMY_LIST_OFFSET + self.world.index * OFFSET_SIZE
        enemy_list_start = WORLD_MAP_BASE_OFFSET + self._rom.little_endian(enemy_list_start_offset)

        self.enemy_offset_address = enemy_list_start + OFFSET_SIZE * self.index

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
