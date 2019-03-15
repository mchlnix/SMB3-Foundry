import wx

from Data import graphics_offsets, common_offsets, NESPalette
from tsa import load_tsa_data

PIXEL_OFFSET = 8  # both bits describing the color of a pixel are in separate 8 byte chunks at the same index

TSA_BANK_0 = 0 * 256
TSA_BANK_1 = 1 * 256
TSA_BANK_2 = 2 * 256
TSA_BANK_3 = 3 * 256

BMP_PIXEL_SIZE = 3  # bytes for the colors

OBJECT_SET_COUNT = 15
OBJECTS_PER_SET = 128


def expand_bitmap(bitmap, width, expand=1):
    new_buffer = bytearray()

    old_row_length = BMP_PIXEL_SIZE * width
    new_row_length = BMP_PIXEL_SIZE * width * expand

    for segment_start in range(0, len(bitmap), BMP_PIXEL_SIZE):
        new_buffer.extend(expand * bitmap[segment_start:segment_start + BMP_PIXEL_SIZE])

        # copy the new row, when it's finished
        if (segment_start + BMP_PIXEL_SIZE) % old_row_length == 0:
            for i in range(1, expand):
                new_buffer.extend(new_buffer[-new_row_length:])

    return bytes(new_buffer)


class Tile:
    WIDTH = 8  # pixel
    HEIGHT = 8  # pixel

    PIXEL_COUNT = WIDTH * HEIGHT
    SIZE = int(PIXEL_COUNT * 2 / 8)   # 1 pixel is defined by 2 bits

    def __init__(self, rom, object_set, object_index, palette_group, palette_index):
        if object_index < OBJECTS_PER_SET:
            self.start = graphics_offsets[object_set] + object_index * Tile.SIZE
        else:
            common_index = object_index - OBJECTS_PER_SET
            self.start = common_offsets[object_set] + common_index * Tile.SIZE

        self.palette = palette_group[palette_index]
        # self.palette = DEFAULT_PALETTE

        self.data = bytearray()
        self.pixels = bytearray()

        rom.seek(self.start)

        for _ in range(Tile.SIZE):
            self.data.append(rom.get_byte())

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

            self.pixels.extend(NESPalette[color])

    def as_bitmap(self, zoom=1):
        if zoom == 1:
            bitmap = wx.Bitmap.FromBuffer(Tile.WIDTH, Tile.HEIGHT, self.pixels)
        else:
            buffer = expand_bitmap(self.pixels, width=Tile.WIDTH, expand=zoom)

            bitmap = wx.Bitmap.FromBuffer(Tile.WIDTH * zoom, Tile.HEIGHT * zoom, buffer)

        return bitmap


class Block:
    WIDTH = 2 * Tile.WIDTH
    HEIGHT = 2 * Tile.HEIGHT

    PIXEL_COUNT = WIDTH * HEIGHT

    tsa_data = []

    def __init__(self, rom, object_set, block_index, palette_group):
        if not Block.tsa_data:
            for os in range(OBJECT_SET_COUNT):
                Block.tsa_data.append(load_tsa_data(rom, os))

        palette_index = block_index // 0x40

        tsa_data = Block.tsa_data[object_set]

        lu = tsa_data[TSA_BANK_0 + block_index]
        ld = tsa_data[TSA_BANK_1 + block_index]
        ru = tsa_data[TSA_BANK_2 + block_index]
        rd = tsa_data[TSA_BANK_3 + block_index]

        self.lu_tile = Tile(rom, object_set, lu, palette_group, palette_index)

        self.ru_tile = Tile(rom, object_set, ru, palette_group, palette_index)

        self.ld_tile = Tile(rom, object_set, ld, palette_group, palette_index)

        self.rd_tile = Tile(rom, object_set, rd, palette_group, palette_index)

    def draw(self, dc, x, y, zoom=2):
        dc.DrawBitmap(self.lu_tile.as_bitmap(zoom), x, y)
        dc.DrawBitmap(self.ru_tile.as_bitmap(zoom), x + zoom * Tile.WIDTH, y)
        dc.DrawBitmap(self.ld_tile.as_bitmap(zoom), x, y + zoom * Tile.HEIGHT)
        dc.DrawBitmap(self.rd_tile.as_bitmap(zoom), x + zoom * Tile.WIDTH, y + zoom * Tile.HEIGHT)
