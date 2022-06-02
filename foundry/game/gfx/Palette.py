from typing import Dict, List, Optional, Tuple

from PySide6.QtGui import QColor
from attr import dataclass

from foundry import root_dir
from foundry.game.File import ROM
from smb3parse.constants import PalSet_Maps, Palette_By_Tileset
from smb3parse.levels import BASE_OFFSET

MAP_PALETTE_ADDRESS = PalSet_Maps

PRG_SIZE = 0x2000
PALETTE_PRG_NO = 22

PALETTE_BASE_ADDRESS = BASE_OFFSET + PALETTE_PRG_NO * PRG_SIZE
PALETTE_OFFSET_LIST = Palette_By_Tileset
PALETTE_OFFSET_SIZE = 2  # bytes

PALETTE_GROUPS_PER_OBJECT_SET = 8
ENEMY_PALETTE_GROUPS_PER_OBJECT_SET = 4
PALETTES_PER_PALETTES_GROUP = 4

COLORS_PER_PALETTE = 4
COLOR_SIZE = 1  # byte

PALETTE_DATA_SIZE = (
    (PALETTE_GROUPS_PER_OBJECT_SET + ENEMY_PALETTE_GROUPS_PER_OBJECT_SET)
    * PALETTES_PER_PALETTES_GROUP
    * COLORS_PER_PALETTE
)


@dataclass(eq=False)
class PaletteGroup:
    object_set: int
    index: int
    palettes: List[bytearray]

    changed = False

    def restore(self):
        new_palette_group = load_palette_group(self.object_set, self.index, use_cache=False)

        self.palettes = new_palette_group.palettes

    def __getitem__(self, item):
        return self.palettes[item]

    def __setitem__(self, key, value):
        self.palettes[key] = value

    def __eq__(self, other):
        if not isinstance(other, PaletteGroup):
            raise TypeError(f"Cannot compare PaletteGroup with {type(other)}.")

        return self.object_set == other.object_set and self.index == other.index

    def __hash__(self):
        return hash((self.object_set, self.index))

    def save(self, rom: Optional[ROM] = None):
        if rom is None:
            rom = ROM()

        palette_offset_position = PALETTE_OFFSET_LIST + (self.object_set * PALETTE_OFFSET_SIZE)
        palette_offset = rom.little_endian(palette_offset_position)

        palette_address = PALETTE_BASE_ADDRESS + palette_offset
        palette_address += self.index * PALETTES_PER_PALETTES_GROUP * COLORS_PER_PALETTE

        palettes = []

        for palette in self.palettes:
            palettes.append(rom.write(palette_address, palette))

            palette_address += COLORS_PER_PALETTE


_palette_group_cache: Dict[Tuple[int, int], PaletteGroup] = {}


def load_palette_group(object_set: int, palette_group_index: int, use_cache=True) -> PaletteGroup:
    """
    Basically does, what the Setup_PalData routine does.

    :param object_set: Level_Tileset in the disassembly.
    :param palette_group_index: Palette_By_Tileset. Defined in the level header.
    :param use_cache: Whether to use a cached version, or read from ROM.

    :return: A list of 4 groups of 4 colors.
    """
    key = (object_set, palette_group_index)

    if key not in _palette_group_cache or not use_cache:
        rom = ROM()

        palette_offset_position = PALETTE_OFFSET_LIST + (object_set * PALETTE_OFFSET_SIZE)
        palette_offset = rom.little_endian(palette_offset_position)

        palette_address = PALETTE_BASE_ADDRESS + palette_offset
        palette_address += palette_group_index * PALETTES_PER_PALETTES_GROUP * COLORS_PER_PALETTE

        palettes = []

        for _ in range(PALETTES_PER_PALETTES_GROUP):
            palettes.append(rom.read(palette_address, COLORS_PER_PALETTE))

            palette_address += COLORS_PER_PALETTE

        _palette_group_cache[key] = PaletteGroup(object_set, palette_group_index, palettes)

    return _palette_group_cache[key]


def save_all_palette_groups(rom: Optional[ROM] = None):
    for palette_group in _palette_group_cache.values():
        palette_group.save(rom)

    if rom is None:
        PaletteGroup.changed = False


def restore_all_palettes():
    for palette_group in _palette_group_cache.values():
        palette_group.restore()

    PaletteGroup.changed = False


palette_file = root_dir.joinpath("data", "Default.pal")

with open(palette_file, "rb") as f:
    color_data = f.read()

offset = 0x18  # first color position

NESPalette = []
COLOR_COUNT = 64
BYTES_IN_COLOR = 3 + 1  # bytes + separator

for i in range(COLOR_COUNT):
    NESPalette.append(QColor(color_data[offset], color_data[offset + 1], color_data[offset + 2]))

    offset += BYTES_IN_COLOR


def bg_color_for_object_set(object_set_number: int, palette_group_index: int) -> QColor:
    palette_group = load_palette_group(object_set_number, palette_group_index)

    return bg_color_for_palette_group(palette_group)


def bg_color_for_palette_group(palette_group: PaletteGroup) -> QColor:
    return NESPalette[palette_group[0][0]]
