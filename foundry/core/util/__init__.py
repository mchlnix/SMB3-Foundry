from smb3parse.levels import WORLD_MIN_Y_POSITION, WORLD_UNKNOWN_OFFSET

RELEASES_LINK = "https://github.com/mchlnix/SMB3-Foundry/releases"
FEATURE_VIDEO_LINK = "https://www.youtube.com/watch?v=7_22cAffMmE"
GIT_LINK = "https://github.com/mchlnix/SMB3-Foundry"
DISCORD_LINK = "https://discord.gg/pm87gm7"
ROM_FILE_FILTER = "ROM files (*.nes *.rom);;All files (*)"
M3L_FILE_FILTER = "M3L files (*.m3l);;All files (*)"
ASM6_FILE_FILER = "ASM files (*.asm);; All files (*)"
IMG_FILE_FILTER = "Screenshots (*.png);;All files (*)"
ROM_HEADER_OFFSET = 0x10  # the size of the rom header identifying the rom
LEVEL_BASE_OFFSET = ROM_HEADER_OFFSET + 0x10000
PAGE_A_BY_TILESET = ROM_HEADER_OFFSET + 0x34000 + 0x83E9  # PAGE_A000_ByTileset
PAGE_C_BY_TILESET = ROM_HEADER_OFFSET + 0x34000 + 0x83D6  # PAGE_C000_ByTileset
WORLD_COUNT = 9  # includes warp zone
WORLD_MAP_HEIGHT = 9  # blocks
SCREEN_WIDTH = 16  # blocks
LEVEL_HEADER_LENGTH = 9  # in bytes
LEVEL_MIN_LENGTH = 0x10  # in blocks
LEVEL_MAX_LENGTH = 0x100
LEVEL_PARTITION_LENGTH = 0x10
LEVEL_BASE_HEIGHT = 27
LEVEL_BASE_WIDTH = 16
WORLD_DATA_OFFSET = ROM_HEADER_OFFSET + 0xE000
WORLD_BLOCK_ATTRIBUTES_OFFSET = WORLD_DATA_OFFSET + 0xA400
WORLD_SCREEN_LEVEL_POINTER_POINTER = WORLD_DATA_OFFSET + 0xB3CA  # Map_ByXHi_InitIndex
WORLD_LEVEL_Y_POSITIONS_POINTER = WORLD_DATA_OFFSET + 0xB3DC  # Map_ByRowType
WORLD_LEVEL_X_POSITIONS_POINTER = WORLD_DATA_OFFSET + 0xB3EE  # Map_ByScrCol
WORLD_LEVEL_OBJECT_POINTER_POINTER = WORLD_DATA_OFFSET + 0xB400
WORLD_LEVEL_GENERATOR_POINTER_POINTER = WORLD_DATA_OFFSET + 0xB412
WORLD_VALID_LEVEL_Y_POSITIONS = range(WORLD_MIN_Y_POSITION, WORLD_MIN_Y_POSITION + WORLD_MAP_HEIGHT)
WORLD_VALID_LEVEL_X_POSITIONS = range(SCREEN_WIDTH)
WORLD_COMPLETABLE_BLOCKS = WORLD_DATA_OFFSET + 0xA447  # Map_Completable_Tiles
WORLD_COMPLETABLE_BLOCKS_END = 0x00  # MCT_END
WORLD_SPECIAL_ENTERABLE_BLOCKS = WORLD_UNKNOWN_OFFSET + 0xCDAF  # Map_EnterSpecialTiles
WORLD_SPECIAL_ENTERABLE_BLOCKS_COUNT = 11  # the rom mistakenly uses 0x1A
WORLD_MAP_SCREEN_SIZE = WORLD_MAP_HEIGHT * SCREEN_WIDTH  # bytes