"""
This module contains default palettes and colors for testing functionality
DEFAULT_COLOR: A default color
DEFAULT_PALETTE: A default palette
DEFAULT_PALETTE_SET: A default palette set
"""

from foundry.game.gfx.Palette import PaletteController, PaletteSet, Palette


_colors = PaletteController().colors

DEFAULT_COLOR = _colors[0]

DEFAULT_PALETTE = Palette(
    _colors[0], _colors[1], _colors[2], _colors[3]
)

DEFAULT_PALETTE_SET = PaletteSet(
    Palette(_colors[0], _colors[1], _colors[2], _colors[3]),
    Palette(_colors[4], _colors[5], _colors[6], _colors[7]),
    Palette(_colors[8], _colors[9], _colors[10], _colors[11]),
    Palette(_colors[12], _colors[13], _colors[14], _colors[15])
)