from smb3parse.levels import LevelBase

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


class Level(LevelBase):
    def __init__(self, memory_address):
        super(Level, self).__init__(memory_address)
