from smb3parse.levels.world_map import WorldMap

BASE_ENEMY_OFFSET = 0x00010
BASE_LEVEL_OFFSET = 0x10010

# in bytes
HEADER_LENGTH = 9

# in blocks
MIN_LENGTH = 0x10
MAX_LENGTH = 0x100
LEVEL_LENGTH_INTERVAL = 0x10

DEFAULT_HORIZONTAL_HEIGHT = 27
DEFAULT_VERTICAL_WIDTH = 16


def is_valid_level_length(level_length: int) -> bool:
    return level_length in range(MIN_LENGTH, MAX_LENGTH + 1, LEVEL_LENGTH_INTERVAL)


class Level:
    def __init__(self, rom, world: WorldMap, screen: int, row: int, column: int):
        self.layout_address, self.enemy_address, self.object_set_index = world.level_for_position(screen, row, column)

        self._rom = rom

        self.header_address = self.layout_address - HEADER_LENGTH

        self.header_bytes = self._rom.read(self.header_address, HEADER_LENGTH)
