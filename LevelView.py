import wx

from Sprite import Spritesheet


class LevelView(wx.Panel):
    def __init__(self, *args, **kwargs):
        super(LevelView, self).__init__(*args, **kwargs)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.sheet = Spritesheet(source="./smb3_sprites.bmp")

    def on_size(self, event):
        event.Skip()
        self.Refresh()

    def on_paint(self, event):
        event.Skip()
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()

        for x, y in zip(range(5), range(5)):
            dc.DrawBitmap(self.sheet.get_sprite(x, y), x * 16, y * 16)
