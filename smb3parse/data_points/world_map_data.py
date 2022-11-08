from collections import defaultdict

from typing import Optional

from smb3parse.constants import (
    AIRSHIP_TRAVEL_SET_COUNT,
    AIRSHIP_TRAVEL_SET_SIZE,
    Airship_Layouts,
    Airship_Objects,
    BASE_OFFSET,
    CoinShip_Layouts,
    CoinShip_Objects,
    FortressFXBase_ByWorld,
    FortressFX_W1,
    LevelJctBQ_Layout,
    LevelJctBQ_Objects,
    LevelJctBQ_Tileset,
    LevelJctGE_Layout,
    LevelJctGE_Objects,
    LevelJctGE_Tileset,
    Map_Airship_Dest_XSets,
    Map_Airship_Dest_YSets,
    Map_Airship_Travel_BaseIdx,
    Map_AnimSpeeds,
    Map_Bottom_Tiles,
    Map_Object_ColorSets,
    Map_Tile_ColorSets,
    Map_Y_Starts,
    OFFSET_SIZE,
    ToadShop_Layouts,
    ToadShop_Objects,
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
from smb3parse.objects.object_set import AIR_SHIP_OBJECT_SET, MUSHROOM_OBJECT_SET, ObjectSet
from smb3parse.util.rom import Rom


class WorldMapData(_IndexedMixin, DataPoint):
    """
    This object compiles all information associated with World Maps, like their tile data, palette index, screen count
    and more.
    """

    def __init__(self, rom: Rom, world_index: int):
        self.index = world_index

        self.tile_data_offset_address = 0x0
        self.tile_data_offset = 0x0
        """The offset into the RAM the tile data for this World Map is located, when its PRG is loaded."""

        self.tile_data = bytearray()
        """
        All the Tile IDs, that make up the layout of the World Map. Will be a multiple of 16 x 9 tile IDs, depending on
        how many screens there are.
        """

        self.bottom_border_tile_address = 0x0
        self.bottom_border_tile = 0x0
        """The Tile ID, that is used to fill the bottom row of the border around the World Map."""

        self.palette_index_address = 0x0
        self.palette_index = 0
        """Which color palette should be used with this World Map."""

        self.obj_color_index_address = 0x0
        self.obj_color_index = 0
        """Which color palette should be used for the Overworld Sprites, like Hammer Bros."""

        self.frame_tick_count_address = 0
        self.frame_tick_count = 0
        """
        How many ticks each animation frame stays on screen, before switching to the next. The higher this value is, the
        slower the animated Tiles are changing. 0 means no animation.
        """

        self.structure_data_offset_address = 0x0
        self.structure_data_offset = 0x0
        """
        The structure data is a handful of lists for the Level and Sprite Locations and their types and items. All the
        lists appear one after another, making it one block of data.
        """

        self.map_start_y_address = 0x0
        self.map_start_y = 0
        """
        The y Position of where Mario starts, when entering the Overworld. In the vanilla game the x coordinate is hard
        coded to column 2, so only the y/row position can be changed.
        """

        self.map_scroll_address = 0x0
        self.map_scroll = 0
        """
        Determines, whether the screen should scroll onto the next, when the player reaches the edge of their current
        screen.
        If disabled, it can hide, that this world has multiple screens, as in World 5.
        """

        self.airship_travel_base_index_address = 0x0
        self.airship_travel_base_index = 0
        """
        All Airship travel routes are in one large list. Every World Map can have 3 indexes into this list, therefore
        selecting 3 of these routes for it to use. Which one of these three is then used is determined randomly, when
        the World Map is initially loaded.

        These 3 times 8 (without Warp World) indexes are in one long list and each World Map remembers where its 3
        indexes are by saving that index. In the Vanilla Game, the indexes are simply the world number (0-indexed)
        times 3, so 0x0, 0x3, 0x6 etc.

        One could change this, so that two worlds use the exact same indexes, for example. But since there is enough
        space for every World to choose its own 3 indexes, there is no reason to do such a thing.

        So changing this value should not be necessary.
        """

        self.airship_travel_x_set_address = 0x0
        self.airship_travel_y_set_address = 0x0

        self.airship_travel_sets: tuple[list[Position], list[Position], list[Position]] = ([], [], [])
        """
        Each World Map has 3 possible Airship routes, one of which is chosen at random, when the World Map is initially
        loaded.

        Each of them has 6 Positions on the world map, which the Airship is traveling along.
        """

        # lock and bridge data
        self.fortress_fx_base_index_address = 0x0
        self.fortress_fx_base_index = 0
        """
        See also FortressFXData.

        Similar to the Airship routes, there is a list of FortressFX data points, except that each World Map gets 4.

        There are a total of 17 possible locks, which each World can choose from. In the Vanilla game, there is no
        overlap between Worlds, but if the layout makes sense two Worlds can share Locks.

        Since each World has space to define 4 locks, there is no reason to change this value.
        """

        self.fortress_fx_indexes: list[int] = []
        """The 4 indexes into the list of 17 locks, that the World has chosen."""

        self.fortress_fx_count = 0
        """Amount of locks this World has designated. Should always be 4."""

        self.fortress_fx: list[FortressFXData] = []
        """The FortressFxData objects, this World has selected."""

        # level pointer data
        self.pos_offsets_for_screen = bytearray(MAX_SCREEN_COUNT)
        """
        When entering a Level, a list of level positions is searched through. Once the players current position is found
        that Positions index is used to look up the Level information in another list.

        Since these positions are ordered by screen and to make searching faster, the game saves the first position of
        each screen in this list.

        Four bytes, one for each screen, where the first byte is naturally always 0.
        """

        self.y_pos_list_start_address = 0x0
        self.y_pos_list_start = 0x0
        """
        The address of the list of y Positions for Level Pointers for this World Map.

        When trying to find the Level the player is standing on, first the y Positions are gone through, until a
        suitable one was found, then, from that index on, the x Positions are gone through until a match is found there,
        too.

        That index can then be used to find the Level and Enemy/Item Offset of that Level.
        """

        self.x_pos_list_start_address = 0x0
        self.x_pos_list_start = 0x0
        """See y_pos_list_start."""

        self.enemy_offset_list_offset_address = 0x0
        self.enemy_offset_list_offset = 0x0
        """See y_pos_list_start."""

        self.level_offset_list_offset_address = 0x0
        self.level_offset_list_offset = 0x0
        """See y_pos_list_start."""

        self.level_pointers: list[LevelPointerData] = []
        """
        The parsed information of Position on World Map, location in memory and Object set of all Level Pointers this
        World has defined.
        """

        self.airship_enemy_offset_address = 0x0
        self.airship_enemy_offset = 0x0
        self.airship_level_offset_address = 0x0
        self.airship_level_offset = 0x0
        """
        The Airship Level that leads you to a Koopa Kid is defined per World, so you go to the same one each time. Its
        Object Set is hard coded as Airship.
        """

        self.coin_ship_enemy_offset_address = 0x0
        self.coin_ship_enemy_offset = 0x0
        self.coin_ship_level_offset_address = 0x0
        self.coin_ship_level_offset = 0x0
        """
        The coin ship Bonus Level that you get to via the overworld Sprite. It is defined per World, so you go to the
        same one each time. Its Object Set is hard coded as Airship.
        """

        self.generic_exit_object_set_address = 0x0
        self.generic_exit_object_set = 0
        self.generic_exit_enemy_offset_address = 0x0
        self.generic_exit_enemy_offset = 0x0
        self.generic_exit_level_offset_address = 0x0
        self.generic_exit_level_offset = 0x0
        """
        Some Object Sets have a Pipe, that ignores the Jump Destination of the Header and instead goes to a Level that
        is supposed to be used like a Generic Exit, allowing both this and a bonus level via normal Pipes. That level
        can be set per World. In the Vanilla Game the Object Set is always Plains, but this can actually be configured.
        """

        self.big_q_block_object_set_address = 0x0
        self.big_q_block_object_set = 0
        self.big_q_block_enemy_offset_address = 0x0
        self.big_q_block_enemy_offset = 0x0
        self.big_q_block_level_offset_address = 0x0
        self.big_q_block_level_offset = 0x0
        """
        Some Object Sets have a Pipe, that ignores the Jump Destination of the Header and instead goes to a Level with a
        Big Question Mark Block, that can be set per World. In the Vanilla Game the Object Set is always Underground,
        but this can actually be configured.
        """

        self.toad_warp_level_offset_address = 0x0
        self.toad_warp_level_offset = 0x0
        """
        The address of the Toad Level. Even though it does not look like a normal level, it is still saved in the ROM as
        one. Every Overworld could have its own, but they all have the same in the Vanilla game.
        """

        self.toad_warp_item_address = 0x0
        self.toad_warp_item = 0
        """
        Is saved as an offset, but only determines what is in the Toad Chest in the upper nibble. 0x02(00) for the warp
        whistle, 0x0A(00) for the Anchor.
        """

        super(WorldMapData, self).__init__(rom)

    def calculate_addresses(self):
        self.tile_data_offset_address = LAYOUT_LIST_OFFSET + OFFSET_SIZE * self.index

        self.palette_index_address = Map_Tile_ColorSets + self.index
        self.obj_color_index_address = Map_Object_ColorSets + self.index

        self.bottom_border_tile_address = Map_Bottom_Tiles + self.index
        # TODO you can define a separate tick count for each anim frame, not used in game though
        self.frame_tick_count_address = Map_AnimSpeeds + self.index * 4  # 4 animation frames

        self.structure_data_offset_address = STRUCTURE_DATA_OFFSETS + OFFSET_SIZE * self.index

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

        self.airship_level_offset_address = Airship_Layouts + OFFSET_SIZE * self.index
        self.airship_enemy_offset_address = Airship_Objects + OFFSET_SIZE * self.index

        self.coin_ship_level_offset_address = CoinShip_Layouts + OFFSET_SIZE * self.index
        self.coin_ship_enemy_offset_address = CoinShip_Objects + OFFSET_SIZE * self.index

        self.generic_exit_level_offset_address = LevelJctGE_Layout + OFFSET_SIZE * self.index
        self.generic_exit_enemy_offset_address = LevelJctGE_Objects + OFFSET_SIZE * self.index
        self.generic_exit_object_set_address = LevelJctGE_Tileset + self.index

        self.big_q_block_level_offset_address = LevelJctBQ_Layout + OFFSET_SIZE * self.index
        self.big_q_block_enemy_offset_address = LevelJctBQ_Objects + OFFSET_SIZE * self.index
        self.big_q_block_object_set_address = LevelJctBQ_Tileset + self.index

        self.toad_warp_level_offset_address = ToadShop_Layouts + OFFSET_SIZE * self.index
        self.toad_warp_item_address = ToadShop_Objects + OFFSET_SIZE * self.index

    def read_values(self):
        self.tile_data_offset = self._rom.little_endian(self.tile_data_offset_address)
        self.tile_data = self._rom.read_until(self.layout_address, WORLD_MAP_LAYOUT_DELIMITER)

        self.palette_index = self._rom.int(self.palette_index_address)
        self.obj_color_index = self._rom.int(self.obj_color_index_address)

        self.bottom_border_tile = self._rom.int(self.bottom_border_tile_address)
        self.frame_tick_count = self._rom.int(self.frame_tick_count_address)

        self.structure_data_offset = self._rom.little_endian(self.structure_data_offset_address)

        self.pos_offsets_for_screen = self._rom.read(self.structure_block_address, MAX_SCREEN_COUNT)

        self.y_pos_list_start = WORLD_MAP_BASE_OFFSET + self._rom.little_endian(self.y_pos_list_start_address)
        self.x_pos_list_start = WORLD_MAP_BASE_OFFSET + self._rom.little_endian(self.x_pos_list_start_address)

        self.level_pointers = [LevelPointerData(self, index) for index in range(self.level_count)]

        self.enemy_offset_list_offset = self._rom.little_endian(self.enemy_offset_list_offset_address)
        self.level_offset_list_offset = self._rom.little_endian(self.level_offset_list_offset_address)

        if self.index != WORLD_MAP_WARP_WORLD_INDEX:
            assert self.level_offset_list_offset == self.enemy_offset_list_offset + self.level_count * OFFSET_SIZE, (
                hex(self.level_offset_list_offset - self.enemy_offset_list_offset),
                self.level_count,
            )

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
            index = self._rom.int(self.fortress_fx_indexes_start_address + offset)

            self.fortress_fx.append(FortressFXData(self._rom, index))
            self.fortress_fx_indexes.append(index)

        self.airship_level_offset = self._rom.little_endian(self.airship_level_offset_address)
        self.airship_enemy_offset = self._rom.little_endian(self.airship_enemy_offset_address)

        self.coin_ship_level_offset = self._rom.little_endian(self.coin_ship_level_offset_address)
        self.coin_ship_enemy_offset = self._rom.little_endian(self.coin_ship_enemy_offset_address)

        self.generic_exit_level_offset = self._rom.little_endian(self.generic_exit_level_offset_address)
        self.generic_exit_enemy_offset = self._rom.little_endian(self.generic_exit_enemy_offset_address)
        self.generic_exit_object_set = self._rom.int(self.generic_exit_object_set_address)

        self.big_q_block_level_offset = self._rom.little_endian(self.big_q_block_level_offset_address)
        self.big_q_block_enemy_offset = self._rom.little_endian(self.big_q_block_enemy_offset_address)
        self.big_q_block_object_set = self._rom.int(self.big_q_block_object_set_address)

        self.toad_warp_level_offset = self._rom.little_endian(self.toad_warp_level_offset_address)
        self.toad_warp_item = self._rom.little_endian(self.toad_warp_item_address)

    def write_back(self, rom: Optional[Rom] = None):
        if rom is None:
            rom = self._rom

        # tile_data_offset
        rom.write_little_endian(self.tile_data_offset_address, self.tile_data_offset)

        # tile_data
        rom.write(self.layout_address, self.tile_data + WORLD_MAP_LAYOUT_DELIMITER)

        rom.write(self.palette_index_address, self.palette_index)
        rom.write(self.obj_color_index_address, self.obj_color_index)

        rom.write(self.bottom_border_tile_address, self.bottom_border_tile)
        rom.write(self.frame_tick_count_address, bytearray([self.frame_tick_count] * 4))

        # structure_data_offset
        rom.write_little_endian(self.structure_data_offset_address, self.structure_data_offset)

        # values depending on amount of level pointers per screen
        self.level_pointers.sort()
        assert self.level_count == len(self.level_pointers)

        level_pointer_per_screen: dict[int, int] = defaultdict(int)

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
            rom.write(self.fortress_fx_indexes_start_address + offset, fortress_fx_data.index)

            fortress_fx_data.write_back(rom)

        rom.write_little_endian(self.airship_level_offset_address, self.airship_level_offset)
        rom.write_little_endian(self.airship_enemy_offset_address, self.airship_enemy_offset)

        rom.write_little_endian(self.coin_ship_level_offset_address, self.coin_ship_level_offset)
        rom.write_little_endian(self.coin_ship_enemy_offset_address, self.coin_ship_enemy_offset)

        rom.write_little_endian(self.generic_exit_level_offset_address, self.generic_exit_level_offset)
        rom.write_little_endian(self.generic_exit_enemy_offset_address, self.generic_exit_enemy_offset)
        rom.write(self.generic_exit_object_set_address, self.generic_exit_object_set)

        rom.write_little_endian(self.big_q_block_level_offset_address, self.big_q_block_level_offset)
        rom.write_little_endian(self.big_q_block_enemy_offset_address, self.big_q_block_enemy_offset)
        rom.write(self.big_q_block_object_set_address, self.big_q_block_object_set)

        rom.write_little_endian(self.toad_warp_level_offset_address, self.toad_warp_level_offset)
        rom.write_little_endian(self.toad_warp_item_address, self.toad_warp_item)

    @property
    def fortress_fx_indexes_start_address(self):
        return FortressFX_W1 + self.fortress_fx_base_index

    @property
    def structure_block_address(self):
        return WORLD_MAP_BASE_OFFSET + self.structure_data_offset

    @structure_block_address.setter
    def structure_block_address(self, value):
        self.structure_data_offset = value - WORLD_MAP_BASE_OFFSET

        # we need to save the level count here, since it's a property of the two attributes we change here
        level_count = self.level_count

        self.y_pos_list_start = self.structure_block_address + MAX_SCREEN_COUNT
        self.x_pos_list_start = self.y_pos_list_start + level_count

        self.enemy_offset_list_offset = self.x_pos_list_start + self.level_count - WORLD_MAP_BASE_OFFSET
        self.level_offset_list_offset = self.enemy_offset_list_offset + self.level_count * OFFSET_SIZE

    @property
    def structure_block_size(self):
        return self.level_count * LevelPointerData.SIZE + len(self.pos_offsets_for_screen)

    @property
    def layout_address(self):
        return WORLD_MAP_BASE_OFFSET + self.tile_data_offset

    @layout_address.setter
    def layout_address(self, value):
        self.tile_data_offset = value - WORLD_MAP_BASE_OFFSET

    @property
    def airship_level_address(self):
        # TODO make object set rom dependent
        return ObjectSet(self.airship_level_object_set).level_offset + self.airship_level_offset

    @airship_level_address.setter
    def airship_level_address(self, value):
        self.airship_level_offset = value - self.airship_level_object_set.level_offset

    @property
    def airship_level_object_set(self):
        return AIR_SHIP_OBJECT_SET

    @property
    def coin_ship_level_address(self):
        # TODO make object set rom dependent
        return ObjectSet(self.coin_ship_level_object_set).level_offset + self.coin_ship_level_offset

    @coin_ship_level_address.setter
    def coin_ship_level_address(self, value):
        self.coin_ship_level_offset = value - ObjectSet(self.coin_ship_level_object_set).level_offset

    @property
    def coin_ship_level_object_set(self):
        return AIR_SHIP_OBJECT_SET

    @property
    def generic_exit_level_address(self):
        # TODO make object set rom dependent
        return ObjectSet(self.generic_exit_object_set).level_offset + self.generic_exit_level_offset

    @generic_exit_level_address.setter
    def generic_exit_level_address(self, value):
        self.generic_exit_level_offset = value - ObjectSet(self.generic_exit_object_set).level_offset

    @property
    def big_q_block_level_address(self):
        # TODO make object set rom dependent
        return ObjectSet(self.big_q_block_object_set).level_offset + self.big_q_block_level_offset

    @big_q_block_level_address.setter
    def big_q_block_level_address(self, value):
        self.big_q_block_level_offset = value - ObjectSet(self.big_q_block_object_set).level_offset

    @property
    def toad_warp_level_address(self):
        return ObjectSet(self.toad_warp_object_set).level_offset + self.toad_warp_level_offset

    @toad_warp_level_address.setter
    def toad_warp_level_address(self, value):
        self.toad_warp_level_offset = value - ObjectSet(self.toad_warp_object_set).level_offset

    @property
    def toad_warp_object_set(self):
        return MUSHROOM_OBJECT_SET

    @property
    def tile_data_size(self):
        return len(self.tile_data) + 1  # the delimiter at the end

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

        self.structure_block_address = self.structure_block_address
