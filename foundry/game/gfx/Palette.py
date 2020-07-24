from typing import List, Tuple, Union
from collections import namedtuple
import yaml
from yaml import CLoader

from PySide2.QtGui import QColor

from foundry import root_dir
from foundry.game.File import ROM
from smb3parse.levels import BASE_OFFSET

MAP_PALETTE_ADDRESS = 0x36BE2

PALETTE_BASE_ADDRESS = BASE_OFFSET + 0x2C000
PALETTE_OFFSET_LIST = BASE_OFFSET + 0x377D2
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


palette_file = root_dir.joinpath("data", "palette.yaml")


Color = namedtuple("Color", "red green blue")
Palette = namedtuple("Palette", "color_0 color_1 color_2 color_3")
PaletteSet = namedtuple("PaletteSet", "palette_0 palette_1 palette_2 palette_3")


_NES_PAL_CONTROLLER = None


def _load_nes_colors():
    with open(palette_file) as f:
        d = yaml.load(f, Loader=CLoader)
    return {idx: Color(c["red"], c["green"], c["blue"]) for idx, c in enumerate(d)}


def load_palette_group(palette_set: Union[List[Palette], Tuple[Palette]]) -> PaletteSet:
    """Loads a palette group from a list of lists"""
    try:
        return PaletteSet(*palette_set[0:4])
    except IndexError as e:
        print(e, f"Not a valid length for a palette set: {palette_set}")


class PaletteController:
    """A singleton that contains important NES palette information"""
    def __new__(cls, *args, **kwargs) -> "PaletteController":
        global _NES_PAL_CONTROLLER
        if _NES_PAL_CONTROLLER is None:
            _NES_PAL_CONTROLLER = super().__new__(cls, *args, **kwargs)
            _NES_PAL_CONTROLLER.colors = _load_nes_colors()
        return _NES_PAL_CONTROLLER

    def get_qcolor(self, color_idx: int) -> QColor:
        """Converts the color to a qcolor"""
        return QColor(self.colors[color_idx][0], self.colors[color_idx][1], self.colors[color_idx][2])


def load_palette(object_set: int, palette_group: int) -> PaletteSet:
    """
    :param object_set: Level_Tileset in the disassembly.
    :param palette_group: Palette_By_Tileset. Defined in the level header.
    :return: Returns a struct
    """
    rom = ROM()

    palette_offset_position = PALETTE_OFFSET_LIST + (object_set * PALETTE_OFFSET_SIZE)
    palette_offset = rom.little_endian(palette_offset_position)

    palette_address = PALETTE_BASE_ADDRESS + palette_offset
    palette_address += palette_group * PALETTES_PER_PALETTES_GROUP * COLORS_PER_PALETTE

    palettes = []

    for _ in range(PALETTES_PER_PALETTES_GROUP):
        palettes.append(Palette(*rom.read(palette_address, COLORS_PER_PALETTE)))
        palette_address += COLORS_PER_PALETTE

    return load_palette_group(palettes)


def bg_color_for_object_set(tile_set: int, palette_group_index: int) -> QColor:
    palette = load_palette(tile_set, palette_group_index)

    return QColor(*bg_color_for_palette(palette))


def bg_color_for_palette(palette_set: PaletteSet):
    """
    Gets the background color of a palette set
    :param palette_set: PaletteSet
    :return: A tuple representing the color data
    """
    return PaletteController().colors[palette_set[0][0]]
