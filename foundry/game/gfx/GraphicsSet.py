from functools import lru_cache

from foundry.game.File import ROM
from smb3parse.constants import Level_BG_Pages1, Level_BG_Pages2

CHR_ROM_OFFSET = 0x40010
CHR_ROM_SEGMENT_SIZE = 0x400

WORLD_MAP = 0
SPADE_ROULETTE = 16
N_SPADE = 17
VS_2P = 18

BG_PAGE_COUNT = Level_BG_Pages2 - Level_BG_Pages1  # 23 in stock rom

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


class GraphicsSet:
    GRAPHIC_SET_BG_PAGE_1 = bytearray()
    GRAPHIC_SET_BG_PAGE_2 = bytearray()

    def __init__(self, graphic_set_number):
        if not self.GRAPHIC_SET_BG_PAGE_1:
            self.GRAPHIC_SET_BG_PAGE_1 = ROM().bulk_read(BG_PAGE_COUNT, Level_BG_Pages1)
            self.GRAPHIC_SET_BG_PAGE_2 = ROM().bulk_read(BG_PAGE_COUNT, Level_BG_Pages2)

        self._data = bytearray()
        self._anim_data = []
        self.anim_frame = 0
        self.number = graphic_set_number

        segments = []

        if graphic_set_number == WORLD_MAP:
            segments = [0x16, 0x20, 0x21, 0x22, 0x23]

            for index in [0x14, 0x70, 0x72, 0x74]:
                self._anim_data.append(bytearray())

                self._read_in_chr_rom_segment(index, self._anim_data[-1])

        if graphic_set_number not in range(BG_PAGE_COUNT):
            self._read_in([graphic_set_number, graphic_set_number + 2])
        else:
            gfx_index = self.GRAPHIC_SET_BG_PAGE_1[graphic_set_number]
            common_index = self.GRAPHIC_SET_BG_PAGE_2[graphic_set_number]

            segments.append(gfx_index)
            segments.append(common_index)

            if graphic_set_number == SPADE_ROULETTE:
                segments.extend([0x20, 0x21, 0x22, 0x23])
            elif graphic_set_number == N_SPADE:
                segments.extend([0x28, 0x29, 0x5A, 0x31])
            elif graphic_set_number == VS_2P:
                segments.extend([0x04, 0x05, 0x06, 0x07])
            else:
                segments.extend(
                    [
                        common_index + 2,
                        common_index + 4,
                        common_index + 6,
                        common_index + 8,
                    ]
                )

        self._read_in(segments)

    @property
    def data(self):
        if self.number == WORLD_MAP:
            return self._anim_data[self.anim_frame] + self._data
        else:
            page_1 = self._data[0 : 2 * CHR_ROM_SEGMENT_SIZE]

            start = 2 * CHR_ROM_SEGMENT_SIZE + self.anim_frame * 2 * CHR_ROM_SEGMENT_SIZE
            end = 2 * CHR_ROM_SEGMENT_SIZE + start + 2 * CHR_ROM_SEGMENT_SIZE

            page_2 = self._data[start:end]

            return page_1 + page_2

    def _read_in(self, segments):
        for segment in segments:
            self._read_in_chr_rom_segment(segment, self._data)

    def _read_in_chr_rom_segment(self, index, data):
        offset = CHR_ROM_OFFSET + index * CHR_ROM_SEGMENT_SIZE
        chr_rom_data = ROM().bulk_read(2 * CHR_ROM_SEGMENT_SIZE, offset)

        data.extend(chr_rom_data)

    @staticmethod
    @lru_cache(32)
    def from_number(graphic_set_number: int) -> "GraphicsSet":
        return GraphicsSet(graphic_set_number)
