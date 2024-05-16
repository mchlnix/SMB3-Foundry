from contextlib import suppress
from dataclasses import dataclass
from typing import Optional

from PySide6.QtGui import QColor

from foundry import root_dir
from foundry.game.File import ROM
from foundry.gui.util import grouper
from smb3parse.constants import Constants
from smb3parse.levels import BASE_OFFSET
from smb3parse.util.rom import PRG_BANK_SIZE, Rom

PALETTE_PRG_NO = 22

PALETTE_BASE_ADDRESS = BASE_OFFSET + PALETTE_PRG_NO * PRG_BANK_SIZE
PALETTE_OFFSET_LIST_JP = 0x374AB  # found by searching through the JP ROM, calculating backwards to find the offset list
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

color_data = root_dir.joinpath("data", "Default.pal").read_bytes()

NES_COLOR_COUNT = 64
BYTES_IN_COLOR = 3 + 1  # bytes + separator
assert len(color_data) == NES_COLOR_COUNT * BYTES_IN_COLOR, (
    len(color_data),
    NES_COLOR_COUNT * BYTES_IN_COLOR,
)

NESPalette = [QColor(r, g, b) for r, g, b, _ in grouper(color_data, 4, incomplete="strict")]


@dataclass(eq=False)
class PaletteGroup:
    """
    A PaletteGroup comprises four palettes of four color values.
    These color values are indexes pointing into the palette of the NES, which consists of 64 hardcoded colors.
    """

    _object_set: int
    index: int  # needed for cache keys outside
    _offset: int
    _palettes: list[bytearray]

    changed = False

    def restore(self):
        new_palette_group = load_palette_group(self._object_set, self.index, use_cache=False)

        self._palettes = new_palette_group._palettes

    def __getitem__(self, item):
        return self._palettes[item]

    def __setitem__(self, key, value):
        self._palettes[key] = value

    def __eq__(self, other):
        if not isinstance(other, PaletteGroup):
            raise TypeError(f"Cannot compare PaletteGroup with {type(other)}.")

        return hash(self) == hash(other)

    def __hash__(self):
        return hash((self._object_set, self.index))

    def save(self, rom: Optional[Rom] = None):
        if rom is None:
            rom = ROM()

        palette_offset_position = self._offset + (self._object_set * PALETTE_OFFSET_SIZE)
        palette_offset = rom.little_endian(palette_offset_position)

        palette_address = PALETTE_BASE_ADDRESS + palette_offset
        palette_address += self.index * PALETTES_PER_PALETTES_GROUP * COLORS_PER_PALETTE

        palettes = []

        for palette in self._palettes:
            palettes.append(rom.write(palette_address, palette))

            palette_address += COLORS_PER_PALETTE


_palette_group_cache: dict[tuple[int, int], PaletteGroup] = {}


def load_palette_group(object_set: int, palette_group_index: int, use_cache=True) -> PaletteGroup:
    """
    Basically does, what the Setup_PalData routine does.

    :param object_set: Level_Tileset in the disassembly.
    :param palette_group_index: Palette_By_Tileset. Defined in the level header.
    :param use_cache: Whether to use a cached version, or read from ROM.

    :return: A list of 4 groups of 4 colors.
    """
    key = (object_set, palette_group_index)

    if use_cache and key in _palette_group_cache:
        return _palette_group_cache[key]

    # the data is in different locations for US and JP roms
    for palette_offset_list in (Constants.Palette_By_Tileset, PALETTE_OFFSET_LIST_JP):
        # ignore ValueError when we don't find valid palette data, might be the other version
        with suppress(ValueError):
            palettes = _load_palettes_from_rom(object_set, palette_group_index, palette_offset_list)
            _palette_group_cache[key] = PaletteGroup(object_set, palette_group_index, palette_offset_list, palettes)

            return _palette_group_cache[key]
    else:
        raise ValueError("Couldn't find valid Palette data at offsets for stock US or stock JP ROM.")


def _load_palettes_from_rom(object_set, palette_group_index, palette_offset_list_address: int):
    rom = ROM()

    palette_offset_position = palette_offset_list_address + (object_set * PALETTE_OFFSET_SIZE)
    palette_offset = rom.little_endian(palette_offset_position)

    palette_address = PALETTE_BASE_ADDRESS + palette_offset
    palette_address += palette_group_index * PALETTES_PER_PALETTES_GROUP * COLORS_PER_PALETTE

    palettes = []

    for _ in range(PALETTES_PER_PALETTES_GROUP):
        palettes.append(bytearray(rom.read(palette_address, COLORS_PER_PALETTE)))

        palette_address += COLORS_PER_PALETTE

    # There are 64 colors in the NES's palette. Any other value indicates, that we did not find the right palette data
    if not all(color_index in range(NES_COLOR_COUNT) for palette in palettes for color_index in palette):
        raise ValueError("Found invalid Palette index value. Probably didn't find correct Palette Data in ROM.")

    return palettes


def save_all_palette_groups(rom: Optional[Rom] = None):
    for palette_group in _palette_group_cache.values():
        palette_group.save(rom)

    if rom is None:
        PaletteGroup.changed = False


def bg_color_for_object_set(object_set_number: int, palette_group_index: int) -> QColor:
    palette_group = load_palette_group(object_set_number, palette_group_index)

    return bg_color_for_palette_group(palette_group)


def bg_color_for_palette_group(palette_group: PaletteGroup) -> QColor:
    return NESPalette[palette_group[0][0]]
