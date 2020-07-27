
from dataclasses import dataclass

from foundry.game.File import ROM


CHR_ROM_OFFSET = 0x40010
CHR_ROM_SEGMENT_SIZE = 0x400

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
    def __init__(self, page: int):
        self.data = bytearray()
        self.page = page

        segments = []

        if page == WORLD_MAP:
            segments = [0x14, 0x16, 0x20, 0x21, 0x22, 0x23]
        if page not in graphic_set2chr_index and page not in common_set2chr_index:
            self._read_in([page, page + 2])
        else:
            gfx_index = graphic_set2chr_index[page]
            common_index = common_set2chr_index[page]

            segments.append(gfx_index)
            segments.append(common_index)

            if page == SPADE_ROULETTE:
                segments.extend([0x20, 0x21, 0x22, 0x23])
            elif page == N_SPADE:
                segments.extend([0x28, 0x29, 0x5A, 0x31])
            elif page == VS_2P:
                segments.extend([0x04, 0x05, 0x06, 0x07])
            else:
                segments.extend([0x00, 0x00, 0x00, 0x00])

        self._read_in(segments)

    def _read_in(self, segments):
        for segment in segments:
            self._read_in_chr_rom_segment(segment)

    def _read_in_chr_rom_segment(self, index):
        offset = ROM().chr_offset + index * CHR_ROM_SEGMENT_SIZE
        chr_rom_data = ROM().bulk_read(2 * CHR_ROM_SEGMENT_SIZE, offset)

        self.data.extend(chr_rom_data)
