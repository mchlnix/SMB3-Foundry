import wx
import wx.lib.scrolledpanel

from BlockViewer import BlockViewer
from File import ROM
from Graphics import LevelObject
from Level import Level, WorldMap
from LevelSelector import LevelSelector
from LevelView import LevelView
from ObjectStatusBar import ObjectStatusBar
from ObjectViewer import ObjectViewer

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

ID_VIEW_BLOCKS = 401
ID_CLONE_OBJECT_ENEMY = 402
ID_ADD_3_BYTE_OBJECT = 403
ID_ADD_4_BYTE_OBJECT = 404
ID_ADD_ENEMY = 405
ID_DELETE_OBJECT_ENEMY = 406
ID_DELETE_ALL = 407
ID_VIEW_OBJECTS = 408

# view menu

ID_GRID_LINES = 501
ID_BACKGROUND_FLOOR = 502
ID_TOOLBAR = 503
ID_ZOOM = 504
ID_USE_ROM_GRAPHICS = 505
ID_PALETTE = 506
ID_MORE = 507
ID_TRANSPARENCY = 508

# help menu

ID_ENEMY_COMPATIBILITY = 601
ID_TROUBLESHOOTING = 602
ID_PROGRAM_WEBSITE = 603
ID_MAKE_A_DONATION = 604
ID_ABOUT = 605

ID_SPIN_DOMAIN = 1000
ID_SPIN_TYPE = 1001
ID_SPIN_LENGTH = 1002

MAX_DOMAIN = 0x07
MAX_TYPE = 0xFF
MAX_LENGTH = 0xFF


class SMB3Foundry(wx.Frame):

    def __init__(self, *args, **kw):
        super(SMB3Foundry, self).__init__(title="SMB3Foundry", style=wx.MAXIMIZE | wx.DEFAULT_FRAME_STYLE, *args, **kw)

        file_menu = wx.Menu()

        file_menu.Append(ID_OPEN_ROM, "&Open ROM", "")
        """
        file_menu.Append(ID_OPEN_M3L, "&Open M3L", "")
        file_menu.AppendSeparator()
        """
        file_menu.Append(ID_SAVE_ROM, "&Save ROM", "")
        file_menu.Append(ID_SAVE_ROM_AS, "&Save ROM as ...", "")
        """
        file_menu.AppendSeparator()
        file_menu.Append(ID_SAVE_M3L, "&Save M3L", "")
        file_menu.Append(ID_SAVE_LEVEL_TO, "&Save Level to", "")
        file_menu.AppendSeparator()
        file_menu.Append(ID_APPLY_IPS_PATCH, "&Apply IPS Patch", "")
        file_menu.AppendSeparator()
        file_menu.Append(ID_ROM_PRESET, "&ROM Preset", "")
        """
        file_menu.AppendSeparator()
        file_menu.Append(ID_EXIT, "&Exit", "")

        edit_menu = wx.Menu()

        """
        edit_menu.Append(ID_EDIT_LEVEL, "&Edit Level", "")
        edit_menu.Append(ID_EDIT_OBJ_DEFS, "&Edit Object Definitions", "")
        edit_menu.Append(ID_EDIT_PALETTE, "&Edit Palette", "")
        edit_menu.Append(ID_EDIT_GRAPHICS, "&Edit Graphics", "")
        edit_menu.Append(ID_EDIT_MISC, "&Edit Miscellaneous", "")
        edit_menu.AppendSeparator()
        edit_menu.Append(ID_FREEFORM_MODE, "&Freeform Mode", "")
        edit_menu.Append(ID_LIMIT_SIZE, "&Limit Size", "")
        """

        level_menu = wx.Menu()

        level_menu.Append(ID_SELECT_LEVEL, "&Select Level", "")
        """
        level_menu.Append(ID_GOTO_NEXT_AREA, "&Go to next Area", "")
        level_menu.AppendSeparator()
        level_menu.Append(ID_RELOAD_LEVEL, "&Reload Level", "")
        level_menu.AppendSeparator()
        level_menu.Append(ID_EDIT_HEADER, "&Edit Header", "")
        level_menu.Append(ID_EDIT_POINTERS, "&Edit Pointers", "")
        """

        object_menu = wx.Menu()

        object_menu.Append(ID_VIEW_BLOCKS, "&View Blocks", "")
        object_menu.Append(ID_VIEW_OBJECTS, "&View Objects", "")
        """
        object_menu.AppendSeparator()
        object_menu.Append(ID_CLONE_OBJECT_ENEMY, "&Clone Object/Enemy", "")
        object_menu.AppendSeparator()
        object_menu.Append(ID_ADD_3_BYTE_OBJECT, "&Add 3 Byte Object", "")
        object_menu.Append(ID_ADD_4_BYTE_OBJECT, "&Add 4 Byte Object", "")
        object_menu.Append(ID_ADD_ENEMY, "&Add Enemy", "")
        object_menu.AppendSeparator()
        object_menu.Append(ID_DELETE_OBJECT_ENEMY, "&Delete Object/Enemy", "")
        object_menu.Append(ID_DELETE_ALL, "&Delete All", "")
        """

        view_menu = wx.Menu()

        view_menu.AppendCheckItem(ID_GRID_LINES, "&Gridlines", "")
        view_menu.AppendCheckItem(ID_TRANSPARENCY, "&Block Transparency", "")
        view_menu.FindItemById(ID_TRANSPARENCY).Check(True)
        """
        view_menu.Append(ID_BACKGROUND_FLOOR, "&Background & Floor", "")
        view_menu.Append(ID_TOOLBAR, "&Toolbar", "")
        view_menu.AppendSeparator()
        view_menu.Append(ID_ZOOM, "&Zoom", "")
        view_menu.AppendSeparator()
        view_menu.Append(ID_USE_ROM_GRAPHICS, "&Use ROM Graphics", "")
        view_menu.Append(ID_PALETTE, "&Palette", "")
        view_menu.AppendSeparator()
        view_menu.Append(ID_MORE, "&More", "")
        """

        help_menu = wx.Menu()
        """
        help_menu.Append(ID_ENEMY_COMPATIBILITY, "&Enemy Compatibility", "")
        help_menu.Append(ID_TROUBLESHOOTING, "&Troubleshooting", "")
        help_menu.AppendSeparator()
        help_menu.Append(ID_PROGRAM_WEBSITE, "&Program Website", "")
        help_menu.Append(ID_MAKE_A_DONATION, "&Make a Donation", "")
        help_menu.AppendSeparator()
        help_menu.Append(ID_ABOUT, "&About", "")
        """

        menu_bar = wx.MenuBar()

        menu_bar.Append(file_menu, "&File")
        menu_bar.Append(edit_menu, "&Edit")
        menu_bar.Append(level_menu, "&Level")
        menu_bar.Append(object_menu, "&Object")
        menu_bar.Append(view_menu, "&View")
        menu_bar.Append(help_menu, "&Help")

        self.SetMenuBar(menu_bar)

        self.Bind(wx.EVT_MENU, self.on_open_rom, id=ID_OPEN_ROM)
        self.Bind(wx.EVT_MENU, self.on_save_rom, id=ID_SAVE_ROM)
        self.Bind(wx.EVT_MENU, self.on_save_rom, id=ID_SAVE_ROM_AS)
        self.Bind(wx.EVT_MENU, self.on_exit, id=ID_EXIT)
        self.Bind(wx.EVT_MENU, self.open_level_selector, id=ID_SELECT_LEVEL)
        self.Bind(wx.EVT_MENU, self.on_block_viewer, id=ID_VIEW_BLOCKS)
        self.Bind(wx.EVT_MENU, self.on_object_viewer, id=ID_VIEW_OBJECTS)
        self.Bind(wx.EVT_MENU, self.on_menu_checked)

        self.Center()

        self.block_viewer = None
        self.object_viewer = None

        horiz_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.level_selector = LevelSelector(parent=self)

        self.scroll_panel = wx.lib.scrolledpanel.ScrolledPanel(self)

        self.level_view = LevelView(parent=self.scroll_panel)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.level_view)

        self.scroll_panel.SetSizer(sizer)

        self.object_list = wx.ListBox(self)

        spinner_sizer = wx.FlexGridSizer(cols=2, vgap=0, hgap=0)
        spinner_sizer.AddGrowableCol(0)

        self.spin_domain = wx.SpinCtrl(self, ID_SPIN_DOMAIN, max=MAX_DOMAIN)
        self.spin_domain.SetBase(16)
        self.spin_type = wx.SpinCtrl(self, ID_SPIN_TYPE, max=MAX_TYPE)
        self.spin_type.SetBase(16)
        self.spin_length = wx.SpinCtrl(self, ID_SPIN_LENGTH, max=MAX_LENGTH)
        self.spin_length.SetBase(16)

        spinner_sizer.Add(wx.StaticText(self, label="Domain: "), flag=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
        spinner_sizer.Add(self.spin_domain)
        spinner_sizer.Add(wx.StaticText(self, label="Type: "), flag=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
        spinner_sizer.Add(self.spin_type)
        spinner_sizer.Add(wx.StaticText(self, label="Length: "), flag=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
        spinner_sizer.Add(self.spin_length)

        self.status_bar = ObjectStatusBar(parent=self)

        vert_left = wx.BoxSizer(wx.VERTICAL)

        vert_left.Add(self.scroll_panel, proportion=1, flag=wx.EXPAND)
        # todo causes gtk warnings for some reason
        vert_left.Add(self.status_bar, flag=wx.EXPAND)

        vert_right = wx.BoxSizer(wx.VERTICAL)

        vert_right.Add(self.object_list, proportion=1, flag=wx.EXPAND)
        vert_right.Add(spinner_sizer, flag=wx.EXPAND)

        horiz_sizer.Add(vert_left, proportion=10, flag=wx.EXPAND)
        horiz_sizer.Add(vert_right, proportion=1, flag=wx.EXPAND)

        self.SetSizer(horiz_sizer)

        self.Bind(wx.EVT_LISTBOX, self.on_list_select)

        self.Bind(wx.EVT_SPINCTRL, self.on_spin)

        self.level_view.Bind(wx.EVT_LEFT_DOWN, self.start_drag)
        self.level_view.Bind(wx.EVT_MOTION, self.on_mouse_motion)
        self.level_view.Bind(wx.EVT_LEFT_UP, self.stop_drag)

        self.level_view.Bind(wx.EVT_RIGHT_DOWN, self.start_resize)
        self.level_view.Bind(wx.EVT_RIGHT_UP, self.stop_resize)

        self.dragging_object = None
        self.dragging_index = None
        self.dragging_offset = None

        self.resizing_object = None
        self.resizing_index = None

        self.Bind(wx.EVT_CLOSE, self.on_exit)

        self.Show()

        if not self.on_open_rom(None):
            quit()

    def update_title(self):
        self.SetTitle(f"{self.level_view.level.name} - {ROM.name}")

    def on_open_rom(self, _):
        if not self.safe_to_change():
            return

        # otherwise ask the user what new file to open
        with wx.FileDialog(self, "Open ROM", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
                           wildcard="NES files (.nes)|*.nes|ROM files (.rom)|*.rom|All files|*") as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return False

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            try:
                ROM.load_from_file(pathname)

                self.level_view.unload_level()

                self.update_level(world=1, level=1)

                return True
            except IOError:
                wx.LogError("Cannot open file '%s'." % pathname)

    def safe_to_change(self):
        if self.level_view.was_changed():
            answer = wx.MessageBox("Current content has not been saved! Proceed?", "Please confirm",
                                   wx.ICON_QUESTION | wx.YES_NO, self)

            return answer == wx.YES
        else:
            return True

    def on_save_rom(self, event):
        if event.GetId() == ID_SAVE_ROM_AS:
            with wx.FileDialog(self, "Save ROM as", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return  # the user changed their mind

                # save the current contents in the file
                pathname = fileDialog.GetPath()
        else:
            pathname = ROM.path

        try:
            level = self.level_view.level

            ROM().bulk_write(level.to_bytes(), level.offset)
            ROM().save_to_file(pathname)

            self.level_view.level.changed = False
        except IOError:
            wx.LogError("Cannot save current data in file '%s'." % pathname)

    def on_menu_checked(self, event):
        item_id = event.GetId()
        menu_item = event.GetEventObject().FindItemById(item_id)

        if not menu_item.IsCheckable():
            event.Skip()
            return

        checked = menu_item.IsChecked()

        if item_id == ID_GRID_LINES:
            self.level_view.grid_lines = checked
        elif item_id == ID_TRANSPARENCY:
            self.level_view.transparency = checked

        self.level_view.Refresh()

    def on_spin(self, event):
        _id = event.GetId()

        index = self.object_list.GetSelection()

        if index == -1:
            return

        level = self.level_view.level
        obj = level.objects[index]

        object_data = [(self.spin_domain.GetValue() << 5) | obj.y,
                       obj.x,
                       self.spin_type.GetValue()]

        if _id == ID_SPIN_LENGTH:
            object_data.append(self.spin_length.GetValue())
        else:
            object_data.append(0)

        self.level_view.level.objects[index] = LevelObject(object_data, level.object_set, level.plains_level,
                                                           level.object_palette_group,
                                                           self.level_view.level.pattern_table)
        self.level_view.level.changed = True

        self.level_view.Refresh()
        self.update_object_list()

        self.on_list_select(None)

    def update_object_list(self):
        index = self.object_list.GetSelection()
        item = self.object_list.GetString(index)

        description = self.level_view.level.objects[index].description

        if item != description:
            self.object_list.SetString(index, description)

    def fill_object_list(self):
        self.object_list.Clear()

        self.object_list.SetItems(self.level_view.level.get_object_names())

    def open_level_selector(self, _):
        if not self.safe_to_change():
            return

        self.level_selector.Show()
        self.level_selector.Raise()

    def on_block_viewer(self, _):
        if self.block_viewer is None:
            self.block_viewer = BlockViewer(parent=self)

        self.block_viewer.Show()
        self.block_viewer.Raise()

    def on_object_viewer(self, _):
        if self.object_viewer is None:
            self.object_viewer = ObjectViewer(parent=self)

        self.object_viewer.Show()
        self.object_viewer.Raise()

    def update_level(self, world, level, object_set=None):
        self.level_view.load_level(world=world, level=level, object_set=object_set)
        self.Fit()

        self.fill_object_list()
        self.update_title()

    def on_list_select(self, _):
        index = self.object_list.GetSelection()

        self.select_object(index=index)

    def on_mouse_motion(self, event):
        if self.dragging_object is not None:
            self.dragging(event)
        elif self.resizing_object is not None:
            self.resizing(event)
        else:
            return

    def start_resize(self, event):
        if self.dragging_object is not None:
            return

        x = event.Position.x
        y = event.Position.y

        obj = self.level_view.object_at(x, y)

        self.select_object(obj)

        if obj is None:
            return

        self.resizing_object = obj
        self.resizing_index = self.level_view.level.objects.index(obj)

    def resizing(self, event):
        if isinstance(self.level_view.level, WorldMap):
            return

        self.level_view.level.objects.remove(self.resizing_object)

        x = event.Position.x
        y = event.Position.y

        level_x, level_y = self.level_view.to_level_point(x, y)

        self.resizing_object.resize_to(level_x, level_y)

        self.status_bar.fill(self.resizing_object)

        self.level_view.level.objects.insert(self.resizing_index, self.resizing_object)

        self.spin_type.SetValue(self.resizing_object.obj_index)
        self.spin_length.SetValue(self.resizing_object.secondary_length)

        self.level_view.level.changed = True

        self.level_view.Refresh()

    def stop_resize(self, _):
        self.resizing_object = None
        self.resizing_index = None

    def start_drag(self, event):
        if self.resizing_object is not None:
            return

        x = event.Position.x
        y = event.Position.y

        obj = self.level_view.object_at(x, y)

        self.select_object(obj)

        if obj is None:
            return

        self.dragging_object = obj
        self.dragging_index = self.level_view.level.objects.index(obj)

        level_x, level_y = self.level_view.to_level_point(x, y)

        x_off = level_x - obj.rect.x
        y_off = level_y - obj.rect.y

        self.dragging_offset = (x_off, y_off)

        self.level_view.Refresh()

    def dragging(self, event):
        self.level_view.level.objects.remove(self.dragging_object)

        x = event.Position.x
        y = event.Position.y

        level_x, level_y = self.level_view.to_level_point(x, y)

        level_x -= self.dragging_offset[0]
        level_y -= self.dragging_offset[1]

        self.dragging_object.set_position(level_x, level_y)

        self.status_bar.fill(self.dragging_object)

        self.level_view.level.add_object(self.dragging_object, self.dragging_index)

        # todo find better way?
        if isinstance(self.level_view.level, WorldMap):
            self.fill_object_list()
            self.object_list.SetSelection(self.level_view.level.objects.index(self.dragging_object))

        self.level_view.level.changed = True

        self.level_view.Refresh()

    def stop_drag(self, _):
        self.dragging_object = None
        self.dragging_index = None
        self.dragging_offset = None

    def select_object(self, obj=None, index=None):
        should_scroll = True

        for _obj in self.level_view.level.objects:
            _obj.selected = False

        if obj is None and index is None:
            index = -1
            self.object_list.SetSelection(index)
            self.status_bar.clear()

        if index is None:
            # assume click on levelview
            should_scroll = False
            index = self.level_view.level.objects.index(obj)

        if index == -1:
            self.spin_domain.SetValue(0)
            self.spin_type.SetValue(0)
            self.spin_length.SetValue(0)

            self.spin_domain.Disable()
            self.spin_type.Disable()
            self.spin_length.Disable()

        else:
            if obj is None:
                # assume click on object_list
                should_scroll = True
                obj = self.level_view.level.objects[index]

            self.object_list.SetSelection(index)
            self.status_bar.fill(obj)

            obj.selected = True

            if isinstance(self.level_view.level, Level):
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

            if should_scroll:
                visible_blocks = self.scroll_panel.GetClientSize()[0] // self.scroll_panel.GetScrollPixelsPerUnit()[0]
                scroll_offset = visible_blocks // 2

                self.scroll_panel.Scroll(obj.level_x - scroll_offset, obj.level_y)

        self.level_view.Refresh()

    def on_exit(self, _):
        if not self.safe_to_change():
            return

        quit()
