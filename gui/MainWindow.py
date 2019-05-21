import wx
import wx.lib.scrolledpanel

from BlockViewer import BlockViewer
from ContextMenu import (
    ContextMenu,
    ID_CTX_REMOVE,
    ID_CTX_ADD_OBJECT,
    ID_CTX_ADD_ENEMY,
    ID_CTX_COPY,
    ID_CTX_PASTE,
    ID_CTX_CUT,
)
from Events import (
    EVT_REDO,
    EVT_UNDO,
    EVT_UNDO_COMPLETE,
    EVT_REDO_COMPLETE,
    EVT_UNDO_CLEARED,
    EVT_UNDO_SAVED,
)
from File import ROM
from Graphics import LevelObject
from HeaderEditor import HeaderEditor, EVT_HEADER_CHANGED
from Level import Level, WorldMap
from LevelSelector import LevelSelector
from LevelView import LevelView
from ObjectList import ObjectList
from ObjectStatusBar import ObjectStatusBar
from ObjectViewer import ObjectViewer
from SpinnerPanel import SpinnerPanel

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

CHECKABLE_MENU_ITEMS = [ID_TRANSPARENCY, ID_GRID_LINES]

# mouse modes

MODE_FREE = 0
MODE_DRAG = 1
MODE_RESIZE = 2


def undoable(func):
    def wrapped(self, *args):
        func(self, *args)
        self.level_view.save_level_state()

    return wrapped


class SMB3Foundry(wx.Frame):
    def __init__(self, *args, **kw):
        super(SMB3Foundry, self).__init__(
            title="SMB3Foundry", style=wx.MAXIMIZE | wx.DEFAULT_FRAME_STYLE, *args, **kw
        )

        file_menu = wx.Menu()

        file_menu.Append(ID_OPEN_ROM, "&Open ROM", "")
        file_menu.Append(ID_OPEN_M3L, "&Open M3L", "")
        file_menu.AppendSeparator()
        file_menu.Append(ID_SAVE_ROM, "&Save ROM", "")
        file_menu.Append(ID_SAVE_ROM_AS, "&Save ROM as ...", "")
        """
        file_menu.AppendSeparator()
        """
        file_menu.Append(ID_SAVE_M3L, "&Save M3L", "")
        """
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
        """
        level_menu.Append(ID_RELOAD_LEVEL, "&Reload Level", "")
        level_menu.AppendSeparator()
        level_menu.Append(ID_EDIT_HEADER, "&Edit Header", "")
        """
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
        self.Bind(wx.EVT_MENU, self.on_open_m3l, id=ID_OPEN_M3L)
        self.Bind(wx.EVT_MENU, self.on_save_rom, id=ID_SAVE_ROM)
        self.Bind(wx.EVT_MENU, self.on_save_rom, id=ID_SAVE_ROM_AS)
        self.Bind(wx.EVT_MENU, self.on_save_m3l, id=ID_SAVE_M3L)
        self.Bind(wx.EVT_MENU, self.on_exit, id=ID_EXIT)
        self.Bind(wx.EVT_MENU, self.open_level_selector, id=ID_SELECT_LEVEL)
        self.Bind(wx.EVT_MENU, self.on_block_viewer, id=ID_VIEW_BLOCKS)
        self.Bind(wx.EVT_MENU, self.on_object_viewer, id=ID_VIEW_OBJECTS)
        self.Bind(wx.EVT_MENU, self.on_header_editor, id=ID_EDIT_HEADER)

        self.context_menu = ContextMenu()

        self.Bind(wx.EVT_MENU, self.on_menu)

        self.Center()

        self.block_viewer = None
        self.object_viewer = None
        self.header_editor = None

        horiz_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.level_selector = LevelSelector(parent=self)

        self.scroll_panel = wx.lib.scrolledpanel.ScrolledPanel(self)

        self.level_view = LevelView(parent=self.scroll_panel)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.level_view)

        self.scroll_panel.SetSizer(sizer)

        self.object_list = ObjectList(self, self.context_menu)

        self.status_bar = ObjectStatusBar(parent=self)

        vert_left = wx.BoxSizer(wx.VERTICAL)

        vert_left.Add(self.scroll_panel, proportion=1, flag=wx.EXPAND)
        # todo causes gtk warnings for some reason
        vert_left.Add(self.status_bar, flag=wx.EXPAND)

        vert_right = wx.BoxSizer(wx.VERTICAL)

        self.spinner_panel = SpinnerPanel(self, self.level_view)

        vert_right.Add(self.spinner_panel, border=5, flag=wx.BOTTOM | wx.EXPAND)
        vert_right.Add(
            self.object_list,
            proportion=1,
            border=5,
            flag=wx.BOTTOM | wx.LEFT | wx.EXPAND,
        )

        horiz_sizer.Add(vert_left, proportion=10, flag=wx.EXPAND)
        horiz_sizer.Add(vert_right, proportion=1, flag=wx.EXPAND)

        self.SetSizer(horiz_sizer)

        self.Bind(wx.EVT_LISTBOX, self.on_list_select)

        self.Bind(wx.EVT_SPINCTRL, self.on_spin)

        self.level_view.Bind(wx.EVT_LEFT_DOWN, self.on_left_mouse_button_down)
        self.level_view.Bind(wx.EVT_LEFT_UP, self.on_left_mouse_button_up)

        self.level_view.Bind(wx.EVT_MOTION, self.on_mouse_motion)
        self.level_view.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel)
        self.level_view.Bind(wx.EVT_RIGHT_DOWN, self.on_right_mouse_button_down)
        self.level_view.Bind(wx.EVT_RIGHT_UP, self.on_right_mouse_button_up)

        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_press)

        self.Bind(EVT_REDO, self.on_redo)
        self.Bind(EVT_UNDO, self.on_undo)
        self.Bind(EVT_UNDO_COMPLETE, self.spinner_panel.disable_buttons)
        self.Bind(EVT_REDO_COMPLETE, self.spinner_panel.disable_buttons)
        self.Bind(EVT_UNDO_CLEARED, self.spinner_panel.disable_buttons)
        self.Bind(EVT_UNDO_SAVED, self.spinner_panel.disable_buttons)

        self.Bind(EVT_HEADER_CHANGED, self.on_header_change)

        self.mouse_mode = MODE_FREE

        self.resize_obj_start_point = 0, 0
        self.resize_mouse_start_x = 0
        self.resizing_happened = False

        self.drag_start_point = 0, 0
        self.dragging_happened = False

        self.last_mouse_position = 0, 0

        self.Bind(wx.EVT_CLOSE, self.on_exit)

        # this is needed, so that the scrolling panel doesn't reset
        # after a redraw. not sure why. only needs to happen once
        self.object_list.SetFocus()

        self.Show()

        if not self.on_open_rom(None):
            quit()

    def update_title(self):
        self.SetTitle(f"{self.level_view.level.name} - {ROM.name}")

    def on_open_rom(self, _):
        if not self.safe_to_change():
            return

        # otherwise ask the user what new file to open
        with wx.FileDialog(
            self,
            "Open ROM",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
            wildcard="NES files (.nes)|*.nes|ROM files (.rom)|*.rom|All files|*",
        ) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return False

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            try:
                ROM.load_from_file(pathname)

                self.update_level(world=1, level=1)

                return True
            except IOError:
                wx.LogError("Cannot open file '%s'." % pathname)

    def on_open_m3l(self, event):
        if not self.safe_to_change():
            return

        # otherwise ask the user what new file to open
        with wx.FileDialog(
            self,
            "Open M3L file",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
            wildcard="M3L files (.m3l)|*.m3l|All files|*",
        ) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return False

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, "rb") as m3l_file:

                    self.update_level(world=1, level=1)
                    self.level_view.from_m3l(bytearray(m3l_file.read()))

                    return True
            except IOError:
                wx.LogError("Cannot open file '%s'." % pathname)

    def safe_to_change(self):
        if self.level_view.was_changed():
            answer = wx.MessageBox(
                "Current content has not been saved! Proceed?",
                "Please confirm",
                wx.ICON_QUESTION | wx.YES_NO,
                self,
            )

            return answer == wx.YES
        else:
            return True

    def on_save_rom(self, event):
        if self.level_view.level.is_too_big():
            wx.MessageBox(
                "Level is too big to save.", "Error", wx.ICON_ERROR | wx.OK, self
            )

            return

        if event.GetId() == ID_SAVE_ROM_AS:
            with wx.FileDialog(
                self,
                "Save ROM as",
                style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                wildcard="NES files (.nes)|*.nes|ROM files (.rom)|*.rom|All files|*",
            ) as fileDialog:
                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return  # the user changed their mind

                # save the current contents in the file
                pathname = fileDialog.GetPath()
        else:
            pathname = ROM.path

        try:
            level = self.level_view.level

            for offset, data in level.to_bytes():
                ROM().bulk_write(data, offset)

            ROM().save_to_file(pathname)

            self.level_view.level.changed = False
        except IOError:
            wx.LogError("Cannot save current data in file '%s'." % pathname)

    def on_save_m3l(self, _):
        with wx.FileDialog(
            self,
            "Save M3L as",
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
            wildcard="M3L files (.m3l)|*.m3l|All files|*",
        ) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # save the current contents in the file
            pathname = fileDialog.GetPath()

        try:
            level = self.level_view.level

            with open(pathname, "wb") as m3l_file:
                m3l_file.write(level.to_m3l())
        except IOError:
            wx.LogError("Cannot save current data in file '%s'." % pathname)

    def on_menu(self, event):
        item_id = event.GetId()

        if item_id in CHECKABLE_MENU_ITEMS:
            self.on_menu_item_checked(event)
        elif item_id in self.context_menu.get_all_menu_item_ids():
            x, y = self.context_menu.get_position()

            level_x, level_y = self.level_view.level.to_level_point(x, y)

            if item_id == ID_CTX_REMOVE:
                self.remove_selected_objects()
            elif item_id == ID_CTX_ADD_OBJECT:
                self.add_object_at(level_x, level_y)
            elif item_id == ID_CTX_ADD_ENEMY:
                self.add_enemy_at(level_x, level_y)
            elif item_id == ID_CTX_CUT:
                self._cut_object()
            elif item_id == ID_CTX_COPY:
                self._copy_objects()
            elif item_id == ID_CTX_PASTE:
                self._paste_objects(level_x, level_y)

            self.object_list.update()

        elif item_id == ID_RELOAD_LEVEL:
            self.reload_level()
        else:
            event.Skip()

        self.level_view.Refresh()

    def reload_level(self):
        if not self.safe_to_change():
            return

        world = self.level_view.level.world
        level = self.level_view.level.level
        object_set = self.level_view.level.object_set

        self.update_level(world, level, object_set)

    @undoable
    def on_header_change(self, event):
        pass

    @undoable
    def add_object_at(self, level_x, level_y):
        self.level_view.level.create_object_at(level_x, level_y)

    @undoable
    def add_enemy_at(self, level_x, level_y):
        self.level_view.level.create_enemy_at(level_x, level_y)

    def on_undo(self, _):
        self.level_view.undo()

        self.object_list.update()

    def on_redo(self, _):
        self.level_view.redo()

        self.object_list.update()

    def _cut_object(self):
        self._copy_objects()
        self.remove_selected_objects()

    def _copy_objects(self):
        selected_objects = self.level_view.get_selected_objects().copy()

        if selected_objects:
            self.context_menu.set_copied_objects(selected_objects)

    @undoable
    def _paste_objects(self, x, y):
        objects, origin = self.context_menu.get_copied_objects()

        ori_x, ori_y = origin

        pasted_objects = []

        for obj in objects:
            obj_x, obj_y = obj.get_position()

            offset_x, offset_y = obj_x - ori_x, obj_y - ori_y

            try:
                pasted_objects.append(
                    self.level_view.level.paste_object_at(
                        x + offset_x, y + offset_y, obj
                    )
                )
            except ValueError:
                print("Tried pasting outside of level.")

        self.level_view.select_objects(pasted_objects)

        self.object_list.update()

    @undoable
    def remove_selected_objects(self):
        self.level_view.remove_selected_objects()
        self.object_list.remove_selected()
        self.select_object(None)

    def on_menu_item_checked(self, event):
        item_id = event.GetId()

        menu_item = event.GetEventObject().FindItemById(item_id)

        checked = menu_item.IsChecked()

        if item_id == ID_GRID_LINES:
            self.level_view.grid_lines = checked
        elif item_id == ID_TRANSPARENCY:
            self.level_view.transparency = checked

    @undoable
    def on_spin(self, event):
        _id = event.GetId()

        indexes = self.object_list.GetSelections()

        if len(indexes) != 1:
            return

        index = indexes[0]

        level = self.level_view.level
        old_object = level.get_object(index)
        level.remove_object(old_object)

        obj_index = self.spinner_panel.get_type()

        x = old_object.x_position
        y = old_object.y_position

        if isinstance(old_object, LevelObject):
            domain = self.spinner_panel.get_domain()

            if self.spinner_panel.is_length_spinner(_id):
                length = self.spinner_panel.get_length()
            else:
                length = None

            level.add_object(domain, obj_index, x, y, length, index)
        else:
            level.add_enemy(obj_index, x, y, index)

        self.level_view.Refresh()
        self.object_list.update()

        self.on_list_select(None)

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

    def on_header_editor(self, _):
        if self.header_editor is None:
            self.header_editor = HeaderEditor(
                parent=self, level_view_ref=self.level_view
            )

        self.header_editor.Show()
        self.header_editor.Raise()

    def update_level(self, world, level, object_set=None):
        self.level_view.load_level(world=world, level=level, object_set=object_set)
        self.Fit()

        if self.header_editor is not None:
            self.header_editor.reload_level()

        self.object_list.fill()
        self.update_title()

        m3l_export_not_for_world_maps = world != 0

        self.GetMenuBar().FindItemById(ID_SAVE_M3L).Enable(
            m3l_export_not_for_world_maps
        )

    def on_list_select(self, _):
        indexes = self.object_list.GetSelections()

        self.level_view.set_selected_objects_by_index(indexes)

        # activate scrolling and object editing, when only one is selected
        if len(indexes) == 1:
            self.select_object(index=indexes[0])
        else:
            self.spinner_panel.disable_all()

    def on_key_press(self, event: wx.KeyEvent):
        key = event.GetKeyCode()

        if key in [wx.WXK_DELETE, wx.WXK_NUMPAD_DELETE]:
            self.remove_selected_objects()
        elif event.ControlDown():
            key = event.GetUnicodeKey()
            if key == wx.WXK_NONE:
                return

            if key == ord("C"):
                self._copy_objects()
            elif key == ord("V"):
                self._paste_objects(*self.last_mouse_position)
            elif key == ord("X"):
                self._cut_object()

            self.level_view.Refresh()

    def on_mouse_motion(self, event):
        if self.mouse_mode == MODE_DRAG:
            self.dragging(event)
        elif self.mouse_mode == MODE_RESIZE:
            self.resizing(event)
        else:
            if self.level_view.selection_square.active:
                self.level_view.set_selection_end(event.GetPosition())

                self.object_list.SetSelection(wx.NOT_FOUND)

                for obj in self.level_view.get_selected_objects():
                    self.object_list.SetSelection(self.level_view.level.index_of(obj))

    def on_mouse_wheel(self, event):
        obj_under_cursor = self.level_view.object_at(*event.GetPosition().Get())

        if obj_under_cursor is None:
            event.Skip()
        else:
            self.change_object_on_mouse_wheel(event)

    @undoable
    def change_object_on_mouse_wheel(self, event):
        obj_under_cursor = self.level_view.object_at(*event.GetPosition().Get())

        if event.GetWheelRotation() > 0:
            obj_under_cursor.increment_type()
        else:
            obj_under_cursor.decrement_type()

        self.select_object(obj=obj_under_cursor)
        self.object_list.update()

        self.level_view.Refresh()

    def select_objects_on_click(self, event):
        x, y = event.GetPosition().Get()
        level_x, level_y = self.level_view.to_level_point(x, y)

        self.last_mouse_position = level_x, level_y

        clicked_object = self.level_view.object_at(x, y)

        clicked_on_background = clicked_object is None

        if clicked_on_background:
            self.select_object(None)
        else:
            self.mouse_mode = MODE_DRAG

            selected_objects = self.level_view.get_selected_objects()

            nothing_selected = not selected_objects

            if nothing_selected or clicked_object not in selected_objects:
                self.select_object(clicked_object)

        return not clicked_on_background

    def on_right_mouse_button_down(self, event):
        if self.mouse_mode == MODE_DRAG:
            return

        x, y = event.GetPosition().Get()
        level_x, level_y = self.level_view.to_level_point(x, y)

        self.last_mouse_position = level_x, level_y

        if self.select_objects_on_click(event):
            self.mouse_mode = MODE_RESIZE

            self.resize_mouse_start_x = level_x

            obj = self.level_view.object_at(x, y)

            self.resize_obj_start_point = obj.x_position, obj.y_position

    def resizing(self, event):
        self.resizing_happened = True

        if isinstance(self.level_view.level, WorldMap):
            return

        x, y = event.GetPosition().Get()

        level_x, level_y = self.level_view.to_level_point(x, y)

        dx = level_x - self.resize_obj_start_point[0]
        dy = level_y - self.resize_obj_start_point[1]

        self.last_mouse_position = level_x, level_y

        for obj in self.level_view.get_selected_objects():
            obj.resize_by(dx, dy)

            self.status_bar.fill(obj)

            self.spinner_panel.set_type(obj.obj_index)

            if obj.is_4byte:
                self.spinner_panel.spin_length(obj.data[3])

            self.level_view.level.changed = True

        self.level_view.Refresh()

    def on_right_mouse_button_up(self, event):
        if self.resizing_happened:
            x, y = event.GetPosition().Get()

            resize_end_x, _ = self.level_view.to_level_point(x, y)

            if self.resize_mouse_start_x != resize_end_x:
                self.stop_resize(event)
        else:
            if self.level_view.get_selected_objects():
                menu = self.context_menu.as_object_menu()
            else:
                menu = self.context_menu.as_background_menu()

            adjusted_for_scrolling = self.ScreenToClient(
                self.level_view.ClientToScreen(event.GetPosition())
            )

            self.context_menu.set_position(event.GetPosition())

            self.PopupMenu(menu, adjusted_for_scrolling)

        self.resizing_happened = False
        self.mouse_mode = MODE_FREE

    @undoable
    def stop_resize(self, _):
        self.resizing_happened = False
        self.mouse_mode = MODE_FREE

    def on_left_mouse_button_down(self, event):
        if self.mouse_mode == MODE_RESIZE:
            return

        if self.select_objects_on_click(event):
            x, y = event.GetPosition().Get()

            obj = self.level_view.object_at(x, y)

            self.drag_start_point = obj.x_position, obj.y_position
        else:
            self.level_view.start_selection_square(event.GetPosition())

    def dragging(self, event):
        self.dragging_happened = True

        x, y = event.GetPosition().Get()

        level_x, level_y = self.level_view.to_level_point(x, y)

        dx = level_x - self.last_mouse_position[0]
        dy = level_y - self.last_mouse_position[1]

        self.last_mouse_position = level_x, level_y

        for obj in self.level_view.get_selected_objects():
            obj.move_by(dx, dy)

            # todo how does this work with multi selections?
            self.status_bar.fill(obj)

            # todo find better way?
            if isinstance(self.level_view.level, WorldMap):
                self.object_list.fill()
                self.object_list.SetSelection(self.level_view.level.objects.index(obj))

            self.level_view.level.changed = True

        self.level_view.Refresh()

    def on_left_mouse_button_up(self, event):
        if self.mouse_mode == MODE_DRAG and self.dragging_happened:
            x, y = event.GetPosition().Get()

            obj = self.level_view.object_at(x, y)

            drag_end_point = obj.x_position, obj.y_position

            if self.drag_start_point != drag_end_point:
                self.stop_drag()
            else:
                self.dragging_happened = False
        else:
            self.level_view.stop_selection_square()

        self.mouse_mode = MODE_FREE

    @undoable
    def stop_drag(self):
        self.dragging_happened = False

    def select_object(self, obj=None, index=None):
        should_scroll = True

        self.level_view.select_object(None)
        self.object_list.SetSelection(wx.NOT_FOUND)

        if obj is None and index is None:
            index = -1
            self.object_list.SetSelection(index)
            self.status_bar.clear()

        if index is None:
            # assume click on levelview
            should_scroll = False
            index = self.level_view.level.index_of(obj)

        if index == wx.NOT_FOUND:
            self.spinner_panel.disable_all()
        else:
            if obj is None:
                # assume click on object_list
                should_scroll = True
                obj = self.level_view.level.get_object(index)

            self.object_list.SetSelection(index)
            self.status_bar.fill(obj)

            self.level_view.select_object(obj)

            if isinstance(self.level_view.level, Level):
                if isinstance(obj, LevelObject):
                    self.spinner_panel.enable_domain(True, obj.domain)
                else:
                    self.spinner_panel.enable_domain(False)

                self.spinner_panel.enable_type(True, obj.obj_index)

                if obj.is_4byte:
                    self.spinner_panel.enable_length(True, obj.length)
                else:
                    self.spinner_panel.enable_length(False)

            if should_scroll:
                visible_blocks = (
                    self.scroll_panel.GetClientSize()[0]
                    // self.scroll_panel.GetScrollPixelsPerUnit()[0]
                )
                scroll_offset = visible_blocks // 2

                self.scroll_panel.Scroll(obj.x_position - scroll_offset, obj.y_position)

        self.level_view.Refresh()

    def on_exit(self, _):
        if not self.safe_to_change():
            return

        quit()
