from smb3parse.constants import (
    C000_OFFSET,
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
from smb3parse.util.rom import Rom

MAP_SPRITE_Y_POS_LIST = Map_List_Object_Ys
MAP_SPRITE_SCREEN_LIST = MAP_SPRITE_Y_POS_LIST + 8 * OFFSET_SIZE  # 8 for all non-warp world maps
MAP_SPRITE_X_POS_LIST = MAP_SPRITE_SCREEN_LIST + 8 * OFFSET_SIZE
MAP_SPRITE_TYPES_LIST = MAP_SPRITE_X_POS_LIST + 8 * OFFSET_SIZE
MAP_SPRITE_ITEMS_LIST = MAP_SPRITE_TYPES_LIST + 8 * OFFSET_SIZE


class SpriteData(_PositionMixin, _IndexedMixin, DataPoint):
    def __init__(self, world_map_data: WorldMapData, index: int):
        self.world = world_map_data
        self.index = index

        self.screen_address = 0x0
        self.screen = 0

        self._x_pos_address = 0x0
        self.x = 0

        self._y_pos_address = 0x0
        self.y = 0

        self._type_address = 0x0
        self.type = MAPOBJ_EMPTY
        """
        An ID describing what kind of Map Sprite it is, Hammer Bros, Airship, etc.
        """

        self._item_address = 0x0
        self.item = MAPITEM_NOITEM
        """
        An ID describing what item this Sprite returns, when beaten. Only really applies for Hammer Bros and similar.
        """

        super(SpriteData, self).__init__(self.world._rom)

    def calculate_addresses(self):
        self._y_pos_address = self._get_address_from_list(MAP_SPRITE_Y_POS_LIST)

        self.screen_address = self._get_address_from_list(MAP_SPRITE_SCREEN_LIST)

        self._x_pos_address = self._get_address_from_list(MAP_SPRITE_X_POS_LIST)

        self._type_address = self._get_address_from_list(MAP_SPRITE_TYPES_LIST)

        self._item_address = self._get_address_from_list(MAP_SPRITE_ITEMS_LIST)

    def _get_address_from_list(self, list_of_list_address: int) -> int:
        """
        This takes and address for a list, containing offsets to lists again and returns the address for the entry for
        this Sprite.

        For example: Every world has a list of x positions for their sprites. To get to that list, we have to consult
        another list. This one will hold addresses to the x position lists of the 8 non-warp worlds.

        The address of this list of lists the parameter.

        :param list_of_list_address:
        :return:
        """
        list_address = C000_OFFSET + self._rom.little_endian(list_of_list_address + self.world.index * OFFSET_SIZE)

        return list_address + self.index

    def read_values(self):
        self.screen = self._rom.int(self.screen_address)

        # lower nibble is 0 and is unused
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

    def write_back(self, rom: Rom = None):
        if rom is None:
            rom = self._rom

        rom.write(self.screen_address, self.screen)
        rom.write_nibbles(self._x_pos_address, self.x)
        rom.write_nibbles(self._y_pos_address, self.y)
        rom.write(self._type_address, self.type)
        rom.write(self._item_address, self.item)
