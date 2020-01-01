from smb3parse.objects.object_set import ObjectSet

OFFSET_SIZE = 2  # byte

BASE_OFFSET = 0x10  # the size of the rom header identifying the rom

ENEMY_BASE_OFFSET = BASE_OFFSET  # + 1
"""
One additional byte, at the beginning of every enemy data, where I don't know what does
"""

UNKNOWN_OFFSET = BASE_OFFSET + 0x8000  # offset used for uncategorized stuff. TODO find a name

WORLD_MAP_BASE_OFFSET = BASE_OFFSET + 0xE000
"""
Offset for a lot of world related parsing.
"""

LEVEL_BASE_OFFSET = BASE_OFFSET + 0x10000
"""
Offset for level related parsing. Currently only used in Header.
"""

LAYOUT_LIST_OFFSET = WORLD_MAP_BASE_OFFSET + 0xA598

TILE_ATTRIBUTES_TS0_OFFSET = WORLD_MAP_BASE_OFFSET + 0xA400
"""
The first 4 bytes describe minimal indexes an overworld tile must have to be enterable.
"""

STRUCTURE_DATA_OFFSETS = WORLD_MAP_BASE_OFFSET + 0xB3CA  # Map_ByXHi_InitIndex
"""
This lists the start of a block of world meta data. 9 worlds means 9 times 2 bytes of offsets. The block starts with a
0x00, so that also marks the end of the block before it.
"""

LEVEL_Y_POS_LISTS = WORLD_MAP_BASE_OFFSET + 0xB3DC  # Map_ByRowType
"""
This list contains the offsets to the y positions/row indexes of the levels of a world map. Since world maps can have up
to 4 screens, the offset could points to 4 consecutive lists, so we need to know the amount of levels per screen, to
make sense of them.
"""

LEVEL_X_POS_LISTS = WORLD_MAP_BASE_OFFSET + 0xB3EE  # Map_ByScrCol
"""
This list contains the offsets to the x positions/column indexes of the levels in a world map. They are listed in a row
for all 4 screens.
"""

LEVEL_ENEMY_LIST_OFFSET = WORLD_MAP_BASE_OFFSET + 0xB400
"""
"""

LEVELS_IN_WORLD_LIST_OFFSET = WORLD_MAP_BASE_OFFSET + 0xB412
"""
The memory locations of levels inside a world map are listed in a row. This offset points to the memory locations of
these lists for every world. The first 2 bytes following this offset point to the levels in world 1, the next 2 for
world 2 etc.
"""

OFFSET_BY_OBJECT_SET_A000 = BASE_OFFSET + 0x34000 + 0x83E9  # PAGE_A000_ByTileset
"""
A list of values, which specify which ROM page should be loaded into addresses 0xA000 - 0xBFFF for a given object set.
This is necessary, since the ROM is larger then the addressable RAM in the NES. The offsets of levels are always into
the RAM, which means, to address levels at different parts in the ROM these parts need to be loaded into the RAM first.
"""

OFFSET_BY_OBJECT_SET_C000 = BASE_OFFSET + 0x34000 + 0x83D6  # PAGE_C000_ByTileset
"""
Same with the ROM page and addresses 0xC000 - 0xFFFF.
"""

WORLD_COUNT = 9  # includes warp zone

WORLD_MAP_HEIGHT = 9  # blocks
WORLD_MAP_SCREEN_WIDTH = 16  # blocks

FIRST_VALID_ROW = 2
"""
Tiles in rows before this one are part of the border and not valid overworld tiles.
"""

VALID_ROWS = range(FIRST_VALID_ROW, FIRST_VALID_ROW + WORLD_MAP_HEIGHT)
"""
A range of row values, where Mario could possibly stand.
"""

VALID_COLUMNS = range(WORLD_MAP_SCREEN_WIDTH)
"""
A range of column values, where Mario could possibly stand.
"""

COMPLETABLE_TILES_LIST = WORLD_MAP_BASE_OFFSET + 0xA447  # Map_Completable_Tiles
"""
A list of tile values, that are completable, like the Toad House.
"""

COMPLETABLE_LIST_END_MARKER = 0x00  # MCT_END
"""
A value, that specifies the end of the completable tiles, rather than a set address.
"""

SPECIAL_ENTERABLE_TILES_LIST = UNKNOWN_OFFSET + 0xCDAF  # Map_EnterSpecialTiles
"""
A list of tile values, that are also enterable, like the castle and the toad house.
"""

SPECIAL_ENTERABLE_TILE_AMOUNT = 11  # the rom mistakenly uses 0x1A

WORLD_MAP_SCREEN_SIZE = WORLD_MAP_HEIGHT * WORLD_MAP_SCREEN_WIDTH  # bytes

# in bytes
HEADER_LENGTH = 9

# in blocks
LEVEL_MIN_LENGTH = 0x10
LEVEL_MAX_LENGTH = 0x100
LEVEL_LENGTH_INTERVAL = 0x10

DEFAULT_HORIZONTAL_HEIGHT = 27
DEFAULT_VERTICAL_WIDTH = 16


def is_valid_level_length(level_length: int) -> bool:
    return level_length in range(LEVEL_MIN_LENGTH, LEVEL_MAX_LENGTH + 1, LEVEL_LENGTH_INTERVAL)


class LevelBase:
    def __init__(self, memory_address: int):
        self.memory_address = memory_address

        self.width: int = 0
        self.height: int = 0

        self.object_set_index: int = 0
        self.object_set = ObjectSet(self.object_set_index)
