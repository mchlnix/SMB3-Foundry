from typing import List, Tuple, Union, NamedTuple, Optional
from dataclasses import dataclass
import yaml
from yaml import CLoader

from PySide2.QtGui import QColor

from smb3parse.asm6_converter import to_hex

from foundry import root_dir
from foundry.game.File import ROM
from foundry.core.util import ROM_HEADER_OFFSET

PALETTE_BASE_ADDRESS = ROM_HEADER_OFFSET + 0x2C000
PALETTE_OFFSET_LIST = ROM_HEADER_OFFSET + 0x377D2
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

palette_file = root_dir.joinpath("data", "palette.yaml")


class Color(NamedTuple):
    """Defines a color"""
    red: int
    green: int
    blue: int

    def __str__(self) -> str:
        return f"{self.red}, {self.green}, {self.blue}"

    @property
    def nes_index(self) -> Optional[int]:
        """Returns the estimated index of the color in terms of the NES palette"""
        return PaletteController().get_index_from_color(self)

    @property
    def nes_str(self) -> str:
        """Returns the color as a NES string"""
        return to_hex(self.nes_index)

@dataclass
class Palette:
    """Defines a basic palette"""
    color_0: Color
    color_1: Color
    color_2: Color
    color_3: Color

    def __str__(self) -> str:
        return f"({self[0]}),({self[1]}),({self[2]}),({self[3]})"

    @property
    def nes_str(self) -> str:
        """Defines the palette as a NES palette string"""
        return f"{self[0].nes_str},{self[1].nes_str},{self[2].nes_str},{self[3].nes_str}"

    def __getitem__(self, item: int) -> Color:
        if item == 0:
            return self.color_0
        elif item == 1:
            return self.color_1
        elif item == 2:
            return self.color_2
        elif item == 3:
            return self.color_3
        else:
            raise NotImplementedError

    def __setitem__(self, key: int, value: Color):
        if key == 0:
            self.color_0 = value
        elif key == 1:
            self.color_1 = value
        elif key == 2:
            self.color_2 = value
        elif key == 3:
            self.color_3 = value
        else:
            raise NotImplementedError


@dataclass
class PaletteSet:
    """Defines a set of palettes"""
    palette_0: Palette
    palette_1: Palette
    palette_2: Palette
    palette_3: Palette

    def __str__(self) -> str:
        return f"({self[0]}),({self[1]}),({self[2]}),({self[3]})"

    @property
    def nes_str(self) -> str:
        """Defines the palette set as a NES palette set string"""
        return f"({self[0].nes_str}),({self[1].nes_str}),({self[2].nes_str}),({self[3].nes_str})"

    def __getitem__(self, item: int) -> Palette:
        if item == 0:
            return self.palette_0
        elif item == 1:
            return self.palette_1
        elif item == 2:
            return self.palette_2
        elif item == 3:
            return self.palette_3
        else:
            raise NotImplementedError

    def __setitem__(self, key: int, value: Palette) -> None:
        if key == 0:
            self.palette_0 = value
        elif key == 1:
            self.palette_1 = value
        elif key == 2:
            self.palette_2 = value
        elif key == 3:
            self.palette_3 = value
        else:
            raise NotImplementedError

    @property
    def background_color(self) -> Color:
        """The background color of the palette"""
        return self.palette_0.color_0

    @background_color.setter
    def background_color(self, color: Color) -> None:
        self.palette_0.color_0 = color


_NES_PAL_CONTROLLER = None


def _load_nes_colors():
    with open(palette_file) as f:
        d = yaml.load(f, Loader=CLoader)
    return {idx: Color(c["red"], c["green"], c["blue"]) for idx, c in enumerate(d)}


def _load_nes_colors_inverse():
    with open(palette_file) as f:
        d = yaml.load(f, Loader=CLoader)
    return {Color(c["red"], c["green"], c["blue"]): idx for idx, c in enumerate(d)}


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
            _NES_PAL_CONTROLLER.colors_inverse = _load_nes_colors_inverse()
        return _NES_PAL_CONTROLLER

    def get_qcolor(self, color_idx: int) -> QColor:
        """Converts the color to a qcolor"""
        return QColor(self.colors[color_idx][0], self.colors[color_idx][1], self.colors[color_idx][2])

    def get_index_from_color(self, color: Color) -> Optional[int]:
        """Provides an approximate index for a given color into the NES palette"""
        for i, c in enumerate(self.colors.values()):
            if c == color:
                return i
        return None


def load_palette(object_set: int, palette_group: int) -> PaletteSet:
    """
    :param object_set: Level_Tileset in the disassembly.
    :param palette_group: Palette_By_Tileset. Defined in the level header.
    :return: Returns a struct
    """
    rom = ROM()

    palette_pointer = PALETTE_OFFSET_LIST + (object_set * PALETTE_OFFSET_SIZE)
    palette_offset = rom.little_endian(palette_pointer)

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
