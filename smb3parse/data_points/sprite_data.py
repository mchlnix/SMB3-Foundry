from smb3parse.constants import (
    BASE_OFFSET,
    MAPITEM_NOITEM,
    MAPOBJ_EMPTY,
    Map_List_Object_Ys,
    OFFSET_SIZE,
)
from smb3parse.data_points.util import DataPoint, _IndexedMixin, _PositionMixin
from smb3parse.data_points.world_map_data import WorldMapData
from smb3parse.levels import (
    FIRST_VALID_ROW,
)

MAP_SPRITE_Y_POS_LIST = Map_List_Object_Ys
MAP_SPRITE_X_POS_SCREEN_LIST = MAP_SPRITE_Y_POS_LIST + 8 * OFFSET_SIZE
MAP_SPRITE_X_POS_LIST = MAP_SPRITE_X_POS_SCREEN_LIST + 8 * OFFSET_SIZE
MAP_SPRITE_TYPES_LIST = MAP_SPRITE_X_POS_LIST + 8 * OFFSET_SIZE
MAP_SPRITE_ITEMS_LIST = MAP_SPRITE_TYPES_LIST + 8 * OFFSET_SIZE


class SpriteData(_PositionMixin, _IndexedMixin, DataPoint):
    def __init__(self, world_map_data: WorldMapData, index: int):
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
        self.x, _ = self._rom.nibbles(self._x_pos_address)
        self.y, _ = self._rom.nibbles(self._y_pos_address)
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
        self._rom.write_nibbles(self._x_pos_address, self.x)
        self._rom.write_nibbles(self._y_pos_address, self.y)
        self._rom.write(self._type_address, self.type)
        self._rom.write(self._item_address, self.item)
