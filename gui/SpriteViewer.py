from math import ceil

import wx

from Level import Level
from Sprite import Block

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

        self.object_set = 0

        self.rom = rom

        self.sprite_bank = SpriteBank(rom=rom, object_set=self.object_set, parent=self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.sprite_bank, flag=wx.EXPAND)

        self.SetSizer(sizer)
        self.Fit()

        self.Bind(wx.EVT_TOOL, self.on_tool_click)
        self.Bind(wx.EVT_CLOSE, self.on_exit)

    def on_tool_click(self, event):
        tool_id = event.GetId()

        if tool_id == ID_ZOOM_IN:
            self.sprite_bank.zoom_in()
        elif tool_id == ID_ZOOM_OUT:
            self.sprite_bank.zoom_out()

        if tool_id == ID_PREV_BANK:
            self.object_set = max(self.object_set - 1, 0)
        if tool_id == ID_NEXT_BANK:
            self.object_set = min(self.object_set + 1, 14)

        self.sprite_bank.object_set = self.object_set

        self.sprite_bank.Refresh()

    def on_resize(self):
        self.Fit()

    def on_exit(self, _):
        self.Hide()


class SpriteBank(wx.Panel):
    def __init__(self, rom, object_set=0, zoom=2, *args, **kwargs):
        self.sprites = 256
        self.sprites_horiz = 16
        self.sprites_vert = ceil(self.sprites / self.sprites_horiz)

        self.object_set = object_set
        self.zoom = zoom

        self.size = wx.Size(self.sprites_horiz * Block.WIDTH * self.zoom,
                            self.sprites_vert * Block.HEIGHT * self.zoom)

        super(SpriteBank, self).__init__(size=self.size, *args, **kwargs)

        self.SetSize(self.size)

        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)

        self.object_set = 0

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
        self.SetSize(wx.Size(self.sprites_horiz * Block.WIDTH * self.zoom,
                             self.sprites_vert * Block.HEIGHT * self.zoom))

        self.GetParent().on_resize()

    def on_paint(self, event):
        event.Skip()

        dc = wx.AutoBufferedPaintDC(self)

        dc.Clear()

        horizontal = self.sprites_horiz

        for i in range(self.sprites):
            block = Block(self.rom, self.object_set, i, Level.palettes[self.object_set][0])

            x = (i % horizontal) * Block.WIDTH * self.zoom
            y = (i // horizontal) * Block.HEIGHT * self.zoom

            block.draw(dc, x, y, self.zoom)

        return
