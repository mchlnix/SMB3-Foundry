
from typing import Tuple
from dataclasses import dataclass, astuple
from functools import lru_cache

from foundry.game.File import ROM, _ROM


CHR_PAGE = CHR_ROM_SEGMENT_SIZE = 0x400

WORLD_MAP = 0
SPADE_ROULETTE = 16
N_SPADE = 17
VS_2P = 18

graphic_set2chr_index = {
    0: 0x00,  # not used
    1: 0x08,  # Plains
    2: 0x10,  # Fortress
    3: 0x1C,  # Hills / Underground
    4: 0x0C,  # Sky
    5: 0x58,  # Piranha Plant
    6: 0x58,  # Water
    7: 0x5C,  # Mushroom
    8: 0x58,  # Pipe
    9: 0x30,  # Desert
    10: 0x34,  # Ship
    11: 0x6E,  # Giant
    12: 0x18,  # Ice
    13: 0x38,  # Cloudy
    14: 0x1C,  # Not Used (same as 3)
    15: 0x24,  # Bonus Room
    16: 0x2C,  # Spade (Roulette)
    17: 0x5C,  # N-Spade (Card)
    18: 0x58,  # 2P vs.
    19: 0x6C,  # Hills / Underground alternative
    20: 0x68,  # 3-7 only
    21: 0x34,  # World 8 War Vehicle
    22: 0x28,  # Throne Room
}

common_set2chr_index = {
    0: 0x00,  # not used
    1: 0x60,  # Plains
    2: 0x60,  # Fortress
    3: 0x60,  # Hills / Underground
    4: 0x60,  # Sky
    5: 0x3E,  # Piranha Plant
    6: 0x60,  # Water
    7: 0x5E,  # Mushroom
    8: 0x60,  # Pipe
    9: 0x60,  # Desert
    10: 0x6A,  # Ship
    11: 0x60,  # Giant
    12: 0x60,  # Ice
    13: 0x60,  # Cloudy
    14: 0x60,  # Not Used (same as 3)
    15: 0x5E,  # Bonus Room
    16: 0x2E,  # Spade (Roulette)
    17: 0x5E,  # N-Spade (Card)
    18: 0x60,  # 2P vs.
    19: 0x60,  # Hills / Underground alternative
    20: 0x60,  # 3-7 only
    21: 0x70,  # World 8 War Vehicle
    22: 0x60,  # Throne Room
}


GRAPHIC_SET_NAMES = [
    "Mario graphics (1)",
    "Plain",
    "Dungeon",
    "Underground (1)",
    "Sky",
    "Pipe/Water (1, Piranha Plant)",
    "Pipe/Water (2, Water)",
    "Mushroom house (1)",
    "Pipe/Water (3, Pipe)",
    "Desert",
    "Ship",
    "Giant",
    "Ice",
    "Clouds",
    "Underground (2)",
    "Spade bonus room",
    "Spade bonus",
    "Mushroom house (2)",
    "Pipe/Water (4)",
    "Hills",
    "Plain 2",
    "Tank",
    "Castle",
    "Mario graphics (2)",
    "Animated graphics (1)",
    "Animated graphics (2)",
    "Animated graphics (3)",
    "Animated graphics (4)",
    "Animated graphics (P-Switch)",
    "Game font/Course Clear graphics",
    "Animated graphics (5)",
    "Animated graphics (6)",
]


@dataclass
class PatternTable:
    """Represents the game's pattern table for the chr data"""
    background_0: int
    background_1: int
    sprite_0: int
    sprite_1: int
    sprite_2: int
    sprite_3: int


class PatternTableHandler:
    """Makes an artificial PPU for the graphics"""
    def __init__(self, pattern_table: PatternTable):
        self.pattern_table = pattern_table
        self.data = self.get_data(astuple(self.pattern_table))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.pattern_table}) with data {self.data}"

    def get_data(self, pattern_table: Tuple[int, int, int, int, int, int]) -> bytearray:
        """Caches the data for quick access"""
        data = bytearray()
        offset = ROM().chr_offset
        for i in range(2):
            data.extend(ROM().bulk_read(CHR_PAGE * 2, offset + CHR_PAGE * (pattern_table[i] & 0b1111_1110)))
        for i in range(2, 6):
            data.extend(ROM().bulk_read(CHR_PAGE, offset + CHR_PAGE * pattern_table[i]))
        data.extend([0 for _ in range(0x10)])
        return data

    @classmethod
    def from_world_map(cls):
        """Makes a pattern table handler for the world map"""
        return cls(PatternTable(0x14, 0x16, 0x20, 0x21, 0x22, 0x23))

    @classmethod
    def from_tileset(cls, tileset: int):
        """Makes a pattern table handler from a tileset"""
        ptn_tbl = PatternTable(0, 0, 0, 0, 0, 0)

        if tileset not in graphic_set2chr_index and tileset not in common_set2chr_index:
            ptn_tbl.background_0 = tileset
            ptn_tbl.background_1 = tileset
        else:
            ptn_tbl.background_0 = graphic_set2chr_index[tileset]
            ptn_tbl.background_1 = common_set2chr_index[tileset]

            if tileset == SPADE_ROULETTE:
                ptn_tbl.sprite_0 = 0x20
                ptn_tbl.sprite_1 = 0x21
                ptn_tbl.sprite_2 = 0x22
                ptn_tbl.sprite_3 = 0x23
            elif tileset == N_SPADE:
                ptn_tbl.sprite_0 = 0x28
                ptn_tbl.sprite_1 = 0x29
                ptn_tbl.sprite_2 = 0x5A
                ptn_tbl.sprite_3 = 0x31
            elif tileset == VS_2P:
                ptn_tbl.sprite_0 = 0x04
                ptn_tbl.sprite_1 = 0x05
                ptn_tbl.sprite_2 = 0x06
                ptn_tbl.sprite_3 = 0x07
        return cls(ptn_tbl)
