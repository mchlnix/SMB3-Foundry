import wx
from math import ceil

from game.File import ROM
from game.gfx.Palette import get_bg_color_for, load_palette
from game.gfx.PatternTable import PatternTable
from game.gfx.drawable.Block import Block
from gui.LevelSelector import OBJECT_SET_ITEMS

ID_ZOOM_IN = 10001
ID_ZOOM_OUT = 10002
ID_PREV_BANK = 10003
ID_NEXT_BANK = 10004
ID_BANK_DROPDOWN = 10005


class BlockViewer(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(BlockViewer, self).__init__(*args, title="Block Viewer", **kwargs)

        self.toolbar = self.CreateToolBar()

        self.toolbar.AddTool(
            ID_PREV_BANK,
            "",
            wx.ArtProvider.GetBitmap(id=wx.ART_GO_BACK, client=wx.ART_TOOLBAR),
        )
        self.toolbar.AddTool(
            ID_NEXT_BANK,
            "",
            wx.ArtProvider.GetBitmap(id=wx.ART_GO_FORWARD, client=wx.ART_TOOLBAR),
        )

        self.toolbar.AddTool(
            ID_ZOOM_OUT,
            "",
            wx.ArtProvider.GetBitmap(id=wx.ART_MINUS, client=wx.ART_TOOLBAR),
        )
        self.toolbar.AddTool(
            ID_ZOOM_IN,
            "",
            wx.ArtProvider.GetBitmap(id=wx.ART_PLUS, client=wx.ART_TOOLBAR),
        )

        self.bank_dropdown = wx.ComboBox(
            parent=self.toolbar, id=ID_BANK_DROPDOWN, choices=OBJECT_SET_ITEMS
        )
        self.bank_dropdown.SetSelection(0)

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
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_press)

        self.SetStatusBar(wx.StatusBar(self))
        self.GetStatusBar().SetFieldsCount(3)

    def on_key_press(self, event):
        key = event.GetKeyCode()

        if key == wx.WXK_ESCAPE:
            self.on_exit(None)

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

        self.size = wx.Size(
            self.sprites_horiz * Block.WIDTH * self.zoom,
            self.sprites_vert * Block.HEIGHT * self.zoom,
        )

        super(BlockBank, self).__init__(size=self.size, *args, **kwargs)

        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_MOTION, self.on_mouse_motion)

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
        self.SetSize(
            wx.Size(
                self.sprites_horiz * Block.WIDTH * self.zoom,
                self.sprites_vert * Block.HEIGHT * self.zoom,
            )
        )

        self.GetParent().on_resize(None)

    def on_mouse_motion(self, event):
        x, y = event.GetPosition().Get()

        block_length = Block.WIDTH * self.zoom

        column = x // block_length
        row = y // block_length

        dec_index = row * self.sprites_horiz + column
        hex_index = hex(dec_index).upper().replace("X", "x")

        self.GetParent().SetStatusText(f"Row: {row}", 0)
        self.GetParent().SetStatusText(f"Column: {column}", 1)
        self.GetParent().SetStatusText(f"Index: {dec_index} / {hex_index}", 2)

        event.Skip()

    def on_paint(self, event):
        event.Skip()

        dc = wx.BufferedPaintDC(self)

        bg_color = get_bg_color_for(self.object_set, 0)
        dc.SetBackground(wx.Brush(wx.Colour(bg_color)))

        dc.Clear()

        pattern_table = PatternTable(self.object_set)
        palette = load_palette(self.object_set, 0)
        tsa_data = ROM.get_tsa_data(self.object_set)

        horizontal = self.sprites_horiz

        block_length = Block.WIDTH * self.zoom

        for i in range(self.sprites):
            block = Block(i, palette, pattern_table, tsa_data)

            x = (i % horizontal) * block_length
            y = (i // horizontal) * block_length

            block.draw(dc, x, y, block_length)

        return
