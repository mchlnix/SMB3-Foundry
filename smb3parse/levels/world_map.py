from typing import List

from smb3parse.levels import (
    COMPLETABLE_LIST_END_MARKER,
    COMPLETABLE_TILES_LIST,
    ENEMY_BASE_OFFSET,
    FIRST_VALID_ROW,
    LAYOUT_LIST_OFFSET,
    LEVELS_IN_WORLD_LIST_OFFSET,
    LEVEL_ENEMY_LIST_OFFSET,
    LEVEL_X_POS_LISTS,
    LEVEL_Y_POS_LISTS,
    LevelBase,
    OFFSET_BY_OBJECT_SET_A000,
    OFFSET_SIZE,
    SPECIAL_ENTERABLE_TILES_LIST,
    SPECIAL_ENTERABLE_TILE_AMOUNT,
    STRUCTURE_DATA_OFFSETS,
    TILE_ATTRIBUTES_TS0_OFFSET,
    VALID_COLUMNS,
    VALID_ROWS,
    WORLD_COUNT,
    WORLD_MAP_BASE_OFFSET,
    WORLD_MAP_HEIGHT,
    WORLD_MAP_SCREEN_SIZE,
    WORLD_MAP_SCREEN_WIDTH,
)
from smb3parse.objects.object_set import WORLD_MAP_OBJECT_SET
from smb3parse.util.rom import Rom


def list_world_map_addresses(rom: Rom) -> List[int]:
    offsets = rom.read(LAYOUT_LIST_OFFSET, WORLD_COUNT * OFFSET_SIZE)

    addresses = []

    for world in range(WORLD_COUNT):
        index = world * 2

        world_map_offset = (offsets[index + 1] << 8) + offsets[index]

        addresses.append(WORLD_MAP_BASE_OFFSET + world_map_offset)

    return addresses


def get_all_world_maps(rom: Rom) -> List["WorldMap"]:
    world_map_addresses = list_world_map_addresses(rom)

    return [WorldMap(address, rom) for address in world_map_addresses]


class WorldMap(LevelBase):
    """
    Represents the data associated with a world map/overworld. World maps are always 9 blocks high and 16 blocks wide.
    They can be multiple screens big, which are either not visibly connected or connected horizontally.

    Attributes:
        layout_address  The position in the ROM of the bytes making up the visual layout of the world map.
        layout_bytes    The actual bytes making up the visual layout

        width           The width of the world map in blocks across all scenes.
        height          The height of the world map, always 9 blocks.

        object_set      An ObjectSet object for the world map object set.
        screen_count    How many screens this world map spans.
    """

    def __init__(self, layout_address: int, rom: Rom):
        super(WorldMap, self).__init__(WORLD_MAP_OBJECT_SET, layout_address)

        self._rom = rom

        self._minimal_enterable_tiles = _get_normal_enterable_tiles(self._rom)
        self._special_enterable_tiles = _get_special_enterable_tiles(self._rom)
        self._completable_tiles = _get_completable_tiles(self._rom)

        memory_addresses = list_world_map_addresses(rom)

        try:
            self.world_number = memory_addresses.index(layout_address) + 1
        except ValueError:
            raise ValueError(f"World map was not found at given memory address {hex(layout_address)}.")

        self.height = WORLD_MAP_HEIGHT

        layout_end_index = rom.find(b"\xFF", layout_address)

        self.layout_bytes = rom.read(layout_address, layout_end_index - layout_address)

        if len(self.layout_bytes) % WORLD_MAP_SCREEN_SIZE != 0:
            raise ValueError(
                f"Invalid length of layout bytes for world map ({self.layout_bytes}). "
                f"Should be divisible by {WORLD_MAP_SCREEN_SIZE}."
            )

        self.screen_count = len(self.layout_bytes) // WORLD_MAP_SCREEN_SIZE
        self.width = int(self.screen_count * WORLD_MAP_SCREEN_WIDTH)

        self._parse_structure_data_block(rom)

    @property
    def world_index(self):
        return self.world_number - 1

    @property
    def level_count(self):
        return self.level_count_s1 + self.level_count_s2 + self.level_count_s3 + self.level_count_s4

    def _parse_structure_data_block(self, rom: Rom):
        structure_block_offset = rom.little_endian(STRUCTURE_DATA_OFFSETS + OFFSET_SIZE * self.world_index)

        self.structure_block_start = WORLD_MAP_BASE_OFFSET + structure_block_offset

        # the indexes into the y_pos list, where the levels for the n-th screen start
        y_pos_start_by_screen = rom.read(self.structure_block_start, 4)

        level_y_pos_list_start = WORLD_MAP_BASE_OFFSET + rom.little_endian(
            LEVEL_Y_POS_LISTS + OFFSET_SIZE * self.world_index
        )

        level_x_pos_list_start = WORLD_MAP_BASE_OFFSET + rom.little_endian(
            LEVEL_X_POS_LISTS + OFFSET_SIZE * self.world_index
        )

        level_y_pos_list_end = level_x_pos_list_start - level_y_pos_list_start

        self.level_count_s1 = y_pos_start_by_screen[1] - y_pos_start_by_screen[0]
        self.level_count_s2 = y_pos_start_by_screen[2] - y_pos_start_by_screen[1]
        self.level_count_s3 = y_pos_start_by_screen[3] - y_pos_start_by_screen[2]
        self.level_count_s4 = level_y_pos_list_end - y_pos_start_by_screen[3]

    def level_for_position(self, screen: int, player_row: int, player_column: int):
        """
        The rom takes the position of the current player, so the world, the screen and the x and y coordinates, and
        operates on them. First it is checked, whether or not the player is located on a tile, that is able to be
        entered.

        If that is the case, the x and y coordinates are used to look up the object set and address of the level. The
        object set is necessary to find the right base offset for the level address and to correctly parse its object
        data.

        Using the tile information it should be possible to correctly name almost all levels, for example Level *-1 will
        be located in the list at the offset pointed to by the "Level 1" tile in that world.

        That means, that all levels should be able to be collected, by iterating over all possible tiles and following
        the same procedure as the rom.

        :param screen:
        :param player_row:
        :param player_column:

        :return: A tuple of the absolute level address, pointing to the objects, enemy address and the object set. Or
            None, if there is no level at the map position.
        """

        tile = self._map_tile_for_position(screen, player_row, player_column)

        if not self._is_enterable(tile):
            return None

        level_y_pos_list_start = WORLD_MAP_BASE_OFFSET + self._rom.little_endian(
            LEVEL_Y_POS_LISTS + OFFSET_SIZE * self.world_index
        )

        level_x_pos_list_start = WORLD_MAP_BASE_OFFSET + self._rom.little_endian(
            LEVEL_X_POS_LISTS + OFFSET_SIZE * self.world_index
        )

        row_amount = col_amount = level_x_pos_list_start - level_y_pos_list_start

        row_start_index = sum(
            [self.level_count_s1, self.level_count_s2, self.level_count_s3, self.level_count_s4][0 : screen - 1]
        )

        # find the row position
        for row_index in range(row_start_index, row_amount):
            value = self._rom.int(level_y_pos_list_start + row_index)

            # adjust the value, so that we ignore the black border tiles around the map
            row = (value >> 4) - FIRST_VALID_ROW

            if row == player_row:
                break
        else:
            # no level on row of player
            return None

        for col_index in range(row_index, col_amount):
            column = self._rom.int(level_x_pos_list_start + col_index) & 0x0F

            if column == player_column:
                break
        else:
            # no column for row
            return None

        level_index = col_index

        # get level offset
        level_list_offset_position = LEVELS_IN_WORLD_LIST_OFFSET + self.world_index * OFFSET_SIZE

        level_list_address = WORLD_MAP_BASE_OFFSET + self._rom.little_endian(level_list_offset_position)

        level_offset = self._rom.little_endian(level_list_address + OFFSET_SIZE * level_index)

        assert 0xA000 <= level_offset < 0xC000  # suppose that level layouts are only in this range?

        # get object set offset

        # the object set is part of the row, but we didn't have the correct row index before, only the first match
        correct_row_value = self._rom.int(level_y_pos_list_start + level_index)
        object_set_number = correct_row_value & 0x0F

        object_set_offset = (self._rom.int(OFFSET_BY_OBJECT_SET_A000 + object_set_number) * 2 - 10) * 0x1000

        absolute_level_address = 0x0010 + object_set_offset + level_offset

        # get enemy address

        enemy_list_start_offset = LEVEL_ENEMY_LIST_OFFSET + self.world_index * OFFSET_SIZE

        enemy_list_start = WORLD_MAP_BASE_OFFSET + self._rom.little_endian(enemy_list_start_offset)

        enemy_address = ENEMY_BASE_OFFSET + self._rom.little_endian(enemy_list_start + level_index * OFFSET_SIZE)

        return object_set_number, absolute_level_address, enemy_address

    def _map_tile_for_position(self, screen: int, row: int, column: int) -> int:
        """
        Returns the tile value at the given coordinates. We (0, 0) to be the topmost, leftmost tile, under the black
        border, so we'll adjust them accordingly, when bound checking.

        :param screen:
        :param row:
        :param column:
        :return:
        """
        if row + FIRST_VALID_ROW not in VALID_ROWS:
            raise ValueError(
                f"Given row {row} is outside the valid range for world maps. First valid row is " f"{FIRST_VALID_ROW}."
            )

        if column not in VALID_COLUMNS:
            raise ValueError(
                f"Given column {column} is outside the valid range for world maps. Remember the black " f"border."
            )

        if screen - 1 not in range(self.screen_count):
            raise ValueError(
                f"World {self.world_number} has {self.screen_count} screens. " f"Given number {screen} invalid."
            )

        return self.layout_bytes[(screen - 1) * WORLD_MAP_SCREEN_SIZE + row * WORLD_MAP_SCREEN_WIDTH + column]

    def _is_enterable(self, tile_index: int) -> bool:
        """
        The tile attributes for the overworld tile set define the minimal value a tile has to have to be enterable.
        Which of the 4 bytes to check against depends on the "quadrant", so the 2 MSBs.

        :param tile_index: Tile index to check.

        :return: Whether the tile is enterable.
        """
        quadrant_index = tile_index >> 6

        # todo allows spade houses, but those break. treat them differently when loading their level
        return (
            tile_index >= self._minimal_enterable_tiles[quadrant_index]
            or tile_index in self._completable_tiles
            or tile_index in self._special_enterable_tiles
        )

    @staticmethod
    def from_world_number(rom: Rom, world_number: int) -> "WorldMap":
        if not world_number - 1 in range(WORLD_COUNT):
            raise ValueError(f"World number must be between 1 and {WORLD_COUNT}, including.")

        memory_address = list_world_map_addresses(rom)[world_number - 1]

        return WorldMap(memory_address, rom)


class WorldMapPosition:
    def __init__(self, world: WorldMap, screen: int, row: int, column: int):
        self.world = world
        self.screen = screen
        self.row = row
        self.column = column

    @property
    def level_info(self):
        return self.world.level_for_position(self.screen, self.row, self.column)


def _get_normal_enterable_tiles(rom: Rom) -> bytearray:
    return rom.read(TILE_ATTRIBUTES_TS0_OFFSET, 4)


def _get_special_enterable_tiles(rom: Rom) -> bytearray:
    return rom.read(SPECIAL_ENTERABLE_TILES_LIST, SPECIAL_ENTERABLE_TILE_AMOUNT)


def _get_completable_tiles(rom: Rom) -> bytearray:
    completable_tile_amount = rom.find(COMPLETABLE_LIST_END_MARKER, COMPLETABLE_TILES_LIST) - COMPLETABLE_TILES_LIST - 1

    return rom.read(COMPLETABLE_TILES_LIST, completable_tile_amount)
