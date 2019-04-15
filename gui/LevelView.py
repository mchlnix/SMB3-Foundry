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

    def object_at(self, x, y):
        level_x = x // Block.WIDTH
        level_y = y // Block.HEIGHT

        for obj in self.level.objects:
            if (level_x, level_y) in obj:
                return obj
        else:
            return None

    def on_size(self, event):
        event.Skip()
        self.Refresh()

    def on_paint(self, event):
        event.Skip()

        dc = wx.BufferedPaintDC(self)

        if hasattr(self, "level"):
            self.level.draw(dc)

        return
