import wx

from foundry.game.gfx.Palette import load_palette
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects.EnemyItem import EnemyObject


class EnemyItemFactory:
    object_set: int
    graphic_set: int

    definitions: list = []

    def __init__(self, object_set, palette_index):
        wx.InitAllImageHandlers()
        png = wx.Image("data/gfx.png")

        rows_per_object_set = 256 // 64

        y_offset = 12 * rows_per_object_set * Block.HEIGHT

        self.png_data = png.GetSubImage(
            wx.Rect(0, y_offset, png.GetWidth(), png.GetHeight() - y_offset)
        )

        self.palette_group = load_palette(object_set, palette_index)

    # todo get rid of index by fixing ground map
    def make_object(self, data, _):
        return EnemyObject(data, self.png_data, self.palette_group)
