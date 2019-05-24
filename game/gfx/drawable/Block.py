import wx

from Data import NESPalette
from game.gfx.drawable import MASK_COLOR
from game.gfx.drawable.Tile import Tile

TSA_BANK_0 = 0 * 256
TSA_BANK_1 = 1 * 256
TSA_BANK_2 = 2 * 256
TSA_BANK_3 = 3 * 256


class Block:
    SIDE_LENGTH = 2 * Tile.SIDE_LENGTH
    WIDTH = SIDE_LENGTH
    HEIGHT = SIDE_LENGTH

    PIXEL_COUNT = WIDTH * HEIGHT

    tsa_data = []

    def __init__(
        self, block_index, palette_group, pattern_table, tsa_data, mirrored=False
    ):

        self.index = block_index

        palette_index = (block_index & 0b1100_0000) >> 6

        self.bg_color = NESPalette[palette_group[palette_index][0]]

        lu = tsa_data[TSA_BANK_0 + block_index]
        ld = tsa_data[TSA_BANK_1 + block_index]
        ru = tsa_data[TSA_BANK_2 + block_index]
        rd = tsa_data[TSA_BANK_3 + block_index]

        self.lu_tile = Tile(lu, palette_group, palette_index, pattern_table)
        self.ld_tile = Tile(ld, palette_group, palette_index, pattern_table)

        if mirrored:
            self.ru_tile = Tile(
                lu, palette_group, palette_index, pattern_table, mirrored=True
            )
            self.rd_tile = Tile(
                ld, palette_group, palette_index, pattern_table, mirrored=True
            )
        else:
            self.ru_tile = Tile(ru, palette_group, palette_index, pattern_table)
            self.rd_tile = Tile(rd, palette_group, palette_index, pattern_table)

        self.image = wx.Image(Block.WIDTH, Block.HEIGHT)

        self.image.Paste(self.lu_tile.as_image(), 0, 0)
        self.image.Paste(self.ru_tile.as_image(), Tile.WIDTH, 0)
        self.image.Paste(self.ld_tile.as_image(), 0, Tile.HEIGHT)
        self.image.Paste(self.rd_tile.as_image(), Tile.WIDTH, Tile.HEIGHT)

        self.image.SetMaskColour(*MASK_COLOR)

    def draw(self, dc, x, y, block_length, selected=False, transparent=False):
        image = self.image.Copy()

        if block_length != Block.WIDTH:
            image.Rescale(block_length, block_length)

        # todo better effect
        if selected:
            image = image.ConvertToDisabled(127)

        if not transparent:
            image.Replace(*MASK_COLOR, *self.bg_color)

        dc.DrawBitmap(image.ConvertToBitmap(), x, y, useMask=transparent)