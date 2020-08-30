import pathlib

LEFT_CLICK = "left_click"
RIGHT_CLICK = "right_click"
MIDDLE_CLICK = "middle_click"
BACK_CLICK = "back_click"
FORWARD_CLICK = "forward_click"
CUSTOM_CLICK = "custom_click"
RELEASES_LINK = "https://github.com/mchlnix/SMB3-Foundry/releases"
FEATURE_VIDEO_LINK = "https://www.youtube.com/watch?v=7_22cAffMmE"
GIT_LINK = "https://github.com/mchlnix/SMB3-Foundry"
DISCORD_LINK = "https://discord.gg/pm87gm7"
ROM_FILE_FILTER = "ROM files (*.nes *.rom);;All files (*)"
M3L_FILE_FILTER = "M3L files (*.m3l);;All files (*)"
ASM6_FILE_FILTER = "ASM files (*.asm);; All files (*)"
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
WORLD_MIN_Y_POSITION = 2
WORLD_VALID_LEVEL_Y_POSITIONS = range(WORLD_MIN_Y_POSITION, WORLD_MIN_Y_POSITION + WORLD_MAP_HEIGHT)
WORLD_VALID_LEVEL_X_POSITIONS = range(SCREEN_WIDTH)
WORLD_COMPLETABLE_BLOCKS = WORLD_DATA_OFFSET + 0xA447  # Map_Completable_Tiles
WORLD_COMPLETABLE_BLOCKS_END = 0x00  # MCT_END
WORLD_UNKNOWN_OFFSET = ROM_HEADER_OFFSET + 0x8000  # offset used for uncategorized stuff. TODO find a name
WORLD_SPECIAL_ENTERABLE_BLOCKS = WORLD_UNKNOWN_OFFSET + 0xCDAF  # Map_EnterSpecialTiles
WORLD_SPECIAL_ENTERABLE_BLOCKS_COUNT = 11  # the rom mistakenly uses 0x1A
WORLD_MAP_SCREEN_SIZE = WORLD_MAP_HEIGHT * SCREEN_WIDTH  # bytes
WORD_BYTE_SIZE = 2  # byte
OBJECT_BASE_OFFSET = ROM_HEADER_OFFSET  # + 1
WORLD_LAYOUT_LIST_OFFSET = WORLD_DATA_OFFSET + 0xA598
RESIZE_LEFT_CLICK = "LMB"
RESIZE_RIGHT_CLICK = "RMB"
DRACULA_STYLE_SET = "DRACULA"
RETRO_STYLE_SET = "RETRO"
default_settings_dir = pathlib.Path.home() / ".smb3foundry"
default_settings_path = default_settings_dir / "settings"
ID_RELOAD_LEVEL = 303
ID_GRID_LINES = 501
ID_TRANSPARENCY = 508
ID_JUMPS = 509
ID_MARIO = 510
ID_RESIZE_TYPE = 511
ID_JUMP_OBJECTS = 512
ID_ITEM_BLOCKS = 513
ID_INVISIBLE_ITEMS = 514
ID_BACKGROUND_ENABLED = 515
ID_VISUAL_OBJECT_TOOLBAR = 600
ID_OBJECT_ATTRIBUTE_TOOLBAR = 601
ID_COMPACT_TOOLBAR = 602
ID_BYTES_COUNTER_TOOLBAR = 603
ID_OBJECT_LIST_TOOLBAR = 604
CHECKABLE_MENU_ITEMS = [
    ID_TRANSPARENCY,
    ID_GRID_LINES,
    ID_JUMPS,
    ID_MARIO,
    ID_RESIZE_TYPE,
    ID_JUMP_OBJECTS,
    ID_ITEM_BLOCKS,
    ID_INVISIBLE_ITEMS,
    ID_BACKGROUND_ENABLED,
    ID_VISUAL_OBJECT_TOOLBAR,
    ID_OBJECT_ATTRIBUTE_TOOLBAR,
    ID_COMPACT_TOOLBAR,
    ID_BYTES_COUNTER_TOOLBAR,
    ID_OBJECT_LIST_TOOLBAR,
]
ID_PROP: bytes = "ID"  # the stubs for setProperty are wrong so keep the warning to this line
MODE_FREE = 0
MODE_DRAG = 1
MODE_RESIZE = 2
LINK_SMB3_FOUNDRY = "https://github.com/mchlnix/SMB3-Foundry"
LINK_SMB3_PRIME = "https://smb3p.kafuka.org/index.php"
LINK_SMB3_WIKI = "https://www.smb3prime.org/wiki/Main_Page"
LINK_HUKKA = "http://hukka.ncn.fi/index.php?about"
LINK_SMB3WORKSHOP = "https://www.romhacking.net/utilities/298/"
LINK_SOUTHBIRD = "https://github.com/captainsouthbird"
LINK_DISASM = "https://github.com/captainsouthbird/smb3"
LINK_BLUEFINCH = "https://www.twitch.tv/bluefinch3000"
LINK_JOE_SMO = "https://github.com/TheJoeSmo"
LINK_PIJOKRA = "https://github.com/PiJoKra"
LINK_MICHAEL = "https://github.com/mchlnix"
LINK_SKYYANNICK = "https://www.youtube.com/channel/UCnI_HjFGbyRmfOBWzzxK6LA"