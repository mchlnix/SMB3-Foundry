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