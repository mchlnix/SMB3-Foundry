from collections import defaultdict
from typing import Dict, List, Tuple

from smb3parse.constants import (
    AIRSHIP_TRAVEL_SET_COUNT,
    AIRSHIP_TRAVEL_SET_SIZE,
    BASE_OFFSET,
    FortressFXBase_ByWorld,
    FortressFX_W1,
    Map_Airship_Dest_XSets,
    Map_Airship_Dest_YSets,
    Map_Airship_Travel_BaseIdx,
    Map_Bottom_Tiles,
    Map_Tile_ColorSets,
    Map_Y_Starts,
    OFFSET_SIZE,
    World_Map_Max_PanR,
)
from smb3parse.data_points import FortressFXData
from smb3parse.data_points.level_pointer_data import LevelPointerData
from smb3parse.data_points.util import DataPoint, Position, _IndexedMixin
from smb3parse.levels import (
    LAYOUT_LIST_OFFSET,
    LEVELS_IN_WORLD_LIST_OFFSET,
    LEVEL_ENEMY_LIST_OFFSET,
    LEVEL_X_POS_LISTS,
    LEVEL_Y_POS_LISTS,
    MAX_SCREEN_COUNT,
    STRUCTURE_DATA_OFFSETS,
    WORLD_MAP_BASE_OFFSET,
    WORLD_MAP_BLANK_TILE_ID,
    WORLD_MAP_LAYOUT_DELIMITER,
    WORLD_MAP_SCREEN_SIZE,
    WORLD_MAP_WARP_WORLD_INDEX,
)
from smb3parse.util.rom import Rom


class WorldMapData(_IndexedMixin, DataPoint):
    def __init__(self, rom: Rom, world_index: int):
        self.index = world_index

        self.tile_data_offset = 0x0
        self.tile_data_offset_address = 0x0

        self.tile_data = bytearray()

        self.bottom_border_tile = 0x0
        self.bottom_border_tile_address = 0x0

        self.palette_index = 0
        self.palette_index_address = 0x0

        self.structure_data_offset = 0x0
        self.structure_data_offset_address = 0x0

        # starting point on world map
        self.map_start_y = 0
        self.map_start_y_address = 0x0

        # if/how the world map scrolls, through multiple screens
        self.map_scroll = 0
        self.map_scroll_address = 0x0

        # air ship travel data
        self.airship_travel_base_index = 0
        self.airship_travel_base_index_address = 0x0

        self.airship_travel_x_set_address = 0x0
        self.airship_travel_y_set_address = 0x0

        self.airship_travel_sets: Tuple[List[Position], List[Position], List[Position]] = ([], [], [])

        # lock and bridge data
        self.fortress_fx_base_index = 0
        self.fortress_fx_base_index_address = 0x0

        self.fortress_fx_indexes: List[int] = []
        self.fortress_fx_indexes_address = 0x0

        self.fortress_fx_count = 0
        self.fortress_fx: List[FortressFXData] = []

        # level pointer data
        self.pos_offsets_for_screen = bytearray(MAX_SCREEN_COUNT)

        self.y_pos_list_start = 0x0
        self.y_pos_list_start_address = 0x0
        self.x_pos_list_start = 0x0
        self.x_pos_list_start_address = 0x0

        self.enemy_offset_list_offset = 0
        self.enemy_offset_list_offset_address = 0x0
        self.level_offset_list_offset = 0
        self.level_offset_list_offset_address = 0x0

        self.level_pointers: List[LevelPointerData] = []

        super(WorldMapData, self).__init__(rom)

    def calculate_addresses(self):
        self.tile_data_offset_address = LAYOUT_LIST_OFFSET + OFFSET_SIZE * self.index
        self.structure_data_offset_address = STRUCTURE_DATA_OFFSETS + OFFSET_SIZE * self.index

        self.palette_index_address = Map_Tile_ColorSets + self.index
        self.bottom_border_tile_address = Map_Bottom_Tiles + self.index

        self.y_pos_list_start_address = LEVEL_Y_POS_LISTS + OFFSET_SIZE * self.index
        self.x_pos_list_start_address = LEVEL_X_POS_LISTS + OFFSET_SIZE * self.index

        self.enemy_offset_list_offset_address = LEVEL_ENEMY_LIST_OFFSET + self.index * OFFSET_SIZE
        self.level_offset_list_offset_address = LEVELS_IN_WORLD_LIST_OFFSET + self.index * OFFSET_SIZE

        self.map_start_y_address = Map_Y_Starts + self.index
        self.map_scroll_address = World_Map_Max_PanR + self.index

        # unused, because the value is always 0x03 * world_index
        self.airship_travel_base_index_address = Map_Airship_Travel_BaseIdx + self.index

        self.airship_travel_x_set_address = Map_Airship_Dest_XSets + AIRSHIP_TRAVEL_SET_COUNT * OFFSET_SIZE * self.index
        self.airship_travel_y_set_address = Map_Airship_Dest_YSets + AIRSHIP_TRAVEL_SET_COUNT * OFFSET_SIZE * self.index

        self.fortress_fx_base_index_address = FortressFXBase_ByWorld + self.index
        self.fortress_fx_base_index = self._rom.int(self.fortress_fx_base_index_address)

        self.fortress_fx_indexes_address = FortressFX_W1 + self.fortress_fx_base_index

    def read_values(self):
        self.tile_data_offset = self._rom.little_endian(self.tile_data_offset_address)
        self.tile_data = self._rom.read_until(self.layout_address, WORLD_MAP_LAYOUT_DELIMITER)

        self.palette_index = self._rom.int(self.palette_index_address)
        self.bottom_border_tile = self._rom.int(self.bottom_border_tile_address)

        self.structure_data_offset = self._rom.little_endian(self.structure_data_offset_address)

        self.pos_offsets_for_screen = self._rom.read(self.structure_block_address, MAX_SCREEN_COUNT)

        self.y_pos_list_start = WORLD_MAP_BASE_OFFSET + self._rom.little_endian(self.y_pos_list_start_address)
        self.x_pos_list_start = WORLD_MAP_BASE_OFFSET + self._rom.little_endian(self.x_pos_list_start_address)

        self.level_pointers = [LevelPointerData(self, index) for index in range(self.level_count)]

        self.enemy_offset_list_offset = self._rom.little_endian(self.enemy_offset_list_offset_address)
        self.level_offset_list_offset = self._rom.little_endian(self.level_offset_list_offset_address)

        if self.index != WORLD_MAP_WARP_WORLD_INDEX:
            assert self.level_offset_list_offset == self.enemy_offset_list_offset + self.level_count * OFFSET_SIZE

        self.map_start_y = self._rom.int(self.map_start_y_address)
        self.map_scroll = self._rom.int(self.map_scroll_address)

        self.airship_travel_base_index = self._rom.int(self.airship_travel_base_index_address)

        for set_number in range(AIRSHIP_TRAVEL_SET_COUNT):
            self.airship_travel_sets[set_number].clear()

            offset_x = self._rom.little_endian(self.airship_travel_x_set_address + set_number * OFFSET_SIZE)
            offset_y = self._rom.little_endian(self.airship_travel_y_set_address + set_number * OFFSET_SIZE)

            for index in range(AIRSHIP_TRAVEL_SET_SIZE):

                x, screen = self._rom.nibbles(BASE_OFFSET + 0xC000 + offset_x + index)
                y, _ = self._rom.nibbles(BASE_OFFSET + 0xC000 + offset_y + index)

                self.airship_travel_sets[set_number].append(Position(x, y, screen))

        self.fortress_fx_base_index = self._rom.int(self.fortress_fx_base_index_address)
        self.fortress_fx_count = self._rom.int(self.fortress_fx_base_index_address + 1) - self.fortress_fx_base_index

        self.fortress_fx.clear()
        self.fortress_fx_indexes.clear()

        for offset in range(self.fortress_fx_count):
            index = self._rom.int(self.fortress_fx_indexes_address + offset)

            self.fortress_fx.append(FortressFXData(self._rom, index))
            self.fortress_fx_indexes.append(index)

    def write_back(self, rom: Rom = None):
        if rom is None:
            rom = self._rom

        # tile_data_offset
        rom.write_little_endian(self.tile_data_offset_address, self.tile_data_offset)

        # tile_data
        rom.write(self.layout_address, self.tile_data + WORLD_MAP_LAYOUT_DELIMITER)

        rom.write(self.palette_index_address, self.palette_index)
        rom.write(self.bottom_border_tile_address, self.bottom_border_tile)

        # structure_data_offset
        rom.write_little_endian(self.structure_data_offset_address, self.structure_data_offset)

        # values depending on amount of level pointers per screen
        self.level_pointers.sort()

        level_pointer_per_screen: Dict[int, int] = defaultdict(int)

        for level_pointer in self.level_pointers:
            level_pointer_per_screen[level_pointer.screen] += 1

        self.level_count_screen_1 = level_pointer_per_screen[0]
        self.level_count_screen_2 = level_pointer_per_screen[1]
        self.level_count_screen_3 = level_pointer_per_screen[2]
        self.level_count_screen_4 = level_pointer_per_screen[3]

        # pos_offsets_for_screen
        rom.write(self.structure_block_address, self.pos_offsets_for_screen)

        # y_pos_list_start
        rom.write_little_endian(
            LEVEL_Y_POS_LISTS + OFFSET_SIZE * self.index, self.y_pos_list_start - WORLD_MAP_BASE_OFFSET
        )

        # x_pos_list_start
        rom.write_little_endian(
            LEVEL_X_POS_LISTS + OFFSET_SIZE * self.index, self.x_pos_list_start - WORLD_MAP_BASE_OFFSET
        )

        rom.write_little_endian(self.enemy_offset_list_offset_address, self.enemy_offset_list_offset)
        rom.write_little_endian(
            self.level_offset_list_offset_address, self.enemy_offset_list_offset + self.level_count * OFFSET_SIZE
        )

        for index, level_pointer in enumerate(self.level_pointers):
            level_pointer.change_index(index)
            level_pointer.write_back(rom)

        rom.write(self.map_start_y_address, self.map_start_y)
        rom.write(self.map_scroll_address, self.map_scroll)

        rom.write(self.airship_travel_base_index_address, self.airship_travel_base_index)

        for set_number in range(AIRSHIP_TRAVEL_SET_COUNT):
            offset_x = rom.little_endian(self.airship_travel_x_set_address + set_number * OFFSET_SIZE)
            offset_y = rom.little_endian(self.airship_travel_y_set_address + set_number * OFFSET_SIZE)

            for index in range(AIRSHIP_TRAVEL_SET_SIZE):
                pos: Position = self.airship_travel_sets[set_number][index]

                rom.write_nibbles(BASE_OFFSET + 0xC000 + offset_x + index, pos.x, pos.screen)
                rom.write_nibbles(BASE_OFFSET + 0xC000 + offset_y + index, pos.y)

        rom.write(self.fortress_fx_base_index_address, self.fortress_fx_base_index)

        for offset, fortress_fx_data in enumerate(self.fortress_fx):
            rom.write(self.fortress_fx_indexes_address + offset, fortress_fx_data.index)

            fortress_fx_data.write_back(rom)

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
            new_tile_data = WORLD_MAP_BLANK_TILE_ID.to_bytes(1, byteorder="big") * diff * WORLD_MAP_SCREEN_SIZE
            self.tile_data.extend(new_tile_data)

        elif new_screen_count < self.screen_count:
            self.tile_data = self.tile_data[: new_screen_count * WORLD_MAP_SCREEN_SIZE]

        self.map_scroll = self.screen_count << 4
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
