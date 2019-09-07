import wx

from foundry.game.gfx.Palette import NESPalette
from foundry.game.gfx.drawable import bit_reverse, MASK_COLOR

PIXEL_OFFSET = (
    8
)  # both bits describing the color of a pixel are in separate 8 byte chunks at the same index

BACKGROUND_COLOR_INDEX = 0


class Tile:
    SIDE_LENGTH = 8  # pixel
    WIDTH = SIDE_LENGTH
    HEIGHT = SIDE_LENGTH

    PIXEL_COUNT = WIDTH * HEIGHT
    SIZE = 2 * PIXEL_COUNT // 8  # 1 pixel is defined by 2 bits

    def __init__(
        self, object_index, palette_group, palette_index, pattern_table, mirrored=False
    ):
        start = object_index * Tile.SIZE

        self.cached_tiles = dict()

        self.palette = palette_group[palette_index]
        # self.palette = DEFAULT_PALETTE

        self.data = bytearray()
        self.pixels = bytearray()
        self.mask_pixels = bytearray()

        self.data = pattern_table.data[start : start + Tile.SIZE]

        if mirrored:
            self._mirror()

        for i in range(Tile.PIXEL_COUNT):
            byte_index = i // Tile.HEIGHT
            bit_index = 2 ** (7 - (i % Tile.WIDTH))

            left_bit = right_bit = 0

            if self.data[byte_index] & bit_index:
                left_bit = 1

            if self.data[PIXEL_OFFSET + byte_index] & bit_index:
                right_bit = 1

            color_index = (right_bit << 1) | left_bit

            color = self.palette[color_index]

            # add alpha values
            if color_index == BACKGROUND_COLOR_INDEX:
                self.pixels.extend(MASK_COLOR)
            else:
                self.pixels.extend(NESPalette[color])

        assert len(self.pixels) == 3 * Tile.PIXEL_COUNT

    def as_image(self, tile_length=8):
        if tile_length not in self.cached_tiles.keys():
            width = height = tile_length

            image = wx.Image()
            image.Create(Tile.WIDTH, Tile.HEIGHT, self.pixels)

            image.Rescale(width, height)

            self.cached_tiles[tile_length] = image

        return self.cached_tiles[tile_length]

    def _mirror(self):
        for byte in range(len(self.data)):
            self.data[byte] = bit_reverse[self.data[byte]]
