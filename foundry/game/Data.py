from collections import namedtuple
from typing import NamedTuple


def read_string_dict(path):
    return_dict = dict()

    with open(path, "r") as f:
        for line in f.readlines():
            key, value = line.rstrip().split("=")

            return_dict[key] = value

    return return_dict


MAX_LEVEL_SECTIONS = 65
SMB3_LEVEL_COUNT = 298

MapscreenPointerLocation = namedtuple("MapscreenPointerLocation", "count offset")
ObjectInfo = namedtuple("ObjectInfo", "index subindex x y width height x2 y2 obj objtype rect drag")


class Mario3Level(NamedTuple):
    game_world: int
    level_in_world: int
    rom_level_offset: int
    enemy_offset: int
    real_obj_set: int
    name: str


map_sprite_names = [
    "Nothing?",
    '"Help!"',
    "Ship",
    "Hammer Bros.",
    "Boomerang Bros.",
    "Sledge Bros.",
    "Fire Bros.",
    "Piranha Plant",
    "Weird",
    "N-card",
    "White Mushroom House",
    "Coin Ship",
    "World 8 Ship #1",
    "Battleship",
    "Tank",
    "World 8 Ship #2",
    "Boat",
]

obj_sets = [
    "Map Screen",
    "Plains Level",
    "Hilly/Underground Level",
    "Sky Level",
    "Dungeon",
    "Airship",
    "Cloudy Level",
    "Desert Level",
    "Water/Pipe Level",
    "Giant Level",
    "Ice Level",
]

mushroom_houses = [
    "P-Wing Only",
    "Warp Whistle Only",
    "P-Wing Only",
    "Frog Suit Only",
    "Tanooki Suit Only",
    "Hammer Suit Only",
    "Frog, Tanooki, Hammer Suit",
    "Mushroom, Leaf, Flower",
    "Leaf, Flower, Frog Suit",
    "Leaf, Flower, Tanooki Suit",
    "Anchor Only",
    "Warp Whistle, P-Wing, Frog Suit",
    "Frog Suit, P-Wing, Tanooki Suit",
    "Frog, Tanooki, Hammer Suit",
    "Warp Whistle, P-Wing, Frog Suit",
    "Frog Suit, P-Wing, Tanooki Suit",
    "Frog, Tanooki, Hammer Suit",
    "Warp Whistle, P-Wing, Frog Suit",
    "Frog Suit, P-Wing, Tanooki Suit",
    "Frog, Tanooki, Hammer Suit",
    "Warp Whistle, P-Wing, Frog Suit",
    "Frog Suit, P-Wing, Tanooki Suit",
    "Frog, Tanooki, Hammer Suit",
    "Warp Whistle, P-Wing, Frog Suit",
    "Frog Suit, P-Wing, Tanooki Suit",
    "Frog, Tanooki, Hammer Suit",
    "Warp Whistle, P-Wing, Frog Suit",
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
