from math import ceil

import wx

from Data import NESPalette
from Graphics import PatternTable
from Level import Level
from LevelSelector import OBJECT_SET_ITEMS
from Sprite import Block

ID_ZOOM_IN = 10001
ID_ZOOM_OUT = 10002
ID_PREV_BANK = 10003
ID_NEXT_BANK = 10004
ID_BANK_DROPDOWN = 10005


class BlockViewer(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(BlockViewer, self).__init__(*args, title="Block Viewer", **kwargs)

        self.toolbar = self.CreateToolBar()

        self.toolbar.AddTool(ID_PREV_BANK, "", wx.Bitmap("data/img/Previous.bmp"))
        self.toolbar.AddTool(ID_NEXT_BANK, "", wx.Bitmap("data/img/Next.bmp"))

        self.toolbar.AddTool(ID_ZOOM_OUT, "", wx.Bitmap("data/img/zoom_out.bmp"))
        self.toolbar.AddTool(ID_ZOOM_IN, "", wx.Bitmap("data/img/zoom_in.bmp"))

        self.bank_dropdown = wx.ComboBox(parent=self.toolbar, id=ID_BANK_DROPDOWN, choices=OBJECT_SET_ITEMS)
        self.bank_dropdown.SetSelection(0)

        self.graphic_set_spinner = wx.SpinCtrl(parent=self.toolbar, min=0, max=0x6000F)

        self.toolbar.AddControl(self.bank_dropdown)

        self.toolbar.Realize()

        self.object_set = 0

        self.sprite_bank = BlockBank(object_set=self.object_set, parent=self)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.sprite_bank, flag=wx.EXPAND)

        self.SetSizer(self.sizer)
        self.sizer.Fit(self)

        self.Bind(wx.EVT_TOOL, self.on_tool_click)
        self.Bind(wx.EVT_COMBOBOX, self.on_combo)
        self.Bind(wx.EVT_CLOSE, self.on_exit)
        self.Bind(wx.EVT_SIZE, self.on_resize)

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
        self.bank_dropdown.SetSelection(self.object_set)

        self.sprite_bank.Refresh()

    def on_combo(self, _):
        self.object_set = self.bank_dropdown.GetSelection()

        self.sprite_bank.object_set = self.object_set

        self.sprite_bank.Refresh()

    def on_resize(self, _):
        self.sizer.SetMinSize(self.sprite_bank.GetSize())
        self.sizer.Fit(self)

    def on_exit(self, _):
        self.Hide()


class BlockBank(wx.Panel):
    def __init__(self, object_set=0, zoom=2, *args, **kwargs):
        self.sprites = 256
        self.sprites_horiz = 16
        self.sprites_vert = ceil(self.sprites / self.sprites_horiz)

        self.object_set = object_set
        self.zoom = zoom

        self.size = wx.Size(self.sprites_horiz * Block.WIDTH * self.zoom,
                            self.sprites_vert * Block.HEIGHT * self.zoom)

        super(BlockBank, self).__init__(size=self.size, *args, **kwargs)

        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)

        self.object_set = 0

        self.SetSize(self.size)

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

        self.GetParent().on_resize(None)

    def on_paint(self, event):
        event.Skip()

        dc = wx.BufferedPaintDC(self)

        bg_color = NESPalette[Level.palettes[self.object_set][0][0][0]]
        dc.SetBackground(wx.Brush(wx.Colour(bg_color)))

        dc.Clear()

        pattern_table = PatternTable(self.object_set)

        horizontal = self.sprites_horiz

        for i in range(self.sprites):
            block = Block(self.object_set, i, Level.palettes[self.object_set][0], pattern_table)

            x = (i % horizontal) * Block.WIDTH * self.zoom
            y = (i // horizontal) * Block.HEIGHT * self.zoom

            block.draw(dc, x, y, self.zoom)

        return
