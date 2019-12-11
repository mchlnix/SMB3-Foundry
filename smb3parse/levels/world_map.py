from typing import List

from smb3parse.levels import LevelBase
from smb3parse.util import little_endian
from util.rom import Rom

OFFSET_SIZE = 2  # byte

BASE_OFFSET = 0xE010
LAYOUT_LIST_OFFSET = BASE_OFFSET + 0xA598

"""
This lists the start of a block of world meta data. 9 worlds means 9 times 2 bytes of offsets. The block starts with a
0x00, so that also marks the end of the block before it.
"""
STRUCTURE_DATA_OFFSETS = BASE_OFFSET + 0xB3CA  # Map_ByXHi_InitIndex

"""
This list contains the offsets to the y positions/row indexes of the levels of a world map. Since world maps can have up
to 4 screens, the offset could points to 4 consecutive lists, so we need to know the amount of levels per screen, to
make sense of them.
"""
LEVEL_Y_POS_LISTS = BASE_OFFSET + 0xB3DC  # Map_ByRowType

"""
This list contains the offsets to the x positions/column indexes of the levels in a world map. They are listed in a row
for all 4 screens.
"""
LEVEL_X_POS_LISTS = BASE_OFFSET + 0xB3EE  # Map_ByScrCol

"""

"""
LEVEL_ENEMY_LIST_OFFSET = BASE_OFFSET + 0xB400

"""
The memory locations of levels inside a world map are listed in a row. This offset points to the memory locations of
these lists for every world. The first 2 bytes following this offset point to the levels in world 1, the next 2 for
world 2 etc.
"""
LEVELS_IN_WORLD_LIST_OFFSET = BASE_OFFSET + 0xB412

WORLD_COUNT = 9  # includes warp zone

WORLD_MAP_HEIGHT = 9  # blocks
WORLD_MAP_SCREEN_WIDTH = 16  # blocks

WORLD_MAP_SCREEN_SIZE = WORLD_MAP_HEIGHT * WORLD_MAP_SCREEN_WIDTH  # bytes


def list_world_map_addresses(rom: Rom) -> List[int]:
    offsets = rom.read(LAYOUT_LIST_OFFSET, WORLD_COUNT * OFFSET_SIZE)

    addresses = []

    for world in range(WORLD_COUNT):
        index = world * 2

        world_map_offset = (offsets[index + 1] << 8) + offsets[index]

        addresses.append(BASE_OFFSET + world_map_offset)

    return addresses


def get_all_world_maps(rom: Rom) -> List["WorldMap"]:
    world_map_addresses = list_world_map_addresses(rom)

    return [WorldMap(address, rom) for address in world_map_addresses]


class WorldMap(LevelBase):
    """
    Represents the data associated with a world map/overworld. World maps are always 9 blocks high and 16 blocks wide.
    They can be multiple screens big, which are either not visibly connected or connected horizontally.

    Attributes:
        memory_address  The position in the ROM of the bytes making up the visual layout of the world map.
        layout_bytes    The actual bytes making up the visual layout

        width           The width of the world map in blocks across all scenes.
        height          The height of the world map, always 9 blocks.

        object_set      An ObjectSet object for the world map object set.
        screen_count    How many screens this world map spans.
    """

    def __init__(self, memory_address: int, rom: Rom):
        super(WorldMap, self).__init__(memory_address)

        self._rom = rom

        memory_addresses = list_world_map_addresses(rom)

        try:
            self.world_number = memory_addresses.index(memory_address) + 1
        except ValueError:
            raise ValueError(f"World map was not found at given memory address {hex(memory_address)}.")

        self._height = WORLD_MAP_HEIGHT

        layout_end_index = rom.find(b"\xFF", memory_address)

        self.layout_bytes = rom.read(memory_address, layout_end_index - memory_address)

        if len(self.layout_bytes) % WORLD_MAP_SCREEN_SIZE != 0:
            raise ValueError(
                f"Invalid length of layout bytes for world map ({self.layout_bytes}). "
                f"Should be divisible by {WORLD_MAP_SCREEN_SIZE}."
            )

        self.screen_count = len(self.layout_bytes) / WORLD_MAP_SCREEN_SIZE
        self._width = int(self.screen_count * WORLD_MAP_SCREEN_WIDTH)

        self._parse_structure_data_block(rom)

    @property
    def world_index(self):
        return self.world_number - 1

    @property
    def level_count(self):
        return self.level_count_s1 + self.level_count_s2 + self.level_count_s3 + self.level_count_s4

    def _parse_structure_data_block(self, rom: Rom):
        structure_block_offset = rom.little_endian(STRUCTURE_DATA_OFFSETS + OFFSET_SIZE * self.world_index)

        self.structure_block_start = BASE_OFFSET + structure_block_offset

        # the indexes into the y_pos list, where the levels for the n-th screen start
        y_pos_start_by_screen = rom.read(self.structure_block_start, 4)

        level_y_pos_list_start = BASE_OFFSET + rom.little_endian(LEVEL_Y_POS_LISTS + OFFSET_SIZE * self.world_index)

        level_x_pos_list_start = BASE_OFFSET + rom.little_endian(LEVEL_X_POS_LISTS + OFFSET_SIZE * self.world_index)

        level_y_pos_list_end = level_x_pos_list_start - level_y_pos_list_start

        self.level_count_s1 = y_pos_start_by_screen[1] - y_pos_start_by_screen[0]
        self.level_count_s2 = y_pos_start_by_screen[2] - y_pos_start_by_screen[1]
        self.level_count_s3 = y_pos_start_by_screen[3] - y_pos_start_by_screen[2]
        self.level_count_s4 = level_y_pos_list_end - y_pos_start_by_screen[3]

    def _get_level_addresses(self, rom_bytes: bytearray):
        # get the offset of the level list for this world
        level_list_offset_position = LEVELS_IN_WORLD_LIST_OFFSET + self.world_index * OFFSET_SIZE

        level_list_offset = little_endian(
            rom_bytes[level_list_offset_position : level_list_offset_position + OFFSET_SIZE]
        )

        level_list_address = BASE_OFFSET + level_list_offset

        level_offsets = rom_bytes[level_list_address : level_list_address + OFFSET_SIZE * self.level_count]

    @staticmethod
    def from_world_number(rom: Rom, world_number: int) -> "WorldMap":
        if not world_number - 1 in range(WORLD_COUNT):
            raise ValueError(f"World number must be between 1 and {WORLD_COUNT}, including.")

        memory_address = list_world_map_addresses(rom)[world_number - 1]

        return WorldMap(memory_address, rom)
