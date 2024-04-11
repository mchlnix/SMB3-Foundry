from PySide6.QtGui import QImage

from foundry.game.gfx.drawable import MASK_COLOR, bit_reverse
from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx.Palette import NESPalette, PaletteGroup
from smb3parse.objects.object_set import CLOUDY_GRAPHICS_SET

PIXEL_OFFSET = 8  # both bits describing the color of a pixel are in separate 8 byte chunks at the same index

BACKGROUND_COLOR_INDEX = 0


class Tile:
    SIDE_LENGTH = 8  # pixel
    WIDTH = SIDE_LENGTH
    HEIGHT = SIDE_LENGTH

    PIXEL_COUNT = WIDTH * HEIGHT
    SIZE = 2 * PIXEL_COUNT // 8  # 1 pixel is defined by 2 bits

    def __init__(
        self,
        object_index: int,
        palette_group: PaletteGroup,
        palette_index: int,
        graphics_set: GraphicsSet,
        mirrored=False,
    ):
        self.tile_index = object_index

        start = object_index * Tile.SIZE

        self.cached_tiles: dict[int, QImage] = dict()

        self.palette = palette_group[palette_index]

        self.data = bytearray()
        self.pixels = bytearray()
        self.mask_pixels = bytearray()

        self.data = graphics_set.data[start : start + Tile.SIZE]

        if graphics_set.number == CLOUDY_GRAPHICS_SET:
            self.background_color_index = 2
        else:
            self.background_color_index = 0

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
            if color_index == self.background_color_index:
                self.pixels.extend(MASK_COLOR)
            else:
                self.pixels.extend(NESPalette[color].toTuple()[:3])

        assert len(self.pixels) == 3 * Tile.PIXEL_COUNT

    def as_image(self, tile_length=8):
        if True or tile_length not in self.cached_tiles:
            width = height = tile_length

            image = QImage(self.pixels, self.WIDTH, self.HEIGHT, QImage.Format_RGB888)

            image = image.scaled(width, height)

            self.cached_tiles[tile_length] = image

        return self.cached_tiles[tile_length]

    def _mirror(self):
        for byte in range(len(self.data)):
            self.data[byte] = bit_reverse[self.data[byte]]
