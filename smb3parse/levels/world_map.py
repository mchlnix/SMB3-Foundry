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

        self._screen_count = len(self.layout_bytes) / WORLD_MAP_SCREEN_SIZE
        self._width = int(self._screen_count * WORLD_MAP_SCREEN_WIDTH)
