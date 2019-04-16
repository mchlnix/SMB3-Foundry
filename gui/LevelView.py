import wx

from Level import Level
from Sprite import Block


class LevelView(wx.Panel):
    def __init__(self, parent, rom, world, level, object_set=None):
        super(LevelView, self).__init__(parent)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)

        self.rom = rom

        print(f"Drawing Level: {world}-{level}")

        self.level = Level(self.rom, world, level, object_set)
        self.SetMinSize(wx.Size(self.level.width * Block.WIDTH, self.level.height * Block.HEIGHT))
        self.SetSize(self.GetMinSize())

        self.grid_lines = True

    def object_at(self, x, y):
        level_point = self.to_level_point(x, y)

        for obj in reversed(self.level.objects):
            if level_point in obj:
                return obj
        else:
            return None

    @staticmethod
    def to_level_point(x, y):
        level_x = x // Block.WIDTH
        level_y = y // Block.HEIGHT

        return level_x, level_y

    def on_size(self, event):
        event.Skip()
        self.Refresh()

    def on_paint(self, event):
        event.Skip()

        dc = wx.BufferedPaintDC(self)

        if hasattr(self, "level"):
            self.level.draw(dc)

        if self.grid_lines:
            grid_pen = wx.Pen(colour=wx.Colour(0x80, 0x80, 0x80, 0x80), width=1)

            dc.SetPen(grid_pen)

            pixel_width = self.level.width * Block.WIDTH
            pixel_height = self.level.height * Block.HEIGHT

            for x in range(0, pixel_width, Block.WIDTH):
                dc.DrawLine(x, 0, x, pixel_height)
            for y in range(0, pixel_height, Block.HEIGHT):
                dc.DrawLine(0, y, pixel_width, y)

        return
