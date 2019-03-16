from collections import namedtuple

import wx

from m3idefs import ObjectDefinition


def read_string_dict(path):
    return_dict = dict()

    with open(path, "r") as f:
        for line in f.readlines():
            key, value = line.rstrip().split("=")
            print(f"{key}={value}")

            return_dict[key] = value

    return return_dict


def get_config_integer(name, default):
    pass


MAX_LEVEL_SECTIONS = 65
SMB3_LEVEL_COUNT = 298
MAP_ENEMY_OFFSET = 0x16070
ENEMY_BANK = 12

MapscreenPointerLocation = namedtuple("MapscreenPointerLocation", "count offset")
ObjectInfo = namedtuple("ObjectInfo", "index subindex x y width height x2 y2 obj objtype rect drag")
ObjectSetPointerType = namedtuple("ObjectSetPointerType", "type name min max")
Mario3Level = namedtuple("Mario3Level", [
    "game_world",
    "level_in_world",
    "rom_level_offset",
    "enemy_offset",
    "real_obj_set",
    "name"
])

tsa_offsets = []
graphics_offsets = []
common_offsets = []

MAP_PALETTE_ADDRESS = 0x36BE2
PALETTE_ADDRESS = 0x36CA2  # for levels?

palette_file = "data/Default.pal"

with open(palette_file, "rb") as f:
    color_data = f.read()

offset = 0x18  # first color position

NESPalette = []
COLOR_COUNT = 64
COLOR_SIZE = 3

for i in range(COLOR_COUNT):
    NESPalette.append([color_data[offset], color_data[offset + 1], color_data[offset + 2]])

    offset += COLOR_SIZE + 1

zoom_size = 16
RomGfx = wx.Image(width=256, height=256)

# loadgfx

string_dict = read_string_dict("data/rom.ini")

for offset in string_dict["offsets.tsa"].split(","):
    tsa_offsets.append(int(offset, 16))

for offset in string_dict["offsets.graphics"].split(","):
    graphics_offsets.append(int(offset, 16))

for offset in string_dict["offsets.common"].split(","):
    common_offsets.append(int(offset, 16))

PALETTE_ADDRESS = int(string_dict["levelpalettes"], 16)
MAP_PALETTE_ADDRESS = int(string_dict["mappalettes"], 16)


world_indexes = [0]  # insert meaningless first item, so that the world number is the correct index
level_array = [0]  # insert meaningless first item so that that world_indexes[world] + level is the correct index

with open("data/levels.dat", "r") as level_data:
    for line_no, line in enumerate(level_data.readlines()):
        data = line.rstrip("\n").split(",")

        numbers = [int(_hex, 16) for _hex in data[0:5]]
        level_name = data[5]

        level_array.append(Mario3Level(*numbers, level_name))

        world_index, level_index = numbers[0], numbers[1]

        if world_index > 0 and level_index == 1:
            world_indexes.append(line_no)

WORLDS = len(world_indexes)


plains_level = [[]]
enemy_handle_x = []
enemy_handle_x2 = []
enemy_handle_y = []

with open("data/data.dat", "r") as f:
    first_index = 0  # todo what are they symbolizing? object tables?
    second_index = 0

    for line in f.readlines():
        if line.startswith(";"):  # is a comment
            continue

        if line.rstrip() == '':
            plains_level.append([])

            first_index += 1
            second_index = 0
            continue

        plains_level[first_index].append(ObjectDefinition(line))

        if first_index == ENEMY_BANK and second_index <= 236:
            if line.find("|") >= 0:
                x, y, x2 = line.split("|")[1].split(" ")
            else:
                x, y, x2 = 0, 0, 0

            enemy_handle_x.append(x)
            enemy_handle_x2.append(x2)
            enemy_handle_y.append(y)

        second_index += 1

map_sprite_names = [
 'Nothing?', '"Help!"', 'Ship', 'Hammer Bros.',
 'Boomerang Bros.', 'Sledge Bros.', 'Fire Bros.',
 'Piranha Plant', 'Weird', 'N-card',
 'White Mushroom House', 'Coin Ship', 'World 8 Ship #1',
 'Battleship', 'Tank', 'World 8 Ship #2', 'Boat'
]

obj_sets = [
 'Map Screen',
 'Plains Level',
 'Hilly/Underground Level',
 'Sky Level',
 'Dungeon',
 'Airship',
 'Cloudy Level',
 'Desert Level',
 'Water/Pipe Level',
 'Giant Level',
 'Ice Level'
]

OBJSET_MAP = 0
OBJSET_PLAINS = 1
OBJSET_HILLY = 2
OBJSET_SKY = 3
OBJSET_DUNGEON = 4
OBJSET_AIRSHIP = 5
OBJSET_CLOUDY = 6
OBJSET_DESERT = 7
OBJSET_WATERPIPE = 8
OBJSET_GIANT = 9
OBJSET_ICE = 10
OBJSET_UNDERGROUND = 11

mushroom_houses = [
    'P-Wing Only', 'Warp Whistle Only',
    'P-Wing Only', 'Frog Suit Only',
    'Tanooki Suit Only', 'Hammer Suit Only',
    'Frog, Tanooki, Hammer Suit', 'Mushroom, Leaf, Flower',
    'Leaf, Flower, Frog Suit', 'Leaf, Flower, Tanooki Suit',
    'Anchor Only',
    'Warp Whistle, P-Wing, Frog Suit', 'Frog Suit, P-Wing, Tanooki Suit',
    'Frog, Tanooki, Hammer Suit',
    'Warp Whistle, P-Wing, Frog Suit', 'Frog Suit, P-Wing, Tanooki Suit',
    'Frog, Tanooki, Hammer Suit',
    'Warp Whistle, P-Wing, Frog Suit', 'Frog Suit, P-Wing, Tanooki Suit',
    'Frog, Tanooki, Hammer Suit',
    'Warp Whistle, P-Wing, Frog Suit', 'Frog Suit, P-Wing, Tanooki Suit',
    'Frog, Tanooki, Hammer Suit',
    'Warp Whistle, P-Wing, Frog Suit', 'Frog Suit, P-Wing, Tanooki Suit',
    'Frog, Tanooki, Hammer Suit',
    'Warp Whistle, P-Wing, Frog Suit'
]

map_pointers = [
    MapscreenPointerLocation(21, 0x19438),  # World 1
    MapscreenPointerLocation(47, 0x194BA),  # World 2
    MapscreenPointerLocation(52, 0x195D8),  # World 3
    MapscreenPointerLocation(34, 0x19714),  # World 4
    MapscreenPointerLocation(42, 0x197E4),  # World 5
    MapscreenPointerLocation(57, 0x198E4),  # World 6
    MapscreenPointerLocation(46, 0x19A3E),  # World 7
    MapscreenPointerLocation(41, 0x19B56),  # World 8
    MapscreenPointerLocation(10, 0x19C50),  # Warp Zone (no enemies or level pointers)
]

object_set_pointers = [
    ObjectSetPointerType(type=0x0000, name='Map Screen', min=0x18010, max=0x1A00F),
    ObjectSetPointerType(type=0x4000, name='Plains', min=0x1E512, max=0x2000F),
    ObjectSetPointerType(type=0x10000, name='Dungeon', min=0x2A7F7, max=0x2C00F),
    ObjectSetPointerType(type=0x6000, name='Hilly', min=0x20587, max=0x2200F),
    ObjectSetPointerType(type=0x8000, name='Sky', min=0x227E0, max=0x2400F),
    ObjectSetPointerType(type=0xC000, name='Piranha Plant', min=0x26A6F, max=0x2800F),
    ObjectSetPointerType(type=0xA000, name='Water', min=0x24BA7, max=0x2600F),
    ObjectSetPointerType(type=0x0000, name='Mushroom House', min=0x0000, max=0x0000),
    ObjectSetPointerType(type=0xA000, name='Pipe', min=0x24BA7, max=0x2600F),
    ObjectSetPointerType(type=0xE000, name='Desert', min=0x28F3F, max=0x2A00F),
    ObjectSetPointerType(type=0x14000, name='Ship', min=0x2EC07, max=0x3000F),
    ObjectSetPointerType(type=0xC000, name='Giant', min=0x26A6F, max=0x2800F),
    ObjectSetPointerType(type=0x8000, name='Ice', min=0x227E0, max=0x2400F),
    ObjectSetPointerType(type=0xC000, name='Cloudy', min=0x26A6F, max=0x2800F),
    ObjectSetPointerType(type=0x0000, name='Underground', min=0x1A587, max=0x1C00F),
    ObjectSetPointerType(type=0x0000, name='Spade House', min=0xA010, max=0xC00F),
]

object_ranges = [
    # Object Set 1
    ((3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3)),
    # Object Set 2
    ((3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3)),
    # Object Set 3
    ((3, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3)),
    # Object Set 4
    ((3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3),
     (3, 3, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, 4, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3)),
    # Object Set 5
    ((3, 3, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3),
     (3, 3, 3, 3, 4, 3, 3, 4, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3)),
    # Object Set 6
    ((3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3),
     (3, 4, 4, 3, 4, 3, 3, 4, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3)),
    # Object Set 7
    ((3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3)),
    # Object Set 8
    ((3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3),
     (3, 3, 3, 3, 3, 4, 3, 3, 3, 3, 3, 3, 3, 4, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3)),
    # Object Set 9
    ((3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3),
     (3, 4, 4, 3, 4, 3, 3, 4, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3)),
    # Object Set 10
    ((3, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3)),
    # Object Set 11
    ((3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
     (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3))
]
