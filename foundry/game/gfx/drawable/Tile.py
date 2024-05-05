from PySide6.QtGui import QImage

from foundry.game.gfx.drawable import MASK_COLOR
from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx.Palette import NESPalette, PaletteGroup
from smb3parse.objects.object_set import CLOUDY_GRAPHICS_SET

PIXEL_OFFSET = 8  # both bits describing the color of a pixel are in separate 8 byte chunks at the same index

BACKGROUND_COLOR_INDEX = 0


class Tile:
    """
    A Tile is an 8x8 square of pixels.
    Instead of the pixels representing a specific color value, it instead represents an index of a color.
    Which color the pixel will actually be in the end depends on the palette of a PaletteGroup the tile is assigned.
    """

    SIDE_LENGTH = 8  # pixel
    WIDTH = SIDE_LENGTH
    HEIGHT = SIDE_LENGTH

    PIXEL_COUNT = WIDTH * HEIGHT
    SIZE = 2 * PIXEL_COUNT // 8  # in bytes; 1 pixel needs 2 bits to represent one of 4 possible color indexes

    def __init__(
        self,
        tile_index: int,
        palette_group: PaletteGroup,
        palette_index: int,
        graphics_set: GraphicsSet,
    ):
        self.tile_index = tile_index

        start = tile_index * Tile.SIZE

        self._cached_tiles: dict[int, QImage] = dict()

        self._palette = palette_group[palette_index]

        self._data = bytearray()
        self._pixels = bytearray()
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
                self._pixels.extend(MASK_COLOR)
            else:
                self._pixels.extend(NESPalette[color].toTuple()[:3])

        assert len(self._pixels) == 3 * Tile.PIXEL_COUNT

    def as_image(self, tile_length=8):
        # why did we put a True here, foregoing the cache? Doesn't slow the test suite down, though.
        if True or tile_length not in self._cached_tiles:
            width = height = tile_length

            image = QImage(self._pixels, self.WIDTH, self.HEIGHT, QImage.Format_RGB888)

            image = image.scaled(width, height)

            self._cached_tiles[tile_length] = image

        return self._cached_tiles[tile_length]
