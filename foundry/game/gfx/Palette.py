from typing import List

from PySide2.QtGui import QColor

from foundry import root_dir
from foundry.game.File import ROM
from smb3parse.constants import PalSet_Maps, Palette_By_Tileset
from smb3parse.levels import BASE_OFFSET

MAP_PALETTE_ADDRESS = PalSet_Maps

PALETTE_BASE_ADDRESS = BASE_OFFSET + 0x2C000
PALETTE_OFFSET_LIST = Palette_By_Tileset
PALETTE_OFFSET_SIZE = 2  # bytes

LEVEL_PALETTE_GROUPS_PER_OBJECT_SET = 8
ENEMY_PALETTE_GROUPS_PER_OBJECT_SET = 4
PALETTES_PER_PALETTES_GROUP = 4

COLORS_PER_PALETTE = 4
COLOR_SIZE = 1  # byte

PALETTE_DATA_SIZE = (
    (LEVEL_PALETTE_GROUPS_PER_OBJECT_SET + ENEMY_PALETTE_GROUPS_PER_OBJECT_SET)
    * PALETTES_PER_PALETTES_GROUP
    * COLORS_PER_PALETTE
)

palette_file = root_dir.joinpath("data", "Default.pal")

with open(palette_file, "rb") as f:
    color_data = f.read()

offset = 0x18  # first color position

NESPalette = []
COLOR_COUNT = 64
BYTES_IN_COLOR = 3 + 1  # bytes + separator

for i in range(COLOR_COUNT):
    NESPalette.append([color_data[offset], color_data[offset + 1], color_data[offset + 2]])

    offset += BYTES_IN_COLOR


def load_palette(object_set: int, palette_group: int):
    """
    Basically does, what the Setup_PalData routine does.

    :param object_set: Level_Tileset in the disassembly.
    :param palette_group: Palette_By_Tileset. Defined in the level header.

    :return: A list of 4 groups of 4 colors.
    """
    rom = ROM()

    palette_offset_position = PALETTE_OFFSET_LIST + (object_set * PALETTE_OFFSET_SIZE)
    palette_offset = rom.little_endian(palette_offset_position)

    palette_address = PALETTE_BASE_ADDRESS + palette_offset
    palette_address += palette_group * PALETTES_PER_PALETTES_GROUP * COLORS_PER_PALETTE

    palettes = []

    for _ in range(PALETTES_PER_PALETTES_GROUP):
        palettes.append(rom.read(palette_address, COLORS_PER_PALETTE))

        palette_address += COLORS_PER_PALETTE

    return palettes


def bg_color_for_object_set(object_set_number: int, palette_group_index: int) -> QColor:
    palette = load_palette(object_set_number, palette_group_index)

    return QColor(*bg_color_for_palette(palette))


def bg_color_for_palette(palette: List[bytearray]):
    return NESPalette[palette[0][0]]
