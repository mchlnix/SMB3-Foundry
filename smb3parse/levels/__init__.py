from abc import ABC

from foundry.core.util import ROM_HEADER_OFFSET, WORLD_MAP_HEIGHT, SCREEN_WIDTH, LEVEL_MIN_LENGTH, LEVEL_MAX_LENGTH, \
    LEVEL_PARTITION_LENGTH
from smb3parse.objects.object_set import ObjectSet

OFFSET_SIZE = 2  # byte

ENEMY_BASE_OFFSET = ROM_HEADER_OFFSET  # + 1
"""
One additional byte, at the beginning of every enemy data, where I don't know what does
"""

UNKNOWN_OFFSET = ROM_HEADER_OFFSET + 0x8000  # offset used for uncategorized stuff. TODO find a name

WORLD_DATA_OFFSET = ROM_HEADER_OFFSET + 0xE000
"""
Offset for a lot of world related parsing.
"""

"""
Offset for level related parsing. Currently only used in Header.
"""

LAYOUT_LIST_OFFSET = WORLD_DATA_OFFSET + 0xA598

WORLD_BLOCK_ATTRIBUTES_OFFSET = WORLD_DATA_OFFSET + 0xA400
"""
The first 4 bytes describe minimal indexes an overworld tile must have to be enterable.
"""

STRUCTURE_DATA_OFFSETS = WORLD_DATA_OFFSET + 0xB3CA  # Map_ByXHi_InitIndex
"""
This lists the start of a block of world meta data. 9 worlds means 9 times 2 bytes of offsets. The block starts with a
0x00, so that also marks the end of the block before it.
"""

LEVEL_Y_POS_LISTS = WORLD_DATA_OFFSET + 0xB3DC  # Map_ByRowType
"""
This list contains the offsets to the y positions/row indexes of the levels of a world map. Since world maps can have up
to 4 screens, the offset could points to 4 consecutive lists, so we need to know the amount of levels per screen, to
make sense of them.
"""

LEVEL_X_POS_LISTS = WORLD_DATA_OFFSET + 0xB3EE  # Map_ByScrCol
"""
This list contains the offsets to the x positions/column indexes of the levels in a world map. They are listed in a row
for all 4 screens.
"""

WORLD_LEVEL_OBJECT_POINTER_POINTER = WORLD_DATA_OFFSET + 0xB400
"""
"""

WORLD_LEVEL_POINTER_POINTER = WORLD_DATA_OFFSET + 0xB412
"""
The memory locations of levels inside a world map are listed in a row. This offset points to the memory locations of
these lists for every world. The first 2 bytes following this offset point to the levels in world 1, the next 2 for
world 2 etc.
"""

"""
A list of values, which specify which ROM page should be loaded into addresses 0xA000 - 0xBFFF for a given object set.
This is necessary, since the ROM is larger then the addressable RAM in the NES. The offsets of levels are always into
the RAM, which means, to address levels at different parts in the ROM these parts need to be loaded into the RAM first.
"""

"""
Same with the ROM page and addresses 0xC000 - 0xFFFF.
"""

FIRST_VALID_ROW = 2
"""
Tiles in rows before this one are part of the border and not valid overworld tiles.
"""

VALID_ROWS = range(FIRST_VALID_ROW, FIRST_VALID_ROW + WORLD_MAP_HEIGHT)
"""
A range of row values, where Mario could possibly stand.
"""

VALID_COLUMNS = range(SCREEN_WIDTH)
"""
A range of column values, where Mario could possibly stand.
"""

COMPLETABLE_TILES_LIST = WORLD_DATA_OFFSET + 0xA447  # Map_Completable_Tiles
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

WORLD_MAP_SCREEN_SIZE = WORLD_MAP_HEIGHT * SCREEN_WIDTH  # bytes


def is_valid_level_length(level_length: int) -> bool:
    return level_length in range(LEVEL_MIN_LENGTH, LEVEL_MAX_LENGTH + 1, LEVEL_PARTITION_LENGTH)


class LevelBase(ABC):
    width: int
    height: int

    def __init__(self, object_set_number: int, layout_address: int):
        self.layout_address = layout_address

        self.object_set_number = object_set_number
        self.object_set = ObjectSet(self.object_set_number)
