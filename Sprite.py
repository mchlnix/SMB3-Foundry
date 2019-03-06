import wx

TILE_MEMORY_OFFSET = 0x40010
TILE_HEIGHT = 8
TILE_WIDTH = 8
TILE_PIXEL_COUNT = TILE_HEIGHT * TILE_WIDTH
TILE_SIZE = int(TILE_PIXEL_COUNT * 2 / 8)  # pixel * pixel * 2 bit
PIXEL_OFFSET = 8  # both bits describing the color of a pixel are in separate 8 byte chunks at the same index

DEFAULT_PALETTE = {
    0b00: bytes([0xF7, 0xD8, 0xA5]),  # background
    0b01: bytes([0xFE, 0xCC, 0xC5]),
    0b10: bytes([0xB5, 0x31, 0x20]),
    0b11: bytes([0x00, 0x00, 0x00]),
}


class Tile:
    def __init__(self, rom, offset, palette=DEFAULT_PALETTE):
        self.start = TILE_MEMORY_OFFSET + offset
        self.palette = palette
        self.data = bytearray()
        self.pixels = bytearray()

        rom.seek(self.start)

        for _ in range(TILE_SIZE):
            self.data.append(rom.get_byte())

        for i in range(TILE_PIXEL_COUNT):
            byte_index = i // 8
            bit_index = 2 ** (i % 8)

            left_bit = right_bit = 0

            if self.data[byte_index] & bit_index: left_bit = 1
            if self.data[PIXEL_OFFSET + byte_index] & bit_index: right_bit = 1

            palette_value = (left_bit << 1) | right_bit

            color = self.palette[palette_value]

            self.pixels.extend(color)

    def as_bitmap(self):
        bitmap = wx.Bitmap.FromBuffer(TILE_WIDTH, TILE_HEIGHT, self.pixels)

        return bitmap


class SpriteSheet(wx.Bitmap):
    def __init__(self, source, sprite_width=16, sprite_height=16, *args, **kwargs):
        super(SpriteSheet, self).__init__(*args, **kwargs)

        self.source = wx.Bitmap(source)
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height

        self.sprite_cache = dict()

    def get_sprite(self, x, y, width=None, height=None):
        if width is None:
            width = self.sprite_width

        if height is None:
            height = self.sprite_height

        x, y = x * self.sprite_width, y * self.sprite_height

        key = (x, y, width, height)

        if key not in self.sprite_cache:
            cut_out = wx.Rect(*key)

            new_bitmap = self.source.GetSubBitmap(cut_out)

            self.sprite_cache[key] = new_bitmap

        return self.sprite_cache[key]
