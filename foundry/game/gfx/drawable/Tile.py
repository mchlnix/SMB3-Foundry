"""Decode SMB3 CHR tiles into editor-ready pixel data.

This module is the lowest-level drawable surface in Foundry's rendering stack.
It turns one 16-byte NES pattern-table tile plus palette state into RGB pixel
bytes that higher-level blocks and object renderers can reuse.

See Also
--------
foundry.game.gfx.GraphicsSet
    Supplies the CHR bytes that this module decodes.
foundry.game.gfx.drawable.Block
    Composes decoded tiles into 16x16 TSA-backed blocks.
"""

from foundry.game.gfx.drawable import MASK_COLOR
from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx.Palette import NESPalette, PaletteGroup
from smb3parse.constants import CLOUDY_GRAPHICS_SET

BITS_IN_BYTE = 8

BITS_PER_COLOR = 2  # 1 pixel needs 2 bits to represent one of 4 possible color indexes

PIXEL_OFFSET = 8  # both bits describing the color of a pixel are in separate 8 byte chunks at the same index

BACKGROUND_COLOR_INDEX = 0


class Tile:
    """Represent one decoded NES 8x8 CHR tile.

    NES pattern-table graphics store each tile as two 8-byte bitplanes. Foundry
    combines those bitplanes into 64 two-bit palette indexes, then resolves each
    index through the selected SMB3 palette row before drawing blocks and object
    previews.

    Parameters
    ----------
    tile_index : int
        Tile number within the active graphics set.
    palette_group : PaletteGroup
        Four palette rows selected by the level object set and header.
    palette_index : int
        Palette row within ``palette_group`` used to resolve the tile's two-bit
        color indexes.
    graphics_set : GraphicsSet
        CHR data source for the tile bytes.

    Attributes
    ----------
    HEIGHT : int
        Tile height in pixels.
    PIXEL_COUNT : int
        Number of pixels decoded from the 8x8 CHR tile.
    SIDE_LENGTH : int
        Tile side length in pixels.
    SIZE : int
        Number of bytes in the NES bitplane representation.
    WIDTH : int
        Tile width in pixels.
    _background_color_index : int
        Palette entry that Foundry treats as transparent mask color.
    _data : bytearray
        Raw 16-byte CHR bitplane data for this tile.
    _mask_pixels : bytearray
        Reserved mask byte buffer for callers that need per-pixel transparency.
    _palette : bytearray
        Four NES color indexes used to resolve the tile's pixel indexes.
    pixels : bytearray
        RGB byte stream used to construct the Qt image for this tile.
    tile_index : int
        Tile number within the active graphics set.

    Examples
    --------
    A renderer typically creates ``Tile`` indirectly through ``Block``, but
    the data flow is ``GraphicsSet`` and ``PaletteGroup`` -> ``Tile`` ->
    RGB bytes for Qt drawing. For a single decoded tile, the constructor keeps
    the original tile index alongside a 64-pixel RGB byte stream that block
    rendering can hand to Qt.
    """

    SIDE_LENGTH = 8  # pixel
    WIDTH = SIDE_LENGTH
    HEIGHT = SIDE_LENGTH

    PIXEL_COUNT = WIDTH * HEIGHT
    SIZE = BITS_PER_COLOR * PIXEL_COUNT // BITS_IN_BYTE  # in bytes

    def __init__(
        self,
        tile_index: int,
        palette_group: PaletteGroup,
        palette_index: int,
        graphics_set: GraphicsSet,
    ):
        """Decode an NES CHR tile into RGB pixel bytes.

        The constructor reads the tile's 16 pattern bytes from the graphics set,
        combines the paired bitplanes into color indexes 0 through 3, and maps
        non-background pixels through ``NESPalette``. Background pixels are
        emitted as ``MASK_COLOR`` so the block renderer can later restore
        transparency or fill with the level backdrop color.

        Parameters
        ----------
        tile_index : int
            Tile number within the active graphics set.
        palette_group : PaletteGroup
            Four palette rows selected by the level object set and header.
        palette_index : int
            Palette row within ``palette_group`` used to resolve pixel indexes.
        graphics_set : GraphicsSet
            CHR data source for the tile bytes.

        Examples
        --------
        The constructor decodes one 16-byte CHR tile from two bitplanes. This
        example feeds a single tile whose first pixel resolves to color index 1
        and leaves the rest of the tile as background mask color:

        >>> class StubGraphicsSet:
        ...     number = 0
        ...     data = bytes([0b10000000] + [0] * 15)
        >>> palette_group = [[0x0F, 0x01, 0x21, 0x31]]
        >>> tile = Tile(0, palette_group, 0, StubGraphicsSet())
        >>> tile.tile_index
        0
        >>> len(tile.pixels) == 3 * Tile.PIXEL_COUNT
        True
        >>> tile.pixels[:3] == bytearray(NESPalette[0x01].toTuple()[:3])
        True
        >>> tile.pixels[3:6] == bytearray(MASK_COLOR)
        True
        """
        self.tile_index = tile_index

        start = tile_index * Tile.SIZE

        self._palette = palette_group[palette_index]

        self._data = bytearray()
        self.pixels = bytearray()
        self._mask_pixels = bytearray()

        self._data = graphics_set.data[start : start + Tile.SIZE]

        if graphics_set.number == CLOUDY_GRAPHICS_SET:
            self._background_color_index = 2
        else:
            self._background_color_index = 0

        for i in range(Tile.PIXEL_COUNT):
            byte_index = i // Tile.HEIGHT
            bit_index = 2 ** (7 - (i % Tile.WIDTH))

            left_bit = right_bit = 0

            if self._data[byte_index] & bit_index:
                left_bit = 1

            if self._data[PIXEL_OFFSET + byte_index] & bit_index:
                right_bit = 1

            color_index = (right_bit << 1) | left_bit

            color = self._palette[color_index]

            # add alpha values
            if color_index == self._background_color_index:
                self.pixels.extend(MASK_COLOR)
            else:
                self.pixels.extend(NESPalette[color].toTuple()[:3])

        assert len(self.pixels) == 3 * Tile.PIXEL_COUNT
