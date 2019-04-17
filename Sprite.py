import wx

from Data import NESPalette
from tsa import load_tsa_data

PIXEL_OFFSET = 8  # both bits describing the color of a pixel are in separate 8 byte chunks at the same index

TSA_BANK_0 = 0 * 256
TSA_BANK_1 = 1 * 256
TSA_BANK_2 = 2 * 256
TSA_BANK_3 = 3 * 256

OBJECT_SET_COUNT = 16
OBJECTS_PER_SET = 128

BACKGROUND_COLOR_INDEX = 0
MASK_COLOR = [0xFF, 0x00, 0xFF]


class Tile:
    WIDTH = 8  # pixel
    HEIGHT = 8  # pixel

    PIXEL_COUNT = WIDTH * HEIGHT
    SIZE = 2 * PIXEL_COUNT // 8   # 1 pixel is defined by 2 bits

    def __init__(self, rom, object_set, object_index, palette_group, palette_index, pattern_table):
        start = object_index * Tile.SIZE

        self.cached_tiles = dict()

        self.palette = palette_group[palette_index]
        # self.palette = DEFAULT_PALETTE

        self.data = bytearray()
        self.pixels = bytearray()
        self.mask_pixels = bytearray()

        self.data = pattern_table.data[start:start + Tile.SIZE]

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

    def as_image(self, zoom=1):
        if zoom not in self.cached_tiles.keys():
            width = Tile.WIDTH * zoom
            height = Tile.HEIGHT * zoom

            image = wx.Image()
            image.Create(Tile.WIDTH, Tile.HEIGHT, self.pixels)

            image.Rescale(width, height)

            self.cached_tiles[zoom] = image

        return self.cached_tiles[zoom]

    def as_bitmap(self, zoom=1):
        return self.as_image(zoom).ConvertToBitmap()


class Block:
    WIDTH = 2 * Tile.WIDTH
    HEIGHT = 2 * Tile.HEIGHT

    PIXEL_COUNT = WIDTH * HEIGHT

    tsa_data = []

    def __init__(self, rom, object_set, block_index, palette_group, pattern_table):
        if not Block.tsa_data:
            for os in range(OBJECT_SET_COUNT):
                Block.tsa_data.append(load_tsa_data(rom, os))

        palette_index = (block_index & 0b1100_0000) >> 6

        self.bg_color = NESPalette[palette_group[palette_index][0]]

        tsa_data = Block.tsa_data[object_set]

        lu = tsa_data[TSA_BANK_0 + block_index]
        ld = tsa_data[TSA_BANK_1 + block_index]
        ru = tsa_data[TSA_BANK_2 + block_index]
        rd = tsa_data[TSA_BANK_3 + block_index]

        self.lu_tile = Tile(rom, object_set, lu, palette_group, palette_index, pattern_table)
        self.ru_tile = Tile(rom, object_set, ru, palette_group, palette_index, pattern_table)
        self.ld_tile = Tile(rom, object_set, ld, palette_group, palette_index, pattern_table)
        self.rd_tile = Tile(rom, object_set, rd, palette_group, palette_index, pattern_table)

        self.image = wx.Image(Block.WIDTH, Block.HEIGHT)

        self.image.Paste(self.lu_tile.as_image(), 0, 0)
        self.image.Paste(self.ru_tile.as_image(), Tile.WIDTH, 0)
        self.image.Paste(self.ld_tile.as_image(), 0, Tile.HEIGHT)
        self.image.Paste(self.rd_tile.as_image(), Tile.WIDTH, Tile.HEIGHT)

        self.image.SetMaskColour(*MASK_COLOR)

    def draw(self, dc, x, y, zoom=1, selected=False, transparent=False):
        image = self.image.Copy()

        if zoom > 1:
            image.Rescale(Block.WIDTH * zoom, Block.HEIGHT * zoom)

        # todo better effect
        if selected:
            image = image.ConvertToDisabled(127)

        if not transparent:
            image.Replace(*MASK_COLOR, *self.bg_color)

        dc.DrawBitmap(image.ConvertToBitmap(), x, y, useMask=transparent)
