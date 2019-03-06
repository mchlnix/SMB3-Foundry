import wx


class LevelView(wx.Panel):
    def __init__(self, rom, *args, **kwargs):
        super(LevelView, self).__init__(*args, **kwargs)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)

        self.rom = rom

    def on_size(self, event):
        event.Skip()
        self.Refresh()

    def on_paint(self, event):
        event.Skip()

        dc = wx.AutoBufferedPaintDC(self)
        dc.SetUserScale(8, 8)

        dc.Clear()

        return
