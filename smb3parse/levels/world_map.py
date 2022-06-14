from collections import defaultdict
from typing import Generator, List, Optional
from warnings import warn

from smb3parse.constants import (
    MAPITEM_NOITEM,
    MAPOBJ_EMPTY,
    TILE_BOWSER_CASTLE,
    TILE_CASTLE_BOTTOM,
    TILE_DUNGEON_1,
    TILE_DUNGEON_2,
    TILE_HAND_TRAP,
    TILE_LEVEL_1,
    TILE_LEVEL_10,
    TILE_MUSHROOM_HOUSE_1,
    TILE_MUSHROOM_HOUSE_2,
    TILE_PIPE,
    TILE_POND,
    TILE_PYRAMID,
    TILE_QUICKSAND,
    TILE_SPADE_HOUSE,
    TILE_SPIRAL_TOWER_1,
    TILE_SPIRAL_TOWER_2,
    TILE_STAR_1,
    TILE_STAR_2,
)
from smb3parse.levels import (
    BASE_OFFSET,
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
from smb3parse.levels.WorldMapPosition import WorldMapPosition
from smb3parse.levels.level import Level
from smb3parse.objects.object_set import WORLD_MAP_OBJECT_SET
from smb3parse.util.rom import Rom

TILE_NAMES = defaultdict(lambda: "NO NAME")
TILE_NAMES.update(
    {
        TILE_MUSHROOM_HOUSE_1: "Mushroom House",
        TILE_MUSHROOM_HOUSE_2: "Mushroom House",
        TILE_SPIRAL_TOWER_1: "Spiral Tower",
        TILE_SPIRAL_TOWER_2: "Spiral Tower",
        TILE_DUNGEON_1: "Dungeon",
        TILE_DUNGEON_2: "Dungeon",
        TILE_QUICKSAND: "Quicksand",
        TILE_PYRAMID: "Pyramid",
        TILE_PIPE: "Pipe",
        TILE_POND: "Pond",
        TILE_CASTLE_BOTTOM: "Peach's Castle",
        TILE_BOWSER_CASTLE: "Bowser's Lair",
        TILE_HAND_TRAP: "Hand Trap",
        TILE_SPADE_HOUSE: "Spade Bonus",
        TILE_STAR_1: "Star",
        TILE_STAR_2: "Star",
    }
)

MAP_SPRITE_Y_POS_LIST = BASE_OFFSET + 0x16010
MAP_SPRITE_X_POS_SCREEN_LIST = MAP_SPRITE_Y_POS_LIST + 8 * OFFSET_SIZE
MAP_SPRITE_X_POS_LIST = MAP_SPRITE_X_POS_SCREEN_LIST + 8 * OFFSET_SIZE
MAP_SPRITE_IDS_LIST = MAP_SPRITE_X_POS_LIST + 8 * OFFSET_SIZE
MAP_SPRITE_ITEMS_LIST = MAP_SPRITE_IDS_LIST + 8 * OFFSET_SIZE

Y_START_POS_LIST = BASE_OFFSET + 0x3C38A


def list_world_map_addresses(rom: Rom) -> List[int]:
    offsets = rom.read(LAYOUT_LIST_OFFSET, WORLD_COUNT * OFFSET_SIZE)

    addresses = []

    for world in range(WORLD_COUNT):
        index = world * OFFSET_SIZE

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
            self.number = memory_addresses.index(layout_address) + 1
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
        return self.number - 1

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
        The rom takes the position of the current player, the world, the screen and the x and y coordinates, and
        operates on them. First it is checked, whether the player is located on a tile, that is able to enterable.

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

        :return: A tuple of the object set number, the absolute level address, pointing to the objects and the enemy
        address. Or None, if there is no level at the map position.
        """

        tile = self.tile_at(screen, player_row, player_column)

        if tile in [TILE_SPADE_HOUSE, TILE_MUSHROOM_HOUSE_1, TILE_MUSHROOM_HOUSE_2]:
            warn("Spade and mushroom house currently not supported, when getting a level address.")
            return None

        level_indexes = self.level_indexes(screen, player_row, player_column)

        if level_indexes is None:
            return None

        row_address, column_address, level_offset_address, enemy_offset_address = level_indexes

        level_offset = self._rom.little_endian(level_offset_address)

        if not 0xA000 <= level_offset < 0xC000:
            # suppose that level layouts are only in this range?
            warn(f"Level in {self}@{screen=}, {player_row=}, {player_column=} has offset {level_offset}")
            return None

        correct_row_value = self._rom.int(row_address)
        object_set_number = correct_row_value & 0x0F

        object_set_offset = (self._rom.int(OFFSET_BY_OBJECT_SET_A000 + object_set_number) * OFFSET_SIZE - 10) * 0x1000

        absolute_level_address = 0x0010 + object_set_offset + level_offset

        # get enemy address
        enemy_address = ENEMY_BASE_OFFSET + self._rom.little_endian(enemy_offset_address)

        return object_set_number, absolute_level_address, enemy_address

    def replace_level_at_position(self, level_info, position: "WorldMapPosition"):
        level_address, enemy_address, object_set_number = level_info

        existing_level = self.level_for_position(position.screen, position.row, position.column)

        if existing_level is None:
            raise LookupError("No existing level at position.")

        _, screen, row, column = position.tuple()

        row_address, column_address, level_offset_address, enemy_offset_address = self.level_indexes(
            screen, row, column
        )

        row_value = ((row + FIRST_VALID_ROW) << 4) + object_set_number
        self._rom.write(row_address, bytes([row_value]))

        column_value = ((screen - 1) << 4) + column
        self._rom.write(column_address, bytes([column_value]))

        object_set_offset = (self._rom.int(OFFSET_BY_OBJECT_SET_A000 + object_set_number) * OFFSET_SIZE - 10) * 0x1000
        level_offset = level_address - object_set_offset - BASE_OFFSET

        self._rom.write_little_endian(level_offset_address, level_offset)

        enemy_offset = enemy_address - BASE_OFFSET

        self._rom.write_little_endian(enemy_offset_address, enemy_offset)

    def level_indexes(self, player_screen, player_row, player_column):
        """

        :param int player_screen: On which screen the level is positioned, 1, 2, 3 or 4.
        :param int player_row: In which row the level is positioned.
        :param int player_column: In which column the level is positioned.

        :return: The memory addresses of the row, column and level offset position.
        """

        level_y_pos_list_start = WORLD_MAP_BASE_OFFSET + self._rom.little_endian(
            LEVEL_Y_POS_LISTS + OFFSET_SIZE * self.world_index
        )

        level_x_pos_list_start = WORLD_MAP_BASE_OFFSET + self._rom.little_endian(
            LEVEL_X_POS_LISTS + OFFSET_SIZE * self.world_index
        )

        level_amount = level_x_pos_list_start - level_y_pos_list_start

        # go through the row and column pairs for all levels in this world
        for coord_index in range(level_amount):
            # get row value first
            row_address = level_y_pos_list_start + coord_index
            row_value = self._rom.int(row_address)

            # adjust the value, and ignore the black border tiles around the map
            row = (row_value >> 4) - FIRST_VALID_ROW

            if row != player_row:
                continue

            # if it matches, get the corresponding column value next
            column_address = level_x_pos_list_start + coord_index
            col_value = self._rom.int(column_address)

            # left 4 bits are the 0-indexed screen number, the right bits are the column
            screen = (col_value >> 4) + 1
            column = col_value & 0x0F

            if column == player_column and screen == player_screen:
                # found our match
                break
        else:
            # no level at given coordinates
            return None

        # get level offset
        level_list_offset_position = LEVELS_IN_WORLD_LIST_OFFSET + self.world_index * OFFSET_SIZE
        level_list_address = WORLD_MAP_BASE_OFFSET + self._rom.little_endian(level_list_offset_position)

        level_offset_position = level_list_address + OFFSET_SIZE * coord_index

        enemy_list_start_offset = LEVEL_ENEMY_LIST_OFFSET + self.world_index * OFFSET_SIZE
        enemy_list_start = WORLD_MAP_BASE_OFFSET + self._rom.little_endian(enemy_list_start_offset)

        enemy_offset_position = enemy_list_start + coord_index * OFFSET_SIZE

        # return the addresses of the row and column value, so we can overwrite them, if necessary
        return row_address, column_address, level_offset_position, enemy_offset_position

    def level_name_for_position(self, screen: int, player_row: int, player_column: int) -> str:
        tile = self.tile_at(screen, player_row, player_column)

        if not self.is_enterable(tile):
            return ""

        if tile in range(TILE_LEVEL_1, TILE_LEVEL_10 + 1):
            return f"Level {self.number}-{tile - TILE_LEVEL_1 + 1}"

        return f"Level {self.number}-{TILE_NAMES[tile]}"

    def sprite_at(self, screen: int, row: int, column: int) -> tuple[int, int]:
        """
        Returns the ID of the overworld sprite at the given location in this world. Or 0 if there is None.

        :param screen:
        :param row:
        :param column:
        """
        y_pos_offset_for_world = self._rom.little_endian(MAP_SPRITE_Y_POS_LIST + self.world_index * OFFSET_SIZE)
        y_pos_address_for_world = BASE_OFFSET + 0xC000 + y_pos_offset_for_world

        x_pos_screen_offset_for_world = self._rom.little_endian(
            MAP_SPRITE_X_POS_SCREEN_LIST + self.world_index * OFFSET_SIZE
        )
        x_pos_screen_address_for_world = BASE_OFFSET + 0xC000 + x_pos_screen_offset_for_world

        x_pos_offset_for_world = self._rom.little_endian(MAP_SPRITE_X_POS_LIST + self.world_index * OFFSET_SIZE)
        x_pos_address_for_world = BASE_OFFSET + 0xC000 + x_pos_offset_for_world

        ids_offset_for_world = self._rom.little_endian(MAP_SPRITE_IDS_LIST + self.world_index * OFFSET_SIZE)
        ids_address_for_world = BASE_OFFSET + 0xC000 + ids_offset_for_world

        item_offset_for_world = self._rom.little_endian(MAP_SPRITE_ITEMS_LIST + self.world_index * OFFSET_SIZE)
        item_address_for_world = BASE_OFFSET + 0xC000 + item_offset_for_world

        y_pos_for_world = [(self._rom.int(y_pos_address_for_world + index) >> 4) for index in range(9)]

        x_pos_screen_for_world = [self._rom.int(x_pos_screen_address_for_world + index) for index in range(9)]
        x_pos_for_world = [self._rom.int(x_pos_address_for_world + index) >> 4 for index in range(9)]

        ids_for_world = [self._rom.int(ids_address_for_world + index) for index in range(9)]
        items_for_world = [self._rom.int(item_address_for_world + index) for index in range(9)]

        for index, y_pos in enumerate(y_pos_for_world):
            if y_pos - FIRST_VALID_ROW != row:
                continue

            if x_pos_screen_for_world[index] != screen - 1:
                continue

            x_pos = x_pos_for_world[index]

            if x_pos == y_pos == 0:
                continue

            if x_pos == column:
                return ids_for_world[index], items_for_world[index]

        return MAPOBJ_EMPTY, MAPITEM_NOITEM

    def tile_at(self, screen: int, row: int, column: int) -> int:
        """
        Returns the tile value at the given coordinates. We define (0, 0) to be the topmost, leftmost tile, under the
        black border, so we'll adjust them accordingly, when bound checking.

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
            raise ValueError(f"World {self.number} has {self.screen_count} screens. " f"Given number {screen} invalid.")

        return self.layout_bytes[(screen - 1) * WORLD_MAP_SCREEN_SIZE + row * WORLD_MAP_SCREEN_WIDTH + column]

    def is_enterable(self, tile_index: int) -> bool:
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

    @property
    def start_pos(self) -> Optional[WorldMapPosition]:
        if self.world_index == 8:
            # warp world
            return None

        # x coordinate is always the same
        x = 0x20 >> 4

        y_positions_of_world = [self._rom.int(Y_START_POS_LIST + index) >> 4 for index in range(8)]

        y = y_positions_of_world[self.world_index] - FIRST_VALID_ROW

        # always on screen 1
        return WorldMapPosition(self, 1, y, x)

    def gen_positions(self) -> Generator["WorldMapPosition", None, None]:
        """
        Returns a generator, which yield WorldMapPosition objects, one screen at a time, one row at a time.
        """
        for screen in range(1, self.screen_count + 1):
            for row in range(WORLD_MAP_HEIGHT):
                for column in range(WORLD_MAP_SCREEN_WIDTH):
                    yield WorldMapPosition(self, screen, row, column)

    def gen_levels(self):
        """
        Returns a generator, which yields all levels accessible from this world map.
        """
        for position in self.gen_positions():
            level_info_tuple = self.level_for_position(position.screen, position.row, position.column)

            if level_info_tuple is None:
                continue

            else:
                yield Level(self._rom, *level_info_tuple)

    def gen_sprites(self):
        for position in self.gen_positions():
            if not position.has_sprite():
                continue

            yield position

    @staticmethod
    def from_world_number(rom: Rom, world_number: int) -> "WorldMap":
        if not world_number - 1 in range(WORLD_COUNT):
            raise ValueError(f"World number must be between 1 and {WORLD_COUNT}, including.")

        memory_address = list_world_map_addresses(rom)[world_number - 1]

        return WorldMap(memory_address, rom)

    def __repr__(self):
        return f"World {self.number}"


def _get_normal_enterable_tiles(rom: Rom) -> bytearray:
    return rom.read(TILE_ATTRIBUTES_TS0_OFFSET, 4)


def _get_special_enterable_tiles(rom: Rom) -> bytearray:
    return rom.read(SPECIAL_ENTERABLE_TILES_LIST, SPECIAL_ENTERABLE_TILE_AMOUNT)


def _get_completable_tiles(rom: Rom) -> bytearray:
    completable_tile_amount = rom.find(COMPLETABLE_LIST_END_MARKER, COMPLETABLE_TILES_LIST) - COMPLETABLE_TILES_LIST

    return rom.read(COMPLETABLE_TILES_LIST, completable_tile_amount)
