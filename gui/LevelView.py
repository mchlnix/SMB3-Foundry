import wx

from Level import Level
from Sprite import Block


class LevelView(wx.Panel):
    def __init__(self, parent, rom, world, level):
        super(LevelView, self).__init__(parent)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)

        self.rom = rom

        print(f"Drawing Level: {world}-{level}")

        self.level = Level(self.rom, world, level)

        self.SetSize(wx.Size(self.level.length * Block.WIDTH, 26 * Block.HEIGHT))

    def on_size(self, event):
        event.Skip()
        self.Refresh()

    def on_resize(self, _):
        self.SetSize(wx.Size(self.level.length * Block.WIDTH, 26 * Block.HEIGHT))

    def on_paint(self, event):
        event.Skip()

        dc = wx.AutoBufferedPaintDC(self)

        self.level.draw(dc)

        return
