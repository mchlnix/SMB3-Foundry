from abc import ABC

from smb3parse.constants import BASE_OFFSET
from smb3parse.objects.object_set import ObjectSet

ENEMY_BASE_OFFSET = BASE_OFFSET  # + 1
"""
One additional byte, at the beginning of every enemy data, where I don't know what does
"""

WORLD_MAP_BASE_OFFSET = BASE_OFFSET + 0xE000
"""
Offset for a lot of world related parsing.
"""

WORLD_COUNT = 9  # includes warp zone

WORLD_MAP_PALETTE_COUNT = 8

WORLD_MAP_HEIGHT = 9  # blocks
WORLD_MAP_SCREEN_WIDTH = 16  # blocks

LEVEL_SCREEN_HEIGHT = 15  # blocks
LEVEL_SCREEN_WIDTH = 16  # blocks

WORLD_MAP_BORDER_TOP_TILE_ID = 0x4E
WORLD_MAP_BLANK_TILE_ID = 0xFE

MAX_SCREEN_COUNT = 4

FIRST_VALID_ROW = 2

NO_MAP_SCROLLING = 0x10

"""
Tiles in rows before this one are part of the border and not valid overworld tiles.
"""

LAST_VALID_ROW = FIRST_VALID_ROW + WORLD_MAP_HEIGHT - 1
"""
Position of last visible row of the overworld.
"""

VALID_ROWS = range(FIRST_VALID_ROW, LAST_VALID_ROW + 1)
"""
A range of row values, where Mario could possibly stand.
"""

VALID_COLUMNS = range(WORLD_MAP_SCREEN_WIDTH)
"""
A range of column values, where Mario could possibly stand.
"""

COMPLETABLE_LIST_END_MARKER = 0x00  # MCT_END
"""
A value, that specifies the end of the completable tiles, rather than a set address.
"""

SPECIAL_ENTERABLE_TILE_AMOUNT = 11  # the rom mistakenly uses 0x1A

WORLD_MAP_SCREEN_SIZE = WORLD_MAP_HEIGHT * WORLD_MAP_SCREEN_WIDTH  # bytes

WORLD_MAP_WARP_WORLD_INDEX = 8
"""The 0-based index of the warp world."""

# in bytes
HEADER_LENGTH = 9

# in blocks
LEVEL_MIN_LENGTH = 0x10
LEVEL_MAX_LENGTH = 0x100
LEVEL_LENGTH_INTERVAL = 0x10

DEFAULT_HORIZONTAL_HEIGHT = 27
DEFAULT_VERTICAL_WIDTH = 16

WORLD_MAP_LAYOUT_DELIMITER = b"\xFF"


def is_valid_level_length(level_length: int) -> bool:
    return level_length in range(LEVEL_MIN_LENGTH, LEVEL_MAX_LENGTH + 1, LEVEL_LENGTH_INTERVAL)


class LevelBase(ABC):
    width: int
    height: int

    def __init__(self, object_set: ObjectSet, layout_address: int):
        self.layout_address = layout_address

        self.object_set = object_set
        self.object_set_number = object_set.number

    def point_in(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height
