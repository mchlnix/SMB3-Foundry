import wx

from Sprite import Tile, TILE_HEIGHT, TILE_WIDTH, TILE_SIZE

ID_ZOOM_IN = 10001
ID_ZOOM_OUT = 10002
ID_PREV_BANK = 10003
ID_NEXT_BANK = 10004


class SpriteViewer(wx.Frame):
    def __init__(self, rom, *args, **kwargs):
        super(SpriteViewer, self).__init__(*args, **kwargs)

        self.toolbar = self.CreateToolBar()

        self.toolbar.AddTool(ID_PREV_BANK, "", wx.Bitmap("data/img/Previous.bmp"))
        self.toolbar.AddTool(ID_NEXT_BANK, "", wx.Bitmap("data/img/Next.bmp"))

        self.toolbar.AddTool(ID_ZOOM_OUT, "", wx.Bitmap("data/img/zoom_out.bmp"))
        self.toolbar.AddTool(ID_ZOOM_IN, "", wx.Bitmap("data/img/zoom_in.bmp"))

        self.toolbar.Realize()

        self.offset = 0

        self.rom = rom

        self.sprite_bank = SpriteBank(rom=rom, offset=self.offset, parent=self)

        self.Fit()

        self.Bind(wx.EVT_TOOL, self.on_tool_click)

    def on_tool_click(self, event):
        tool_id = event.GetId()

        if tool_id == ID_ZOOM_IN:
            self.sprite_bank.zoom_in()
        elif tool_id == ID_ZOOM_OUT:
            self.sprite_bank.zoom_out()

        if tool_id == ID_PREV_BANK:
            self.offset = max(self.offset - 512, 0)
        if tool_id == ID_NEXT_BANK:
            self.offset += 512

        self.sprite_bank.set_offset(self.offset)

    def on_resize(self):
        self.SetSize(self.sprite_bank.GetSize())

    def on_exit(self, e):
        e.Skip()

        self.Close(True)


class SpriteBank(wx.Panel):
    def __init__(self, rom, offset=0, zoom=4, *args, **kwargs):
        self.sprites = 512
        self.sprites_horiz = 16
        self.sprites_vert = self.sprites // self.sprites_horiz + 1

        self.offset = offset
        self.zoom = zoom

        self.size = wx.Size(self.sprites_horiz * TILE_WIDTH * self.zoom,
                            self.sprites_vert * TILE_HEIGHT * self.zoom)

        super(SpriteBank, self).__init__(size=self.size, *args, **kwargs)

        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)

        self.rom = rom

    def on_size(self, event):
        event.Skip()
        self.Refresh()

    def zoom_in(self):
        self.zoom += 1
        self._after_zoom()

    def zoom_out(self):
        self.zoom = max(self.zoom - 1, 1)
        self._after_zoom()

    def _after_zoom(self):
        self.SetSize(wx.Size(self.sprites_horiz * TILE_WIDTH * self.zoom,
                             self.sprites_vert * TILE_HEIGHT * self.zoom))

        self.Refresh()
        self.GetParent().on_resize()

    def set_offset(self, offset):
        self.offset = offset * TILE_SIZE
        self.Refresh()

    def on_paint(self, event):
        event.Skip()

        dc = wx.AutoBufferedPaintDC(self)
        dc.SetUserScale(self.zoom, self.zoom)

        dc.Clear()

        for i in range(self.sprites):
            offset = self.offset + i * TILE_SIZE

            x = (i % self.sprites_horiz) * TILE_WIDTH
            y = (i // self.sprites_horiz) * TILE_HEIGHT

            tile = Tile(self.rom, offset)

            dc.DrawBitmap(tile.as_bitmap(), x, y)

        return
