import wx
import wx.lib.scrolledpanel

from File import ROM
from Graphics import LevelObject
from LevelSelector import LevelSelector
from LevelView import LevelView
from SpriteViewer import SpriteViewer

# file menu

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

ID_VIEW_OBJECTS = 401
ID_CLONE_OBJECT_ENEMY = 402
ID_ADD_3_BYTE_OBJECT = 403
ID_ADD_4_BYTE_OBJECT = 404
ID_ADD_ENEMY = 405
ID_DELETE_OBJECT_ENEMY = 406
ID_DELETE_ALL = 407

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

ID_SPIN_DOMAIN = 1000
ID_SPIN_TYPE = 1001
ID_SPIN_LENGTH = 1002


class SMB3Foundry(wx.Frame):

    def __init__(self, *args, **kw):
        super(SMB3Foundry, self).__init__(style=wx.MAXIMIZE | wx.DEFAULT_FRAME_STYLE, *args, **kw)

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

        self.Bind(wx.EVT_MENU, self.open_level_selector, id=ID_SELECT_LEVEL)

        object_menu = wx.Menu()

        object_menu.Append(ID_VIEW_OBJECTS, "&View Objects", "")
        object_menu.AppendSeparator()
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
        self.Bind(wx.EVT_MENU, self.open_sprite_viewer, id=ID_VIEW_OBJECTS)

        self.SetTitle("SMB3Foundry")
        self.Center()

        self.rom = ROM("SMB3.nes")

        self.sprite_viewer = SpriteViewer(rom=ROM("SMB3.nes"), parent=self)

        horiz_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.level_selector = LevelSelector(parent=self)

        self.scroll_panel = wx.lib.scrolledpanel.ScrolledPanel(self)
        self.scroll_panel.SetupScrolling()

        self.levelview = LevelView(parent=self.scroll_panel, rom=self.rom, world=1, level=1, object_set=1)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.levelview)

        self.scroll_panel.SetSizer(sizer)

        self.object_list = wx.ListBox(self)
        self.update_object_list()

        vert_sizer = wx.BoxSizer(wx.VERTICAL)
        spinner_sizer = wx.FlexGridSizer(cols=2, vgap=0, hgap=0)

        self.spin_domain = wx.SpinCtrl(self, ID_SPIN_DOMAIN, max=7)
        self.spin_type = wx.SpinCtrl(self, ID_SPIN_TYPE, max=0xFF)
        self.spin_length = wx.SpinCtrl(self, ID_SPIN_LENGTH, max=0xFF)

        self.select_object(None)

        spinner_sizer.Add(self.spin_domain, flag=wx.EXPAND)
        spinner_sizer.Add(self.spin_type, flag=wx.EXPAND)
        spinner_sizer.Add(self.spin_length, flag=wx.EXPAND)

        vert_sizer.Add(self.object_list, proportion=1, flag=wx.EXPAND)
        vert_sizer.Add(spinner_sizer, flag=wx.EXPAND)

        horiz_sizer.Add(self.scroll_panel, proportion=10, flag=wx.EXPAND)
        horiz_sizer.Add(vert_sizer, proportion=1, flag=wx.EXPAND)

        self.SetSizer(horiz_sizer)

        self.Bind(wx.EVT_LISTBOX, self.select_object)
        self.Bind(wx.EVT_BUTTON, self.on_button)

        self.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.Bind(wx.EVT_SPINCTRL, self.on_spin)

    def on_button(self, _):
        index = self.object_list.GetSelection()

        if index == -1:
            return

        level = self.levelview.level
        object_data = level.objects[index].data

        object_type = object_data[2]

        object_data[2] = (object_type + 1) % 0x100

        self.levelview.level.objects[index] = LevelObject(object_data, level.object_set, level.plains_level[level.object_definition], level.object_palette_group)
        self.levelview.Refresh()
        self.update_object_list()

    def on_spin(self, event):
        _id = event.GetId()

        if _id == ID_SPIN_TYPE:
            index = self.object_list.GetSelection()

            if index == -1:
                return

            level = self.levelview.level
            object_data = level.objects[index].data

            object_data[2] = self.spin_type.GetValue() % 256

            self.levelview.level.objects[index] = LevelObject(object_data, level.object_set,
                                                              level.plains_level[level.object_definition],
                                                              level.object_palette_group)
            self.levelview.Refresh()
            self.update_object_list()

        self.select_object(None)

    def update_object_list(self):
        index = self.object_list.GetSelection()

        self.object_list.SetItems([obj.description for obj in self.levelview.level.objects])

        self.object_list.SetSelection(index)

    def open_level_selector(self, _):
        self.level_selector.Show()

    def open_sprite_viewer(self, _):
        self.sprite_viewer.Show()

    def update_level(self, world, level, object_set):
        old = self.levelview
        new = LevelView(parent=self, rom=self.rom, world=world, level=level, object_set=object_set)

        self.scroll_panel.GetSizer().Replace(old, new)

        self.levelview.Destroy()
        self.levelview = new

        self.update_object_list()

    def select_object(self, _):
        index = self.object_list.GetSelection()

        for obj in self.levelview.level.objects:
            obj.selected = False

        if index == -1:
            self.spin_domain.SetValue(0)
            self.spin_type.SetValue(0)
            self.spin_length.SetValue(0)

            self.spin_domain.Disable()
            self.spin_type.Disable()
            self.spin_length.Disable()

            return
        else:
            obj = self.levelview.level.objects[index]

            obj.selected = True
            self.spin_domain.SetValue(obj.domain)
            self.spin_type.SetValue(obj.data[2])

            self.spin_domain.Enable()
            self.spin_type.Enable()

            if obj.is_4byte:
                self.spin_length.SetValue(obj.length)
                self.spin_length.Enable()
            else:
                self.spin_length.SetValue(0)
                self.spin_length.Disable()

            self.levelview.Refresh()

    def on_exit(self, _):
        self.Close(True)
