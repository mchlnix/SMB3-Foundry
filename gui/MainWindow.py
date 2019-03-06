import wx

# file menu
from wx import EVT_TOOL

from File import ROM, Map
from LevelView import LevelView
from Sprite import Tile, Spritesheet, TILE_SIZE, TILE_WIDTH, TILE_HEIGHT

ID_OPEN_ROM = 101
ID_OPEN_M3L = 102
ID_SAVE_ROM = 103
ID_SAVE_M3L = 104
ID_SAVE_LEVEL_TO = 105
ID_SAVE_ROM_AS = 106
ID_APPLY_IPS_PATCH = 107
ID_ROM_PRESET = 108
ID_EXIT = 109

# edit menu

ID_EDIT_LEVEL = 201
ID_EDIT_OBJ_DEFS = 202
ID_EDIT_PALETTE = 203
ID_EDIT_GRAPHICS = 204
ID_EDIT_MISC = 205
ID_FREEFORM_MODE = 206
ID_LIMIT_SIZE = 207

# level menu

ID_GOTO_NEXT_AREA = 301
ID_SELECT_LEVEL = 302
ID_RELOAD_LEVEL = 303
ID_EDIT_HEADER = 304
ID_EDIT_POINTERS = 305

# object menu

ID_CLONE_OBJECT_ENEMY = 401
ID_ADD_3_BYTE_OBJECT = 402
ID_ADD_4_BYTE_OBJECT = 403
ID_ADD_ENEMY = 404
ID_DELETE_OBJECT_ENEMY = 405
ID_DELETE_ALL = 406

# view menu

ID_GRIDLINES = 501
ID_BACKGROUND_FLOOR = 502
ID_TOOLBAR = 503
ID_ZOOM = 504
ID_USE_ROM_GRAPHICS = 505
ID_PALETTE = 506
ID_MORE = 507

# help menu

ID_ENEMY_COMPATIBILITY = 601
ID_TROUBLESHOOTING = 602
ID_PROGRAM_WEBSITE = 603
ID_MAKE_A_DONATION = 604
ID_ABOUT = 605


class SMB3Foundry(wx.Frame):

    def __init__(self, *args, **kw):
        super(SMB3Foundry, self).__init__(*args, **kw)

        file_menu = wx.Menu()

        file_menu.Append(ID_OPEN_ROM, "&Open ROM", " Terminate the program")
        file_menu.Append(ID_OPEN_M3L, "&Open M3L", " Terminate the program")
        file_menu.AppendSeparator()
        file_menu.Append(ID_SAVE_ROM, "&Save ROM", " Terminate the program")
        file_menu.AppendSeparator()
        file_menu.Append(ID_SAVE_M3L, "&Save M3L", " Terminate the program")
        file_menu.Append(ID_SAVE_LEVEL_TO, "&Save Level to", " Terminate the program")
        file_menu.Append(ID_SAVE_ROM_AS, "&Save ROM as", " Terminate the program")
        file_menu.AppendSeparator()
        file_menu.Append(ID_APPLY_IPS_PATCH, "&Apply IPS Patch", " Terminate the program")
        file_menu.AppendSeparator()
        file_menu.Append(ID_ROM_PRESET, "&ROM Preset", " Terminate the program")
        file_menu.AppendSeparator()
        file_menu.Append(ID_EXIT, "&Exit", " Terminate the program")

        edit_menu = wx.Menu()

        edit_menu.Append(ID_EDIT_LEVEL, "&Edit Level", "")
        edit_menu.Append(ID_EDIT_OBJ_DEFS, "&Edit Object Definitions", "")
        edit_menu.Append(ID_EDIT_PALETTE, "&Edit Palette", "")
        edit_menu.Append(ID_EDIT_GRAPHICS, "&Edit Graphics", "")
        edit_menu.Append(ID_EDIT_MISC, "&Edit Miscellaneous", "")
        edit_menu.AppendSeparator()
        edit_menu.Append(ID_FREEFORM_MODE, "&Freeform Mode", "")
        edit_menu.Append(ID_LIMIT_SIZE, "&Limit Size", "")

        level_menu = wx.Menu()

        level_menu.Append(ID_GOTO_NEXT_AREA, "&Go to next Area", "")
        level_menu.Append(ID_SELECT_LEVEL, "&Select Level", "")
        level_menu.AppendSeparator()
        level_menu.Append(ID_RELOAD_LEVEL, "&Reload Level", "")
        level_menu.AppendSeparator()
        level_menu.Append(ID_EDIT_HEADER, "&Edit Header", "")
        level_menu.Append(ID_EDIT_POINTERS, "&Edit Pointers", "")

        object_menu = wx.Menu()

        object_menu.Append(ID_CLONE_OBJECT_ENEMY, "&Clone Object/Enemy", "")
        object_menu.AppendSeparator()
        object_menu.Append(ID_ADD_3_BYTE_OBJECT, "&Add 3 Byte Object", "")
        object_menu.Append(ID_ADD_4_BYTE_OBJECT, "&Add 4 Byte Object", "")
        object_menu.Append(ID_ADD_ENEMY, "&Add Enemy", "")
        object_menu.AppendSeparator()
        object_menu.Append(ID_DELETE_OBJECT_ENEMY, "&Delete Object/Enemy", "")
        object_menu.Append(ID_DELETE_ALL, "&Delete All", "")

        view_menu = wx.Menu()

        view_menu.Append(ID_GRIDLINES, "&Gridlines", "")
        view_menu.Append(ID_BACKGROUND_FLOOR, "&Background & Floor", "")
        view_menu.Append(ID_TOOLBAR, "&Toolbar", "")
        view_menu.AppendSeparator()
        view_menu.Append(ID_ZOOM, "&Zoom", "")
        view_menu.AppendSeparator()
        view_menu.Append(ID_USE_ROM_GRAPHICS, "&Use ROM Graphics", "")
        view_menu.Append(ID_PALETTE, "&Palette", "")
        view_menu.AppendSeparator()
        view_menu.Append(ID_MORE, "&More", "")

        help_menu = wx.Menu()

        help_menu.Append(ID_ENEMY_COMPATIBILITY, "&Enemy Compatibility", "")
        help_menu.Append(ID_TROUBLESHOOTING, "&Troubleshooting", "")
        help_menu.AppendSeparator()
        help_menu.Append(ID_PROGRAM_WEBSITE, "&Program Website", "")
        help_menu.Append(ID_MAKE_A_DONATION, "&Make a Donation", "")
        help_menu.AppendSeparator()
        help_menu.Append(ID_ABOUT, "&About", "")

        menu_bar = wx.MenuBar()

        menu_bar.Append(file_menu, "&File")
        menu_bar.Append(edit_menu, "&Edit")
        menu_bar.Append(level_menu, "&Level")
        menu_bar.Append(object_menu, "&Object")
        menu_bar.Append(view_menu, "&View")
        menu_bar.Append(help_menu, "&Help")

        self.SetMenuBar(menu_bar)

        self.Bind(wx.EVT_MENU, self.on_exit, id=ID_EXIT)
        self.Bind(wx.EVT_MENU, self.on_sprite_viewer, id=ID_OPEN_ROM)

        self.SetTitle("SMB3Foundry")
        self.Center()

        rom = ROM("SMB3.nes")

        self.levelview = LevelView(parent=self, rom=rom)
        Map(0, rom)

    def on_sprite_viewer(self, event):
        event.Skip()

        self.sprite_viewer = SpriteViewer(rom=ROM("SMB3.nes"), parent=self)
        self.sprite_viewer.Show()

    def on_exit(self, e):
        e.Skip()

        self.Close(True)


ID_ZOOM_IN = 10001
ID_ZOOM_OUT = 10002
ID_PREV_BANK = 10003
ID_NEXT_BANK = 10004


class SpriteViewer(wx.Frame):
    def __init__(self, rom, *args, **kwargs):
        super(SpriteViewer, self).__init__(*args, **kwargs)

        self.toolbar = self.CreateToolBar()

        self.toolbar.AddTool(ID_PREV_BANK, "", wx.Bitmap("./Previous.bmp"))
        self.toolbar.AddTool(ID_NEXT_BANK, "", wx.Bitmap("./Next.bmp"))

        self.toolbar.AddTool(ID_ZOOM_OUT, "", wx.Bitmap("./zoom_out.bmp"))
        self.toolbar.AddTool(ID_ZOOM_IN, "", wx.Bitmap("./zoom_in.bmp"))

        self.toolbar.Realize()

        self.offset = 0

        self.rom = rom

        self.sprite_bank = SpriteBank(rom=rom, offset=self.offset, parent=self)

        self.Fit()

        self.Bind(EVT_TOOL, self.on_tool_click)

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
        self.sheet = Spritesheet(source="./smb3_sprites.bmp")

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

        self.rom.seek(0x40010)

        palette = {
            0b00: bytes([0xF7, 0xD8, 0xA5]),  # background
            0b01: bytes([0xFE, 0xCC, 0xC5]),
            0b10: bytes([0xB5, 0x31, 0x20]),
            0b11: bytes([0x00, 0x00, 0x00]),
        }

        for i in range(self.sprites):
            offset = self.offset + i * TILE_SIZE

            x = (i % self.sprites_horiz) * TILE_WIDTH
            y = (i // self.sprites_horiz) * TILE_HEIGHT

            tile = Tile(self.rom, offset, palette)

            dc.DrawBitmap(tile.as_bitmap(), x, y)

        return


def main():
    app = wx.App()
    ex = SMB3Foundry(None)
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
