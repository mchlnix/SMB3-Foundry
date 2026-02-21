from binascii import unhexlify
from collections import defaultdict
from pathlib import Path

from smb3parse._default_constants import _DefaultConstants
from smb3parse.util import hex_int

BASE_OFFSET = 0x10
"""the size of the INES header identifying the rom"""

PAGE_A000_OFFSET = 0xA000
"""
Certain PRG Banks are loaded into memory beginning at address 0xA000, which is why offsets into them are between 0xA000
and 0xBFFF.

To get the absolute address of things within those Banks, this implicit 0xA000 offset needs to be subtracted first.
"""

PAGE_C000_OFFSET = 0xC000
"""
See PAGE_A000_OFFSET. Just with 0xC000 as the implicit offset.
"""

WORLD_MAP_TSA_INDEX = 12

ENEMY_DATA_BANK_INDEX = 6
"""The 6th PRG bank is where all the enemy/item data is located. And nothing else."""

PLAINS_LEVEL_DATA_BANK_INDEX = 15
"""The 15th PRG bank is where all the level data for Plain levels is located. With related code at the beginning."""

VANILLA_PRG_BANK_COUNT = 32

STOCK_LEVEL_BG_PAGES1_BYTES = unhexlify(
    b"0008101c0c58585c5830346e18381c242c5c586c683428"
)
"""The Level_BG_Pages1 byte array from the stock ROM"""

STOCK_LEVEL_BG_PAGES2_BYTES = unhexlify(
    b"00606060603e605e60606a606060605e2e5e6060607060"
)
"""The Level_BG_Pages2 byte array from the stock ROM"""

TILE_LEVEL_1 = 0x03
TILE_LEVEL_2 = 0x04
TILE_LEVEL_3 = 0x05
TILE_LEVEL_4 = 0x06
TILE_LEVEL_5 = 0x07
TILE_LEVEL_6 = 0x08
TILE_LEVEL_7 = 0x09
TILE_LEVEL_8 = 0x0A
TILE_LEVEL_9 = 0x0B
TILE_LEVEL_10 = 0x0C
TILE_MUSHROOM_HOUSE_1 = 0x50
TILE_MUSHROOM_HOUSE_2 = 0xE0
TILE_STAR_1 = 0x55
TILE_STAR_2 = 0xE9
TILE_SPIRAL_TOWER_1 = 0x5F
TILE_SPIRAL_TOWER_2 = 0xDF
TILE_DUNGEON_1 = 0x67
TILE_DUNGEON_2 = 0xEB
TILE_QUICKSAND = 0x68
TILE_PYRAMID = 0x69
TILE_PIPE = 0xBC
TILE_POND = 0xBF
TILE_CASTLE_BOTTOM = 0xC9
TILE_BOWSER_CASTLE = 0xCC  # TILE_BOWSERCASTLELL
TILE_HAND_TRAP = 0xE6
TILE_SPADE_HOUSE = 0xE8

MUSIC_THEMES = {
    0x01: _("World 1"),
    0x02: _("World 2"),
    0x03: _("World 3"),
    0x04: _("World 4"),
    0x05: _("World 5"),
    0x06: _("World 6"),
    0x07: _("World 7"),
    0x08: _("World 8"),
    0x09: _("Warp World / Coin Heaven"),
    0x0A: _("Starman / Invincibility"),
    0x0B: _("Warp Whistle"),
    0x0C: _("Music Box"),
    0x0D: _("King's Room"),
    0x0E: _("Bonus Game"),
    0x0F: _("Ending Music"),
    0x10: _("Overworld 1"),
    0x20: _("Underground"),
    0x30: _("Water"),
    0x40: _("Fortress"),
    0x50: _("Boss Battle"),
    0x60: _("Airship"),
    0x70: _("Hammer Bros. Battle"),
    0x80: _("Toad House"),
    0x90: _("Overworld 2"),
    0xA0: _("P-Switch"),
    0xB0: _("Bowser"),
    0xC0: _("Bowser's World 8 Letter"),
}

SPRITE_COUNT = 9

MAPOBJ_EMPTY = 0x00
MAPOBJ_HELP = 0x01
MAPOBJ_AIRSHIP = 0x02
MAPOBJ_HAMMERBRO = 0x03
MAPOBJ_BOOMERANGBRO = 0x04
MAPOBJ_HEAVYBRO = 0x05
MAPOBJ_FIREBRO = 0x06
MAPOBJ_W7PLANT = 0x07
MAPOBJ_UNK08 = 0x08
MAPOBJ_NSPADE = 0x09
MAPOBJ_WHITETOADHOUSE = 0x0A
MAPOBJ_COINSHIP = 0x0B
MAPOBJ_UNK0C = 0x0C
MAPOBJ_BATTLESHIP = 0x0D
MAPOBJ_TANK = 0x0E
MAPOBJ_W8AIRSHIP = 0x0F
MAPOBJ_CANOE = 0x10

MAPOBJ_NAMES = {
    MAPOBJ_EMPTY: _("Empty"),
    MAPOBJ_HELP: _("'HELP!' Speech Bubble"),
    MAPOBJ_AIRSHIP: _("Airship"),
    MAPOBJ_HAMMERBRO: _("Hammer Bro"),
    MAPOBJ_BOOMERANGBRO: _("Bummerang Bro"),
    MAPOBJ_HEAVYBRO: _("Heavy Bro"),
    MAPOBJ_FIREBRO: _("Fire Bro"),
    MAPOBJ_W7PLANT: _("World 7 Plant"),
    MAPOBJ_UNK08: _("Unknown"),
    MAPOBJ_NSPADE: _("N-Spade Card"),
    MAPOBJ_WHITETOADHOUSE: _("White Toad House"),
    MAPOBJ_COINSHIP: _("Coinship"),
    MAPOBJ_UNK0C: _("Unknown 2"),
    MAPOBJ_BATTLESHIP: _("Battleship"),
    MAPOBJ_TANK: _("Tank"),
    MAPOBJ_W8AIRSHIP: _("World 8 Airship"),
    MAPOBJ_CANOE: _("Canoe"),
}

# 1 - Super, 2 - Fire, 3 - Leaf, 4 - Frog, 5 - Tanooki, 6 - Hammer, 7 - Judgems, 8 - Pwing, 9 - Star
# A - Anchor, B - Hammer, C - Warp Whistle, D - Music Box

MAPITEM_NOITEM = 0x00
MAPITEM_MUSHROOM = 0x01
MAPITEM_FIREFLOWER = 0x02
MAPITEM_LEAF = 0x03
MAPITEM_FROG = 0x04
MAPITEM_TANOOKI = 0x05
MAPITEM_HAMMERSUIT = 0x06
MAPITEM_JUDGEMS = 0x07
MAPITEM_PWING = 0x08
MAPITEM_STAR = 0x09
MAPITEM_ANCHOR = 0x0A
MAPITEM_HAMMER = 0x0B
MAPITEM_WHISTLE = 0x0C
MAPITEM_MUSICBOX = 0x0D
MAPITEM_UNKNOWN1 = 0x0E
MAPITEM_UNKNOWN2 = 0x0F

MAPITEM_NAMES = {
    MAPITEM_NOITEM: _("No Item"),
    MAPITEM_MUSHROOM: _("Mushroom"),
    MAPITEM_FIREFLOWER: _("Fire Flower"),
    MAPITEM_LEAF: _("Leaf"),
    MAPITEM_FROG: _("Frog Suit"),
    MAPITEM_TANOOKI: _("Tanooki Suit"),
    MAPITEM_HAMMERSUIT: _("Hammer Suit"),
    MAPITEM_JUDGEMS: _("Cloud"),
    MAPITEM_PWING: _("P-Wing"),
    MAPITEM_STAR: _("Star"),
    MAPITEM_ANCHOR: _("Anchor"),
    MAPITEM_HAMMER: _("Hammer"),
    MAPITEM_WHISTLE: _("Warp Whistle"),
    MAPITEM_MUSICBOX: _("Music Box"),
    MAPITEM_UNKNOWN1: _("Broken 1"),
    MAPITEM_UNKNOWN2: _("Broken 2"),
}

TILE_NAMES: dict[int, str] = defaultdict(lambda: _("Blank Square"))
TILE_NAMES.update(
    {
        0x00: _("Mario Clear (Blue)"),
        0x01: _("Luigi Clear (Blue)"),
        0x02: _("Black Square"),
        0x03: _("Level 1"),
        0x04: _("Level 2"),
        0x05: _("Level 3"),
        0x06: _("Level 4"),
        0x07: _("Level 5"),
        0x08: _("Level 6"),
        0x09: _("Level 7"),
        0x0A: _("Level 8"),
        0x0B: _("Level 9"),
        0x0C: _("Level 10"),
        0x0D: _("Level 1 (Broken)"),
        0x0E: _("Level 2 (Broken)"),
        0x0F: _("Level 3 (Broken)"),
        0x10: _("Level 4 (Broken)"),
        0x11: _("Level 5 (Broken)"),
        0x12: _("Level 6 (Broken)"),
        0x13: _("Level 7 (Broken)"),
        0x14: _("Level 8 (Broken)"),
        0x15: _("Level 9 (Broken)"),
        0x40: _("Mario Clear (Orange)"),
        0x41: _("Luigi Clear (Orange)"),
        0x42: _("Desert Background"),
        0x43: _("Sand"),
        0x44: _("Path Upper Left"),
        0x45: _("Path Horizontal 1"),
        0x46: _("Path Vertical"),
        0x47: _("Path Upper Right 1"),
        0x48: _("Path Lower Left"),
        0x49: _("Path Horizontal 2"),
        0x4A: _("Path Lower Right"),
        0x4B: _("Pier"),
        0x4C: _("I's"),
        0x4D: _("Z's"),
        0x4E: _("Top World Map Border"),
        0x4F: _("Bottom World Map Border"),
        0x50: _("Mushroom House (Orange)"),
        0x51: _("Rock 1"),
        0x52: _("Rock 2"),
        0x53: _("Rock 3"),
        0x54: _("Key Door 1"),
        0x55: _("Star 1"),
        0x56: _("Key Door 2"),
        0x57: _("Miniature Path Lower Right"),
        0x58: _("Miniature Path Lower Left 1"),
        0x59: _("Miniature Path Horizontal"),
        0x5A: _("Miniature Tower"),
        0x5B: _("Miniature Path Point Horizontal"),
        0x5C: _("Miniature Path Lower Left 2"),
        0x5D: _("Miniature Cacti 1"),
        0x5E: _("Miniature Cacti 2"),
        0x5F: _("Tower"),
        0x60: _("Fortress Ruins"),
        0x61: _("Bowsers Castle Wall Tower"),
        0x62: _("Bowsers Castle Wall Side"),
        0x63: _("Bowsers Castle Wall Top 1"),
        0x64: _("Bowsers Castle Wall"),
        0x65: _("Bowsers Castle Wall Top 2"),
        0x66: _("Path Upper Right 2"),
        0x67: _("Fortress"),
        0x68: _("Quicksand"),
        0x69: _("Pyramid"),
        0x6A: _("Barracks"),
        0x80: _("Mario Clear (Green)"),
        0x81: _("Luigi Clear (Green)"),
        0x82: _("Water Three-Way Up"),
        0x83: _("Water Three-Way Down"),
        0x84: _("Water 1"),
        0x85: _("Water 2"),
        0x86: _("Water 3"),
        0x87: _("Water 4"),
        0x88: _("Water 5"),
        0x89: _("Water 6"),
        0x8A: _("Water 7"),
        0x8B: _("Water 8"),
        0x8C: _("Water 9"),
        0x8D: _("Water 10"),
        0x8E: _("Water 11"),
        0x8F: _("Water 12"),
        0x90: _("Water 13"),
        0x91: _("Water 14"),
        0x92: _("Water 15"),
        0x93: _("Water 16"),
        0x94: _("Water 17"),
        0x95: _("Water 18"),
        0x96: _("Water 19"),
        0x97: _("Water 20"),
        0x98: _("Water 21"),
        0x99: _("Water 22"),
        0x9A: _("Water 23"),
        0x9B: _("Water 24"),
        0x9C: _("Water 25"),
        0x9D: _("Water 26"),
        0x9E: _("Water 27"),
        0x9F: _("Water 28"),
        0xA0: _("Water 29"),
        0xA1: _("Water 30"),
        0xA2: _("Water 31"),
        0xA3: _("Water 32"),
        0xA4: _("Water 33"),
        0xA5: _("Water 34"),
        0xA6: _("Water 35"),
        0xA7: _("Water 36"),
        0xA8: _("Water 37"),
        0xA9: _("Water 38"),
        0xAA: _("Path Vertical Water Down"),
        0xAB: _("Path Vertical Water Up"),
        0xAC: _("Path Horizontal in Water"),
        0xAD: _("Island"),
        0xAE: _("Path Upper Right in Water"),
        0xAF: _("Path Lower Right in Water"),
        0xB0: _("Path Vertical in Water"),
        0xB1: _("Switchable Bridge Vertical"),
        0xB2: _("Switchable Bridge Horizontal"),
        0xB3: _("Round Bridge"),
        0xB4: _("Bushes"),
        0xB5: _("Path Lower Left in Water"),
        0xB6: _("Path Upper Left in Water"),
        0xB7: _("Path Horizontal Water Right"),
        0xB8: _("Path Horizontal Water Left"),
        0xB9: _("Path Horizontal Water Center"),
        0xBA: _("Path Vertical Water Center"),
        0xBB: _("Palm Tree"),
        0xBC: _("Pipe"),
        0xBD: _("Fire Flower"),
        0xBE: _("Piranha Plant"),
        0xBF: _("Pond"),
        0xC0: _("Mario Clear (Red)"),
        0xC1: _("Luigi Clear (Red)"),
        0xC2: _("Cloud Upper Left"),
        0xC3: _("Cloud Top Left"),
        0xC4: _("Cloud Top Right"),
        0xC5: _("Cloud Upper Right"),
        0xC6: _("? 3"),
        0xC7: _("? 4"),
        0xC8: _("End Castle Top"),
        0xC9: _("End Castle Bottom"),
        0xCA: _("Bowsers Lair Top Left"),
        0xCB: _("Bowsers Lair Top Right"),
        0xCC: _("Bowsers Lair Bottom Left"),
        0xCD: _("Bowsers Lair Bottom Right"),
        0xCE: _("Cloud Left 1"),
        0xCF: _("? 5"),
        0xD0: _("Cloud Diagnoal"),
        0xD1: _("Flame"),
        0xD2: _("Cloud Left 2"),
        0xD3: _("Cloud Bottom"),
        0xD4: _("Cloud Lower Right"),
        0xD5: _("I's 2"),
        0xD6: _("Red Background ?"),
        0xD7: _("Desert Background 2 ?"),
        0xD8: _("Black Square"),
        0xD9: _("Path Upper Left 2"),
        0xDA: _("Path Horizontal 3"),
        0xDB: _("Path Vertical 2"),
        0xDC: _("Path Upper Right 2"),
        0xDD: _("Path Lower Left 2"),
        0xDE: _("Path Lower Right 2"),
        0xDF: _("Tower 2"),
        0xE0: _("Mushroom House 2"),
        0xE1: _("Mushroom"),
        0xE2: _("Skull"),
        0xE3: _("Fortress Ruins 2"),
        0xE4: _("Key Door 3"),
        0xE5: _("Start Field"),
        0xE6: _("Hand Field"),
        0xE7: _("? 6"),
        0xE8: _("Spade Bonus"),
        0xE9: _("Star 2"),
        0xEA: _("Rock Alternative"),
        0xEB: _("Fortress 2"),
    }
)

AIRSHIP_TRAVEL_SET_COUNT = 3  # offsets of 2 bytes each
AIRSHIP_TRAVEL_SET_SIZE = 6  # bytes

FORTRESS_FX_COUNT = 17  # entries/bytes
PIPE_PAIR_COUNT = 24  # entries

GAME_LEVEL_POINTER_COUNT = 340  # without the 10 from warp world
GAME_SCREEN_COUNT = 20

OFFSET_SIZE = 2  # byte
ENEMY_SIZE = 3  # byte

# level objects (domain, index)
LVL_OBJ_LEVEL_END = (0x02, 0x09)

# enemies and item objects
OBJ_PIPE_EXITS = 0x25
OBJ_GOAL_CARD = 0x41
OBJ_BOOMBOOM = 0x4B
OBJ_FLYING_BOOMBOOM = 0x4C
OBJ_TREASURE_CHEST = 0x52
OBJ_HAMMER_BRO = 0x81
OBJ_CHEST_EXIT = 0xBA
OBJ_AUTOSCROLL = 0xD3
OBJ_WHITE_MUSHROOM_HOUSE = 0xD4
OBJ_CHEST_ITEM_SETTER = 0xD6

POWERUP_MUSHROOM = 0x01
POWERUP_FIREFLOWER = 0x02
POWERUP_RACCOON = 0x03
POWERUP_FROG = 0x04
POWERUP_TANOOKI = 0x05
POWERUP_HAMMER = 0x06
POWERUP_ADDITION_JUDGEMS = 0x07
POWERUP_ADDITION_PWING = 0x08
POWERUP_ADDITION_STARMAN = 0x09

STARTING_WORLD_INDEX_ADDRESS = 0x30CC3


class _ClassVarRedirect(type):
    """
    A metaclass that allows a class to define class variables that will get their values dynamically from other class
    variables.
    The relation between those two class variables is described in a dictionary called _redirect.
    The keys are the names of class variables, without a name, the values are the names of variables to look up instead.
    """

    _redirect: dict[str, str]

    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, "_redirect") or not isinstance(cls._redirect, dict):
            raise ValueError(
                "Class must have a dictionary class variable named '_redirect'"
            )

        for annotation in cls.__annotations__:
            if annotation not in cls._redirect:
                raise ValueError(
                    f"'{annotation}' must have an entry in its class's _redirect dictionary"
                )

            class_var = cls._redirect[annotation]

            if not hasattr(cls, class_var):
                raise ValueError(
                    f"Didn't find class variable '{class_var}' for annotation '{annotation}'"
                )

        super(_ClassVarRedirect, cls).__init__(name, bases, attrs)

    def __getattr__(cls, item):
        """
        Intercept class variable access.
        If the attribute is an annotation without a value, instead of a class variable, consult the _redirect dict.
        If an entry of that name is found there, return the value of whatever attribute is in that entry is returned.
        """
        if item in cls.__annotations__ and item in cls._redirect:
            class_variable_to_return_instead = cls._redirect[item]

            return getattr(cls, class_variable_to_return_instead)
        else:
            return object.__getattribute__(cls, item)


class Constants(_DefaultConstants, metaclass=_ClassVarRedirect):
    OFFSET_BY_OBJECT_SET_A000: int
    """
    A list of values, which specify which ROM page should be loaded into addresses 0xA000 - 0xBFFF for a given object
    set.
    This is necessary, since the ROM is larger then the addressable RAM in the NES. The offsets of levels are always
    into the RAM, which means, to address levels at different parts in the ROM these parts need to be loaded into the
    RAM first.
    """

    OFFSET_BY_OBJECT_SET_C000: int
    """
    See OFFSET_BY_OBJECT_SET_A000. Same as that, but with the ROM page and addresses 0xC000 - 0xFFFF.
    """

    TSA_OS_LIST: int

    LEVEL_BASE_OFFSET: int
    """
    Offset for level related parsing. Currently only used in Header.
    """

    LAYOUT_LIST_OFFSET: int

    TILE_ATTRIBUTES_TS0_OFFSET: int
    """
    The first 4 bytes describe minimal indexes an overworld tile must have to be enterable.
    """

    STRUCTURE_DATA_OFFSETS: int
    """
    This lists the start of a block of world meta data. 9 worlds means 9 times 2 bytes of offsets. The block starts with
    a 0x00, so that also marks the end of the block before it.
    """

    LEVEL_Y_POS_LISTS: int
    """
    This list contains the offsets to the y positions/row indexes of the levels of a world map. Since world maps can
    have up to 4 screens, the offset could points to 4 consecutive lists, so we need to know the amount of levels per
    screen, to make sense of them.
    """

    LEVEL_X_POS_LISTS: int
    """
    This list contains the offsets to the x positions/column indexes of the levels in a world map. They are listed in a
    row for all 4 screens.
    """

    LEVEL_ENEMY_LIST_OFFSET: int
    """
    """

    LEVELS_IN_WORLD_LIST_OFFSET: int
    """
    The memory locations of levels inside a world map are listed in a row. This offset points to the memory locations of
    these lists for every world. The first 2 bytes following this offset point to the levels in world 1, the next 2 for
    world 2 etc.
    """

    COMPLETABLE_TILES_LIST: int
    """
    A list of tile values, that are completable, like the Toad House.
    """

    SPECIAL_ENTERABLE_TILES_LIST: int
    """
    A list of tile values, that are also enterable, like the castle and the toad house.
    """

    LEVEL_LOAD_ROUTINE_BY_OBJECT_SET: int
    """
    A lookup table that holds the individual addresses of the level loading routines for each object set.
    """

    _redirect = {
        "OFFSET_BY_OBJECT_SET_A000": "PAGE_A000_ByTileset",
        "TSA_OS_LIST": "PAGE_A000_ByTileset",
        "OFFSET_BY_OBJECT_SET_C000": "PAGE_C000_ByTileset",
        "LEVEL_BASE_OFFSET": "Level_TilesetIdx_ByTileset",
        "LAYOUT_LIST_OFFSET": "Map_Tile_Layouts",
        "TILE_ATTRIBUTES_TS0_OFFSET": "Tile_Attributes_TS0",
        "STRUCTURE_DATA_OFFSETS": "Map_ByXHi_InitIndex",
        "LEVEL_Y_POS_LISTS": "Map_ByRowType",
        "LEVEL_X_POS_LISTS": "Map_ByScrCol",
        "LEVEL_ENEMY_LIST_OFFSET": "Map_ObjSets",
        "LEVELS_IN_WORLD_LIST_OFFSET": "Map_LevelLayouts",
        "COMPLETABLE_TILES_LIST": "Map_Completable_Tiles",
        "SPECIAL_ENTERABLE_TILES_LIST": "Map_EnterSpecialTiles",
        "LEVEL_LOAD_ROUTINE_BY_OBJECT_SET": "LevelLoad_ByTileset",
    }


def reset_global_offsets():
    for attr_name in dir(Constants):
        if attr_name.startswith("__"):
            # internal attribute
            continue

        if attr_name.startswith("_"):
            # backup value
            continue

        backup_attr_name = "_" + attr_name

        setattr(Constants, attr_name, getattr(Constants, backup_attr_name))


def update_global_offsets(path_to_global_list: Path):
    warnings: list[str] = []

    with path_to_global_list.open("r") as label_file:
        reset_global_offsets()
        for line in label_file:
            if line.startswith(";"):
                continue

            label_name, hex_address = line.split("=")
            label_name = label_name.strip()
            hex_address = hex_address.strip().replace("$", "0x")

            if label_name.startswith(("PRG0", "_")):
                continue

            global_address = hex_int(hex_address)

            if not hasattr(Constants, label_name):
                warnings.append(_("Unknown label: %s") % label_name)

            setattr(Constants, label_name, global_address)

    for attr_name in Constants._redirect:
        if attr_name.isupper():
            print(f"{attr_name}: {getattr(Constants, attr_name):#x}")
