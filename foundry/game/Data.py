from typing import NamedTuple

VANILLA_SMB3_LEVEL_COUNT = 298


class Mario3Level(NamedTuple):
    game_world: int
    level_in_world: int
    rom_level_offset: int
    enemy_offset: int
    real_obj_set: int
    name: str


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
