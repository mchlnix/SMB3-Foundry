from collections import defaultdict
from typing import Dict, Generator, List, Optional
from warnings import warn

from smb3parse.constants import (
    Map_Y_Starts,
    OFFSET_SIZE,
    SPRITE_COUNT,
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
from smb3parse.data_points import LevelPointerData, Position, SpriteData, WorldMapData
from smb3parse.levels import (
    COMPLETABLE_LIST_END_MARKER,
    COMPLETABLE_TILES_LIST,
    FIRST_VALID_ROW,
    LAYOUT_LIST_OFFSET,
    LevelBase,
    SPECIAL_ENTERABLE_TILES_LIST,
    SPECIAL_ENTERABLE_TILE_AMOUNT,
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
from smb3parse.objects.object_set import WORLD_MAP_OBJECT_SET
from smb3parse.util.rom import Rom

TILE_NAMES: Dict[int, str] = defaultdict(lambda: "NO NAME")
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

Y_START_POS_LIST = Map_Y_Starts


def list_world_map_addresses(rom: Rom) -> List[int]:
    addresses = []

    for world in range(WORLD_COUNT):
        addresses.append(WORLD_MAP_BASE_OFFSET + rom.little_endian(LAYOUT_LIST_OFFSET + OFFSET_SIZE * world))

    return addresses


def get_all_world_maps(rom: Rom) -> List["WorldMap"]:
    world_map_addresses = list_world_map_addresses(rom)

    return [WorldMap(address, rom) for address in world_map_addresses]


def level_name(data: LevelPointerData) -> str:
    if data is None:
        return ""

    tile = data.world.tile_data[data.pos.tile_data_index]

    if not tile_is_enterable(tile, data._rom):
        return "Untitled Level"

    if tile in range(TILE_LEVEL_1, TILE_LEVEL_10 + 1):
        return f"Level {data.world.index + 1}-{tile - TILE_LEVEL_1 + 1}"

    return f"Level {data.world.index + 1}-{TILE_NAMES[tile]}"


def _get_normal_enterable_tiles(rom: Rom) -> bytes:
    return rom.read(TILE_ATTRIBUTES_TS0_OFFSET, 4)


def _get_special_enterable_tiles(rom: Rom) -> bytes:
    return rom.read(SPECIAL_ENTERABLE_TILES_LIST, SPECIAL_ENTERABLE_TILE_AMOUNT)


def _get_completable_tiles(rom: Rom) -> bytearray:
    completable_tile_amount = (
        rom.find(COMPLETABLE_LIST_END_MARKER.to_bytes(1, byteorder="big"), COMPLETABLE_TILES_LIST)
        - COMPLETABLE_TILES_LIST
    )

    return rom.read(COMPLETABLE_TILES_LIST, completable_tile_amount)


def tile_is_enterable(tile_index: int, rom: Rom) -> bool:
    quadrant_index = tile_index >> 6

    return (
        tile_index >= _get_normal_enterable_tiles(rom)[quadrant_index]
        or tile_index in _get_completable_tiles(rom)
        or tile_index in _get_special_enterable_tiles(rom)
    )


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

        self.rom = rom

        memory_addresses = list_world_map_addresses(rom)

        try:
            self.number = memory_addresses.index(layout_address) + 1
        except ValueError:
            raise ValueError(f"World map was not found at given memory address {hex(layout_address)}.")

        self.data = WorldMapData(self.rom, self.world_index)

        self.height = WORLD_MAP_HEIGHT

        if len(self.layout_bytes) % WORLD_MAP_SCREEN_SIZE != 0:
            raise ValueError(
                f"Invalid length of layout bytes for world map ({self.layout_bytes}). "
                f"Should be divisible by {WORLD_MAP_SCREEN_SIZE}."
            )

    @property
    def screen_count(self):
        return len(self.layout_bytes) // WORLD_MAP_SCREEN_SIZE

    @property
    def width(self):
        return int(self.screen_count * WORLD_MAP_SCREEN_WIDTH)

    @property
    def layout_bytes(self):
        return self.data.tile_data

    @layout_bytes.setter
    def layout_bytes(self, value):
        self.data.tile_data = value

    @property
    def world_index(self):
        return self.number - 1

    @property
    def level_count(self):
        return self.data.level_count

    def level_for_position(self, pos: Position) -> Optional[LevelPointerData]:
        """
        The rom takes the position of the current player, the world, the screen and the x and y coordinates, and
        operates on them. First it is checked, whether the player is located on a tile, that can be entered.

        If that is the case, the x and y coordinates are used to look up the object set and address of the level. The
        object set is necessary to find the right base offset for the level address and to correctly parse its object
        data.

        Using the tile information it should be possible to correctly name almost all levels, for example Level *-1 will
        be located in the list at the offset pointed to by the "Level 1" tile in that world.

        That means, that all levels should be able to be collected, by iterating over all possible tiles and following
        the same procedure as the rom.

        :return: A tuple of the object set number, the absolute level address, pointing to the objects and the enemy
        address. Or None, if there is no level at the map position.
        """
        if (level_pointer := self.level_at(pos)) is None:
            return None

        if not 0xA000 <= level_pointer.level_offset < 0xC000:
            # suppose that level layouts are only in this range?
            warn(f"Level in {self}@{pos.screen=}, {pos.row=}, {pos.column=} has offset {level_pointer.level_offset}")

        return level_pointer

    def replace_level_at_position(self, level_info, position: "WorldMapPosition"):
        level_address, enemy_address, object_set_number = level_info

        level_pointer = self.level_for_position(position)

        if level_pointer is None:
            raise LookupError("No existing level at position.")

        level_pointer.object_set = object_set_number
        level_pointer.level_address = level_address
        level_pointer.enemy_address = enemy_address

        level_pointer.write_back()

    def level_name_for_position(self, pos: Position) -> str:
        return level_name(self.level_at(pos))

    def gen_sprites(self) -> Generator[SpriteData, None, None]:
        for index in range(SPRITE_COUNT):
            yield SpriteData(self.data, index)

    def clear_sprites(self):
        for sprite in self.gen_sprites():
            sprite.clear()
            sprite.write_back()

    def sprite_at(self, pos: Position) -> Optional[SpriteData]:
        """
        Returns the ID of the overworld sprite at the given location in this world. Or 0 if there is None.
        """
        for sprite_data in self.gen_sprites():
            if sprite_data.is_at(pos):
                return sprite_data
        else:
            return None

    @property
    def level_pointers(self):
        return self.data.level_pointers

    def clear_level_pointers(self):
        # todo doesn't remove them from the world list, though. need to change amount on screen as well
        for level_pointer in self.level_pointers:
            level_pointer.clear()
            level_pointer.write_back()

    def level_at(self, pos: Position) -> Optional[LevelPointerData]:
        """
        Returns the ID of the overworld sprite at the given location in this world. Or 0 if there is None.
        """
        for level_pointer in self.level_pointers:
            if level_pointer.is_at(pos):
                return level_pointer
        else:
            return None

    def tile_at(self, pos: Position) -> int:
        """
        Returns the tile value at the given coordinates. We define (0, 0) to be the topmost, leftmost tile, under the
        black border, so we'll adjust them accordingly, when bound checking.

        :return:
        """
        if pos.row not in VALID_ROWS:
            raise ValueError(
                f"Given row {pos.row} is outside the valid range for world maps. Allowed are: {VALID_ROWS}."
            )

        if pos.column not in VALID_COLUMNS:
            raise ValueError(
                f"Given column {pos.column} is outside the valid range for world maps. Allowed are {VALID_COLUMNS}"
            )

        if pos.screen not in range(self.screen_count):
            raise ValueError(f"World {self.number} has {self.screen_count} screens. Given number {pos.screen} invalid.")

        return self.layout_bytes[pos.tile_data_index]

    def is_enterable(self, tile_index: int) -> bool:
        """
        The tile attributes for the overworld tile set define the minimal value a tile has to have to be enterable.
        Which of the 4 bytes to check against depends on the "quadrant", so the 2 MSBs.

        :param tile_index: Tile index to check.

        :return: Whether the tile is enterable.
        """
        # todo allows spade houses, but those break. treat them differently when loading their level
        return tile_is_enterable(tile_index)

    @property
    def start_pos(self) -> Optional[WorldMapPosition]:
        if self.world_index == 8:
            # warp world
            return None

        # x coordinate is always the same
        x = 0x20 >> 4

        y_positions_of_world = [self.rom.int(Y_START_POS_LIST + index) >> 4 for index in range(8)]

        y = y_positions_of_world[self.world_index]

        # always on screen 1
        return WorldMapPosition(self, 1, y, x)

    def gen_positions(self) -> Generator["WorldMapPosition", None, None]:
        """
        Returns a generator, which yield WorldMapPosition objects, one screen at a time, one row at a time.
        """
        for screen in range(self.screen_count):
            for row in range(WORLD_MAP_HEIGHT):
                for column in range(WORLD_MAP_SCREEN_WIDTH):
                    yield WorldMapPosition(self, screen, row + FIRST_VALID_ROW, column)

    def save_to_rom(self):
        pass

    @staticmethod
    def from_world_number(rom: Rom, world_number: int) -> "WorldMap":
        if not world_number - 1 in range(WORLD_COUNT):
            raise ValueError(f"World number {world_number - 1} must be between 1 and {WORLD_COUNT}, including.")

        memory_address = list_world_map_addresses(rom)[world_number - 1]

        return WorldMap(memory_address, rom)

    def __repr__(self):
        return f"World {self.number}"
