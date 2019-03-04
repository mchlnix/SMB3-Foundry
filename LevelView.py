import wx


class LevelView(wx.Panel):
    def __init__(self, *args, **kwargs):
        super(LevelView, self).__init__(*args, **kwargs)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def on_size(self, event):
        event.Skip()
        self.Refresh()

    def on_paint(self, event):
        w, h = self.GetClientSize()
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        sprites = wx.Bitmap("./smb3_sprites.bmp")
        dc.DrawBitmap(sprites, 0, 0)
