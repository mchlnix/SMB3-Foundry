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


class LevelBase:
    def __init__(self, memory_address: int):
        self._memory_address = memory_address

        self._width: int = 0
        self._height: int = 0

        self._object_set_index: int = 0
