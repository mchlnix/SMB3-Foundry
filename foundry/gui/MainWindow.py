import os
from typing import Tuple, Optional, Union

import wx
import wx.lib.scrolledpanel

from foundry.game.File import ROM
from foundry.game.gfx.objects.EnemyItem import EnemyObject
from foundry.game.gfx.objects.LevelObject import LevelObject
from foundry.game.level.Level import Level
from foundry.game.level.WorldMap import WorldMap
from foundry.gui.AboutWindow import AboutDialog
from foundry.gui.BlockViewer import BlockViewer
from foundry.gui.ContextMenu import (
    ContextMenu,
    ID_CTX_REMOVE,
    ID_CTX_ADD_OBJECT,
    ID_CTX_ADD_ENEMY,
    ID_CTX_COPY,
    ID_CTX_PASTE,
    ID_CTX_CUT,
)
from foundry.gui.Events import (
    EVT_REDO,
    EVT_UNDO,
    EVT_UNDO_COMPLETE,
    EVT_REDO_COMPLETE,
    EVT_UNDO_CLEARED,
    EVT_UNDO_SAVED,
    EVT_OBJ_LIST,
    ObjectListUpdateEvent,
    EVT_JUMP_LIST,
    EVT_JUMP_UPDATE,
    EVT_JUMP_ADDED,
    EVT_JUMP_REMOVED,
)
from foundry.gui.HeaderEditor import HeaderEditor, EVT_HEADER_CHANGED
from foundry.gui.JumpEditor import JumpEditor
from foundry.gui.JumpList import JumpList
from foundry.gui.LevelSelector import LevelSelector
from foundry.gui.LevelView import LevelView
from foundry.gui.ObjectDropdown import ObjectDropdown
from foundry.gui.ObjectList import ObjectList
from foundry.gui.ObjectStatusBar import ObjectStatusBar
from foundry.gui.ObjectViewer import ObjectViewer
from foundry.gui.SpinnerPanel import SpinnerPanel, ID_SPIN_DOMAIN, ID_SPIN_TYPE, ID_SPIN_LENGTH

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
ID_FREE_FORM_MODE = 206
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
ID_JUMPS = 509
ID_SCREEN_SHOT = 510

# help menu

ID_ENEMY_COMPATIBILITY = 601
ID_TROUBLESHOOTING = 602
ID_PROGRAM_WEBSITE = 603
ID_MAKE_A_DONATION = 604
ID_ABOUT = 605

CHECKABLE_MENU_ITEMS = [ID_TRANSPARENCY, ID_GRID_LINES, ID_JUMPS]

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

        self.SetIcon(wx.Icon("data/foundry.ico"))

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

        """
        edit_menu = wx.Menu()

        edit_menu.Append(ID_EDIT_LEVEL, "&Edit Level", "")
        edit_menu.Append(ID_EDIT_OBJ_DEFS, "&Edit Object Definitions", "")
        edit_menu.Append(ID_EDIT_PALETTE, "&Edit Palette", "")
        edit_menu.Append(ID_EDIT_GRAPHICS, "&Edit Graphics", "")
        edit_menu.Append(ID_EDIT_MISC, "&Edit Miscellaneous", "")
        edit_menu.AppendSeparator()
        edit_menu.Append(ID_FREE_FORM_MODE, "&Free form Mode", "")
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

        view_menu.AppendCheckItem(ID_JUMPS, "Jumps")
        view_menu.AppendCheckItem(ID_GRID_LINES, "&Grid lines", "")
        view_menu.AppendCheckItem(ID_TRANSPARENCY, "&Block Transparency", "")
        view_menu.FindItemById(ID_TRANSPARENCY).Check(True)
        view_menu.AppendSeparator()
        view_menu.Append(ID_SCREEN_SHOT, "&Save Screenshot of Level", "")
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
        """
        help_menu.Append(ID_ABOUT, "&About", "")

        menu_bar = wx.MenuBar()

        menu_bar.Append(file_menu, "&File")
        # menu_bar.Append(edit_menu, "&Edit")
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
        self.Bind(wx.EVT_MENU, self.on_about, id=ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.on_screenshot, id=ID_SCREEN_SHOT)

        self.context_menu = ContextMenu()

        self.Bind(wx.EVT_MENU, self.on_menu)

        self.Center()

        self.block_viewer = None
        self.object_viewer = None
        self.header_editor = None

        horiz_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.level_selector = LevelSelector(parent=self)

        self.scroll_panel = wx.lib.scrolledpanel.ScrolledPanel(self)

        self.level_view = LevelView(self.scroll_panel, self.context_menu)

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

        self.object_dropdown = ObjectDropdown(self)

        vert_right.Add(
            self.object_dropdown, border=5, flag=wx.BOTTOM | wx.LEFT | wx.EXPAND
        )

        vert_right.Add(
            self.object_list,
            proportion=1,
            border=5,
            flag=wx.BOTTOM | wx.LEFT | wx.EXPAND,
        )

        panel = wx.CollapsiblePane(self, wx.ID_ANY, "Jumps")

        win = panel.GetPane()

        self.jump_list = JumpList(win)

        self.Bind(EVT_JUMP_LIST, self.on_jump_list_change)
        self.Bind(EVT_JUMP_ADDED, self.on_jump_added)
        self.Bind(EVT_JUMP_REMOVED, self.on_jump_removed)

        panel_sizer = wx.BoxSizer(wx.VERTICAL)
        win.SetSizer(panel_sizer)
        panel_sizer.Add(self.jump_list, border=5, flag=wx.BOTTOM | wx.LEFT | wx.EXPAND)

        vert_right.Add(panel, 0, wx.GROW | wx.ALL, 5)

        horiz_sizer.Add(vert_left, proportion=10, flag=wx.EXPAND)
        horiz_sizer.Add(vert_right, proportion=0, flag=wx.EXPAND)

        self.jump_list.Bind(wx.EVT_LISTBOX_DCLICK, self.on_jump_double_click)

        self.SetSizer(horiz_sizer)

        self.Bind(wx.EVT_LISTBOX, self.on_list_select)

        self.Bind(wx.EVT_SPINCTRL, self.on_spin, id=ID_SPIN_DOMAIN)
        self.Bind(wx.EVT_SPINCTRL, self.on_spin, id=ID_SPIN_TYPE)
        self.Bind(wx.EVT_SPINCTRL, self.on_spin, id=ID_SPIN_LENGTH)

        self.level_view.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel)
        self.level_view.Bind(wx.EVT_MIDDLE_UP, self.on_middle_click)

        self.Bind(EVT_OBJ_LIST, self.on_objects_selected)

        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_press)

        self.Bind(EVT_REDO, self.on_redo)
        self.Bind(EVT_UNDO, self.on_undo)
        self.Bind(EVT_UNDO_COMPLETE, self.spinner_panel.disable_buttons)
        self.Bind(EVT_REDO_COMPLETE, self.spinner_panel.disable_buttons)
        self.Bind(EVT_UNDO_CLEARED, self.spinner_panel.disable_buttons)
        self.Bind(EVT_UNDO_SAVED, self.spinner_panel.disable_buttons)

        self.Bind(EVT_HEADER_CHANGED, self.on_header_change)
        self.Bind(EVT_JUMP_UPDATE, self.on_jump_change)

        self.resize_obj_start_point = 0, 0
        self.resize_mouse_start_x = 0
        self.resizing_happened = False

        self.drag_start_point = 0, 0
        self.dragging_happened = False

        self.Bind(wx.EVT_CLOSE, self.on_exit)

        # this is needed, so that the scrolling panel doesn't reset
        # after a redraw. not sure why. only needs to happen once
        self.object_list.SetFocus()

        self.Show()

        if not self.on_open_rom(None):
            wx.Exit()

    def on_screenshot(self, _) -> bool:
        if self.level_view is None:
            return False

        with wx.FileDialog(
            self,
            "Save Screenshot",
            defaultFile=f"{ROM.name} - {self.level_view.level.name}.png",
            defaultDir=os.path.expanduser("~"),
            style=wx.FD_SAVE,
            wildcard="Bitmap files (.png)|*.png|All files|*",
        ) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return False

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            try:
                dc = wx.MemoryDC()

                bitmap = self.level_view.make_screenshot(dc)

                dc.SelectObject(wx.NullBitmap)

                img = bitmap.ConvertToImage()

                img.SaveFile(pathname, wx.BITMAP_TYPE_PNG)

                return True
            except IOError:
                wx.LogError("Cannot save file '%s'." % pathname)

                return False

    def update_title(self):
        self.SetTitle(f"{self.level_view.level.name} - {ROM.name}")

    def on_open_rom(self, _) -> bool:
        if not self.safe_to_change():
            return False

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

                self.level_view.level = None

                self.open_level_selector(None)

                return True
            except IOError:
                wx.LogError("Cannot open file '%s'." % pathname)

                return False

    def on_open_m3l(self, _) -> bool:
        if not self.safe_to_change():
            return False

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

                    self.level_view.from_m3l(bytearray(m3l_file.read()))
            except IOError:
                wx.LogError("Cannot open file '%s'." % pathname)

        self.level_view.level.name = os.path.basename(pathname)

        self.set_up_gui_for_level()

        return True

    def safe_to_change(self) -> bool:
        if self.level_view.was_changed():
            answer = wx.MessageBox(
                "Current content has not been saved! Proceed?",
                "Please confirm",
                wx.ICON_QUESTION | wx.YES_NO | wx.NO_DEFAULT,
                self,
            )

            return answer == wx.YES
        else:
            return True

    def on_save_rom(self, event):
        is_save_as = event.GetId() == ID_SAVE_ROM_AS

        safe_to_save, reason, additional_info = self.level_view.level_safe_to_save()

        if not safe_to_save:
            answer = wx.MessageBox(
                f"{additional_info}\n\nDo you want to proceed?",
                reason,
                wx.ICON_WARNING | wx.YES_NO | wx.NO_DEFAULT,
                self,
            )

            if answer == wx.NO:
                return

        if not self.level_view.level.attached_to_rom:
            wx.MessageBox(
                "Please select the positions in the ROM you want the level objects and enemies/items to be stored.",
                "Importing M3L into ROM",
                wx.ICON_INFORMATION | wx.OK,
                self,
            )

            answer = self.level_selector.ShowModal()

            if answer == wx.OK:
                self.level_view.level.attach_to_rom(
                    self.level_selector.object_data_offset,
                    self.level_selector.enemy_data_offset,
                )

                if is_save_as:
                    # if we save to another rom, don't consider the level
                    # attached (to the current rom)
                    self.level_view.level.attached_to_rom = False
            else:
                return

        if is_save_as:
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

            self.update_title()

            self.level_view.level.changed = False
        except IOError:
            wx.LogError("Cannot save current data in file '%s'." % pathname)

    def on_save_m3l(self, _):
        suggested_file = self.level_view.level.name

        if not suggested_file.endswith(".m3l"):
            suggested_file += ".m3l"

        with wx.FileDialog(
            self,
            "Save M3L as",
            defaultFile=suggested_file,
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

            if item_id == ID_CTX_REMOVE:
                self.remove_selected_objects()
            elif item_id == ID_CTX_ADD_OBJECT:
                selected_object = self.object_dropdown.GetSelection()

                if selected_object == wx.NOT_FOUND:
                    self.create_object_at(x, y)
                else:
                    self.place_object_from_dropdown(selected_object, (x, y))
            elif item_id == ID_CTX_ADD_ENEMY:
                self.create_enemy_at(x, y)
            elif item_id == ID_CTX_CUT:
                self._cut_object()
            elif item_id == ID_CTX_COPY:
                self._copy_objects()
            elif item_id == ID_CTX_PASTE:
                self._paste_objects(x, y)

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
        object_data = self.level_view.level.object_offset
        enemy_data = self.level_view.level.enemy_offset
        object_set = self.level_view.level.object_set

        self.update_level(world, level, object_data, enemy_data, object_set)

    @undoable
    def on_header_change(self, event):
        pass

    @undoable
    def create_object_at(self, x, y):
        self.level_view.create_object_at(x, y)

    @undoable
    def create_enemy_at(self, x, y):
        self.level_view.create_enemy_at(x, y)

    def on_undo(self, _):
        self.level_view.undo()

        if self.header_editor is not None:
            self.header_editor.refresh()

        self.object_list.update()
        self.jump_list.update()

    def on_redo(self, _):
        self.level_view.redo()

        if self.header_editor is not None:
            self.header_editor.refresh()

        self.object_list.update()
        self.jump_list.update()

    def _cut_object(self):
        self._copy_objects()
        self.remove_selected_objects()

    def _copy_objects(self):
        selected_objects = self.level_view.get_selected_objects().copy()

        if selected_objects:
            self.context_menu.set_copied_objects(selected_objects)

    @undoable
    def _paste_objects(self, x=None, y=None):
        self.level_view.paste_objects_at(
            self.context_menu.get_copied_objects(), x, y
        )

        self.object_list.update()

    @undoable
    def remove_selected_objects(self):
        self.level_view.remove_selected_objects()
        self.object_list.remove_selected()
        self.deselect_all()

    def on_menu_item_checked(self, event):
        item_id = event.GetId()

        menu_item = event.GetEventObject().FindItemById(item_id)

        checked = menu_item.IsChecked()

        if item_id == ID_GRID_LINES:
            self.level_view.grid_lines = checked
        elif item_id == ID_TRANSPARENCY:
            self.level_view.transparency = checked
        elif item_id == ID_JUMPS:
            self.level_view.jumps = checked

    @undoable
    def on_spin(self, event):
        _id = event.GetId()

        indexes = self.object_list.GetSelections()

        if len(indexes) != 1:
            return

        index = indexes[0]

        old_object = self.level_view.get_object(index)

        obj_index = self.spinner_panel.get_type()

        if isinstance(old_object, LevelObject):
            domain = self.spinner_panel.get_domain()

            if self.spinner_panel.is_length_spinner(_id):
                length = self.spinner_panel.get_length()
            else:
                length = None

            self.level_view.replace_object(old_object, domain, obj_index, length)
        else:
            self.level_view.replace_enemy(old_object, obj_index)

        self.level_view.Refresh()
        self.object_list.update()

        self.on_list_select(None)

    def fill_object_list(self):
        self.object_list.Clear()

        self.object_list.SetItems(self.level_view.get_object_names())

    def open_level_selector(self, _):
        if not self.safe_to_change():
            return

        answer = self.level_selector.ShowModal()

        if answer == wx.OK:
            self.update_level(
                self.level_selector.selected_world,
                self.level_selector.selected_level,
                self.level_selector.object_data_offset,
                self.level_selector.enemy_data_offset,
                self.level_selector.object_set,
            )

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

    def update_level(
        self,
        world: int,
        level: int,
        object_data_offset: int,
        enemy_data_offset: int,
        object_set: int,
    ):
        try:
            self.level_view.load_level(
                world, level, object_data_offset, enemy_data_offset, object_set
            )
        except IndexError:
            wx.MessageBox(
                "Failed loading level. The level offsets don't match.",
                "Please confirm",
                wx.ICON_ERROR | wx.OK,
                self,
            )

            return

        self.set_up_gui_for_level()

    def set_up_gui_for_level(self):
        self.Fit()

        if self.header_editor is not None and isinstance(self.level_view.level, Level):
            self.header_editor.reload_level()

        self.object_list.fill()
        self.update_title()

        is_a_world_map = self.level_view.level.world == 0

        self.GetMenuBar().FindItemById(ID_SAVE_M3L).Enable(not is_a_world_map)
        self.GetMenuBar().FindItemById(ID_EDIT_HEADER).Enable(not is_a_world_map)

        if is_a_world_map:
            self.object_dropdown.Clear()
            self.object_dropdown.Enable(False)

            self.jump_list.Enable(False)
            self.jump_list.Clear()
        else:
            self.object_dropdown.Enable(True)
            self.object_dropdown.set_object_factory(
                self.level_view.level.object_factory
            )

            self.jump_list.Enable(True)

    def on_list_select(self, _):
        indexes = self.object_list.GetSelections()

        self.level_view.set_selected_objects_by_index(indexes)

        # activate scrolling and object editing, when only one is selected
        if len(indexes) == 1:
            self.select_object(index=indexes[0])
        else:
            self.spinner_panel.disable_all()

    def on_jump_double_click(self, event):
        index = event.Int

        jump_editor = JumpEditor(self, self.level_view.level.jumps[index], index)

        jump_editor.Show()

    @undoable
    def on_jump_added(self, event):
        self.level_view.add_jump(event)

    @undoable
    def on_jump_removed(self, event):
        self.level_view.remove_jump(event)

    @undoable
    def on_jump_change(self, event):
        index = event.index
        jump = event.jump

        if isinstance(self.level_view.level, Level):
            self.level_view.level.jumps[index] = jump
            self.jump_list.SetString(index, str(jump))

    def on_jump_list_change(self, event):
        self.jump_list.set_jumps(event)

    def on_key_press(self, event: wx.KeyEvent):
        widget = self.FindFocus()

        if isinstance(widget, wx.Control) and widget != self.object_list:
            # check if we are in a widget taking user input. ignore our shortcuts, then
            # the default widget with keyboard focus is the object list for some reason, so don't ignore then
            event.Skip()

            return

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
                self._paste_objects()
            elif key == ord("X"):
                self._cut_object()

            self.level_view.Refresh()
        else:
            event.Skip()

    def on_middle_click(self, event):
        index = self.object_dropdown.GetSelection()

        if index == wx.NOT_FOUND:
            return
        else:
            pos = event.GetPosition().Get()

            self.place_object_from_dropdown(index, pos)

    @undoable
    def place_object_from_dropdown(self, index: int, pos: Tuple[int, int]) -> None:
        domain, object_index = self.object_dropdown.GetClientData(index)

        self.level_view.create_object_at(*pos, domain, object_index)

        self.object_list.update()

    def on_mouse_wheel(self, event):

        obj_under_cursor = self.level_view.object_at(*event.GetPosition().Get())

        if obj_under_cursor is None:
            event.Skip()
        else:
            if isinstance(self.level_view.level, WorldMap):
                return

            # scrolling through the level could unintentionally change objects, if the cursor would wander onto them.
            # this is annoying (to me) so only change already selected objects
            if obj_under_cursor not in self.level_view.selected_objects:
                return

            self.change_object_on_mouse_wheel(event)

    @undoable
    def change_object_on_mouse_wheel(self, event):
        obj_under_cursor = self.level_view.object_at(*event.GetPosition().Get())

        if event.GetWheelRotation() > 0:
            obj_under_cursor.increment_type()
        else:
            obj_under_cursor.decrement_type()

        self.select_object(obj=obj_under_cursor)
        self.object_list.fill()

        self.level_view.Refresh()

    def on_objects_selected(self, event):
        objects = event.objects

        self.status_bar.clear()
        self.spinner_panel.disable_all()
        self.object_list.SetSelection(wx.NOT_FOUND)

        for index in event.indexes:
            self.object_list.SetSelection(index)

        if len(objects) == 1:
            obj = objects[0]
            self.status_bar.fill(obj)

            if isinstance(obj, LevelObject):
                self.spinner_panel.set_type(obj.obj_index)
                self.spinner_panel.set_domain(obj.domain)

                if obj.is_4byte:
                    self.spinner_panel.set_length(obj.data[3])
            elif isinstance(obj, EnemyObject):
                self.spinner_panel.set_type(obj.obj_index)

    def deselect_all(self):
        self.level_view.select_object(None)

        self.spinner_panel.disable_all()

    def select_object(self, obj: Optional[Union[LevelObject, EnemyObject]] = None, index: Optional[int] = None):
        should_scroll = True

        self.level_view.select_object(None)
        self.object_list.SetSelection(wx.NOT_FOUND)

        if obj is None and index is None:
            index = -1
            self.on_objects_selected(
                ObjectListUpdateEvent(id=wx.ID_ANY, objects=[], indexes=[])
            )

        if index is None:
            # assume click on LevelView
            should_scroll = False
            index = self.level_view.index_of(obj)

        if index == wx.NOT_FOUND:
            self.spinner_panel.disable_all()
        else:
            if obj is None:
                # assume click on object_list
                should_scroll = True
                obj = self.level_view.get_object(index)

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

    def on_about(self, _):
        about = AboutDialog(self)

        about.Show()

    def on_exit(self, _):
        if not self.safe_to_change():
            return

        self.Destroy()
