from typing import List

from smb3parse.levels import LevelBase

OFFSET_SIZE = 2  # byte

BASE_OFFSET = 0xE010
LAYOUT_LIST_OFFSET = BASE_OFFSET + 0xA598
INIT_LIST_OFFSET = BASE_OFFSET + 0xB3CA
LEVEL_Y_POS_LIST_OFFSET = BASE_OFFSET + 0xB3DC
LEVEL_X_POS_LIST_OFFSET = BASE_OFFSET + 0xB3EE
LEVEL_ENEMY_LIST_OFFSET = BASE_OFFSET + 0xB400
LEVEL_LAYOUT_LIST_OFFSET = BASE_OFFSET + 0xB412

WORLD_COUNT = 9  # includes warp zone

WORLD_MAP_HEIGHT = 9  # blocks
WORLD_MAP_SCREEN_WIDTH = 16  # blocks

WORLD_MAP_SCREEN_SIZE = WORLD_MAP_HEIGHT * WORLD_MAP_SCREEN_WIDTH  # bytes


def list_world_map_addresses(rom_bytes: bytearray) -> List[int]:
    offsets = rom_bytes[LAYOUT_LIST_OFFSET : LAYOUT_LIST_OFFSET + WORLD_COUNT * OFFSET_SIZE]

    addresses = []

    for world in range(WORLD_COUNT):
        index = world * 2

        world_map_offset = (offsets[index + 1] << 8) + offsets[index]

        addresses.append(BASE_OFFSET + world_map_offset)

    return addresses


def get_all_world_maps(rom_bytes: bytearray) -> List["WorldMap"]:
    world_map_addresses = list_world_map_addresses(rom_bytes)

    return [WorldMap(address, rom_bytes) for address in world_map_addresses]


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

    def __init__(self, memory_address: int, rom_bytes: bytearray):
        super(WorldMap, self).__init__(memory_address)

        self._height = WORLD_MAP_HEIGHT

        layout_end_index = rom_bytes.find(b"\xFF", memory_address)

        self.layout_bytes = rom_bytes[memory_address:layout_end_index]

        if len(self.layout_bytes) % WORLD_MAP_SCREEN_SIZE != 0:
            raise ValueError(
                f"Invalid length of layout bytes for world map ({self.layout_bytes}). "
                f"Should be divisible by {WORLD_MAP_SCREEN_SIZE}."
            )

        self.screen_count = len(self.layout_bytes) / WORLD_MAP_SCREEN_SIZE
        self._width = int(self.screen_count * WORLD_MAP_SCREEN_WIDTH)

    @staticmethod
    def from_world_number(rom_bytes: bytearray, world_number: int) -> "WorldMap":
        if not world_number - 1 in range(WORLD_COUNT):
            raise ValueError(f"World number must be between 1 and {WORLD_COUNT}, including.")

        memory_address = list_world_map_addresses(rom_bytes)[world_number - 1]

        return WorldMap(memory_address, rom_bytes)
