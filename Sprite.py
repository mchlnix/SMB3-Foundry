import wx

from Data import graphics_offsets, common_offsets, NESPalette
from tsa import load_tsa_data

PIXEL_OFFSET = 8  # both bits describing the color of a pixel are in separate 8 byte chunks at the same index

TSA_BANK_0 = 0 * 256
TSA_BANK_1 = 1 * 256
TSA_BANK_2 = 2 * 256
TSA_BANK_3 = 3 * 256

OBJECT_SET_COUNT = 16
OBJECTS_PER_SET = 128

BACKGROUND_COLOR_INDEX = 0
MASK_COLOR_VISIBLE = [0xFF] * 3
MASK_COLOR_HIDDEN = [0x00] * 3


class Tile:
    WIDTH = 8  # pixel
    HEIGHT = 8  # pixel

    PIXEL_COUNT = WIDTH * HEIGHT
    SIZE = 2 * PIXEL_COUNT // 8   # 1 pixel is defined by 2 bits

    def __init__(self, rom, object_set, object_index, palette_group, palette_index, graphis_offset=None, common_offset=None):
        if graphis_offset is None:
            graphis_offset = graphics_offsets[object_set]

        if common_offset is None:
            common_offset = common_offsets[object_set]

        if object_index < OBJECTS_PER_SET:
            self.start = graphis_offset + object_index * Tile.SIZE
        else:
            common_index = object_index - OBJECTS_PER_SET
            self.start = common_offset + common_index * Tile.SIZE

        self.cached_tiles = dict()

        self.palette = palette_group[palette_index]
        # self.palette = DEFAULT_PALETTE

        self.data = bytearray()
        self.pixels = bytearray()
        self.mask_pixels = bytearray()

        rom.seek(self.start)

        self.data = rom.bulk_read(Tile.SIZE)

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
                self.mask_pixels.extend(MASK_COLOR_HIDDEN)
            else:
                self.mask_pixels.extend(MASK_COLOR_VISIBLE)

            self.pixels.extend(NESPalette[color])

        assert len(self.pixels) == 3 * Tile.PIXEL_COUNT

    def as_image(self, zoom=1):
        if zoom not in self.cached_tiles.keys():
            width = Tile.WIDTH * zoom
            height = Tile.HEIGHT * zoom

            image = wx.Image()
            image.Create(Tile.WIDTH, Tile.HEIGHT, self.pixels)

            mask = wx.Image()
            mask.Create(Tile.WIDTH, Tile.HEIGHT, self.mask_pixels)

            image.SetMaskFromImage(mask, *MASK_COLOR_HIDDEN)

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

    def __init__(self, rom, object_set, block_index, palette_group, graphic_offset=None, common_offset=None):
        if not Block.tsa_data:
            for os in range(OBJECT_SET_COUNT):
                Block.tsa_data.append(load_tsa_data(rom, os))

        palette_index = (block_index & 0b1100_0000) >> 6

        tsa_data = Block.tsa_data[object_set]

        lu = tsa_data[TSA_BANK_0 + block_index]
        ld = tsa_data[TSA_BANK_1 + block_index]
        ru = tsa_data[TSA_BANK_2 + block_index]
        rd = tsa_data[TSA_BANK_3 + block_index]

        self.lu_tile = Tile(rom, object_set, lu, palette_group, palette_index, graphic_offset, common_offset)

        self.ru_tile = Tile(rom, object_set, ru, palette_group, palette_index, graphic_offset, common_offset)

        self.ld_tile = Tile(rom, object_set, ld, palette_group, palette_index, graphic_offset, common_offset)

        self.rd_tile = Tile(rom, object_set, rd, palette_group, palette_index, graphic_offset, common_offset)

        self.image = wx.Image(Block.WIDTH, Block.HEIGHT)
        self.image.SetMask(True)

        self.image.Paste(self.lu_tile.as_image(), 0, 0)
        self.image.Paste(self.ru_tile.as_image(), Tile.WIDTH, 0)
        self.image.Paste(self.ld_tile.as_image(), 0, Tile.HEIGHT)
        self.image.Paste(self.rd_tile.as_image(), Tile.WIDTH, Tile.HEIGHT)

    def draw(self, dc, x, y, zoom=1):
        if zoom > 1:
            image = self.image.Copy()
            image.Rescale(Block.WIDTH * zoom, Block.HEIGHT * zoom)
        else:
            image = self.image

        dc.DrawBitmap(image.ConvertToBitmap(), x, y, useMask=True)
