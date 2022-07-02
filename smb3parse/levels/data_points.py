from builtins import NotImplementedError
from typing import TYPE_CHECKING

from smb3parse.constants import BASE_OFFSET, MAPITEM_NOITEM, MAPOBJ_EMPTY, Map_List_Object_Ys
from smb3parse.levels import FIRST_VALID_ROW, OFFSET_SIZE

if TYPE_CHECKING:
    from smb3parse.util.rom import Rom
    from smb3parse.levels.world_map import WorldMap


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


class SpriteData(DataPoint):
    def __init__(self, rom, world_map: "WorldMap", index: int):
        self.world = world_map
        self.index = index

        self._x_pos_screen_address = 0x0
        self.screen = 1

        self._x_pos_address = 0x0
        self.x = 0

        self._y_pos_address = 0x0
        self.y = 0

        self._type_address = 0x0
        self.type = MAPOBJ_EMPTY

        self._item_address = 0x0
        self.item = MAPITEM_NOITEM

        super(SpriteData, self).__init__(rom)

    def calculate_addresses(self):
        y_pos_offset_for_world = self._rom.little_endian(MAP_SPRITE_Y_POS_LIST + self.world.world_index * OFFSET_SIZE)
        self._y_pos_address = BASE_OFFSET + 0xC000 + y_pos_offset_for_world + self.index

        x_pos_screen_offset_for_world = self._rom.little_endian(
            MAP_SPRITE_X_POS_SCREEN_LIST + self.world.world_index * OFFSET_SIZE
        )
        x_pos_screen_address_for_world = BASE_OFFSET + 0xC000 + x_pos_screen_offset_for_world
        self._x_pos_screen_address = x_pos_screen_address_for_world + self.index

        x_pos_offset_for_world = self._rom.little_endian(MAP_SPRITE_X_POS_LIST + self.world.world_index * OFFSET_SIZE)
        x_pos_address_for_world = BASE_OFFSET + 0xC000 + x_pos_offset_for_world
        self._x_pos_address = x_pos_address_for_world + self.index

        types_offset_for_world = self._rom.little_endian(MAP_SPRITE_TYPES_LIST + self.world.world_index * OFFSET_SIZE)
        types_address_for_world = BASE_OFFSET + 0xC000 + types_offset_for_world
        self._type_address = types_address_for_world + self.index

        item_offset_for_world = self._rom.little_endian(MAP_SPRITE_ITEMS_LIST + self.world.world_index * OFFSET_SIZE)
        item_address_for_world = BASE_OFFSET + 0xC000 + item_offset_for_world
        self._item_address = item_address_for_world + self.index

    def read_values(self):
        self.screen = self._rom.int(self._x_pos_screen_address)
        self.x = self._rom.int(self._x_pos_address) >> 4
        self.y = self._rom.int(self._y_pos_address) >> 4
        self.type = self._rom.int(self._type_address)
        self.item = self._rom.int(self._item_address)

    def change_index(self, index: int):
        self.index = index

        self.calculate_addresses()

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

    def is_at(self, screen, row, column):
        return self.screen == screen - 1 and self.x == column and self.y - FIRST_VALID_ROW == row

    def set_pos(self, screen, row, column):
        self.screen = screen
        self.x = column
        self.y = row
