import wx

from game.Data import level_array, world_indexes
from game.level.Level import Level

WORLD_ITEMS = [
    "World Maps",
    "World 1",
    "World 2",
    "World 3",
    "World 4",
    "World 5",
    "World 6",
    "World 7",
    "World 8",
    "Lost Levels",
]

OBJECT_SET_ITEMS = [
    "0 Overworld",
    "1 Plains",
    "2 Dungeon",
    "3 Hilly",
    "4 Sky",
    "5 Piranha Plant",
    "6 Water",
    "7 Mushroom",
    "8 Pipe",
    "9 Desert",
    "A Ship",
    "B Giant",
    "C Ice",
    "D Cloudy",
    "E Underground",
    "F Spade Bonus",
]


SPINNER_MAX_VALUE = 0xFF_FF_FF  # arbitrary; 16,7 MB
OVERWORLD_MAPS_INDEX = 0
WORLD_1_INDEX = 1


class LevelSelector(wx.Frame):
    def __init__(self, parent):
        super(LevelSelector, self).__init__(parent, title="Level Selector")
        self.selected_world = 1
        self.selected_level = 1

        self.Bind(wx.EVT_CLOSE, self.on_exit)

        self.world_label = wx.StaticText(self, label="World")
        self.world_list = wx.ListBox(parent=self)
        self.world_list.InsertItems(WORLD_ITEMS, 0)

        self.Bind(wx.EVT_LISTBOX, self.on_world_click, id=self.world_list.GetId())

        self.level_label = wx.StaticText(self, label="Level")
        self.level_list = wx.ListBox(parent=self)

        self.Bind(wx.EVT_LISTBOX, self.on_level_click, id=self.level_list.GetId())

        self.enemy_data_label = wx.StaticText(self, label="Enemy Data")
        self.enemy_data_spinner = wx.SpinCtrl(self, min=0, max=SPINNER_MAX_VALUE)
        self.enemy_data_spinner.SetBase(16)

        self.object_data_label = wx.StaticText(self, label="Object Data")
        self.object_data_spinner = wx.SpinCtrl(self, min=0, max=SPINNER_MAX_VALUE)
        self.object_data_spinner.SetBase(16)

        self.object_set_label = wx.StaticText(self, label="Object Set")
        self.object_set_dropdown = wx.ComboBox(self, choices=OBJECT_SET_ITEMS)

        self.button_ok = wx.Button(self, id=wx.ID_OK)
        self.button_cancel = wx.Button(self, id=wx.ID_CANCEL)

        border_width = 5

        self.window_sizer = wx.FlexGridSizer(cols=2, vgap=0, hgap=0)

        self.window_sizer.Add(self.world_label, flag=wx.ALL, border=border_width)
        self.window_sizer.Add(self.level_label, flag=wx.ALL, border=border_width)

        self.window_sizer.Add(
            self.world_list, flag=wx.ALL | wx.EXPAND, border=border_width
        )
        self.window_sizer.Add(
            self.level_list, flag=wx.ALL | wx.EXPAND, border=border_width
        )

        self.window_sizer.Add(self.enemy_data_label, flag=wx.ALL, border=border_width)
        self.window_sizer.Add(self.object_data_label, flag=wx.ALL, border=border_width)
        self.window_sizer.Add(self.enemy_data_spinner, flag=wx.ALL, border=border_width)
        self.window_sizer.Add(
            self.object_data_spinner, flag=wx.ALL, border=border_width
        )

        self.window_sizer.Add(
            self.object_set_label,
            flag=wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL,
            border=border_width,
        )
        self.window_sizer.Add(
            self.object_set_dropdown, flag=wx.ALL | wx.EXPAND, border=border_width
        )

        self.window_sizer.Add(
            self.button_ok, flag=wx.ALL | wx.ALIGN_RIGHT, border=border_width
        )
        self.window_sizer.Add(self.button_cancel, flag=wx.ALL, border=border_width)

        self.SetSizerAndFit(self.window_sizer)

        self.Bind(wx.EVT_BUTTON, self.on_ok, id=self.button_ok.GetId())
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.on_ok)
        self.Bind(wx.EVT_BUTTON, self.on_exit, id=self.button_cancel.GetId())

        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_press)

        self.world_list.Select(1)  # select Level 1-1
        self.on_world_click(None)

    def on_key_press(self, event):
        key = event.GetKeyCode()

        if key == wx.WXK_ESCAPE:
            self.on_exit(None)
        else:
            event.Skip()

    def on_world_click(self, _):
        index = self.world_list.GetSelection()

        assert index >= 0

        self.level_list.Clear()

        # skip first meaningless item
        for level in level_array[1:]:
            if level.game_world == index:
                if level.name:
                    self.level_list.Append(level.name)

        if not self.level_list.IsEmpty():
            self.level_list.Select(0)

            self.on_level_click(None)

    def on_level_click(self, _):
        index = self.level_list.GetSelection()

        assert index >= 0

        self.selected_world = self.world_list.GetSelection()
        self.selected_level = index + 1

        if self.selected_world == OVERWORLD_MAPS_INDEX:  # over-world maps
            level_array_offset = self.selected_level
        else:
            level_array_offset = (
                world_indexes[self.selected_world] + self.selected_level
            )

        object_data_for_lvl = level_array[level_array_offset].rom_level_offset

        if self.selected_world >= WORLD_1_INDEX:
            object_data_for_lvl -= Level.HEADER_LENGTH

        self.object_data_spinner.SetValue(object_data_for_lvl)

        if self.selected_world >= WORLD_1_INDEX:
            enemy_data_for_lvl = level_array[level_array_offset].enemy_offset
        else:
            enemy_data_for_lvl = 0

        if enemy_data_for_lvl > 0:
            enemy_data_for_lvl -= 1

        self.enemy_data_spinner.SetValue(enemy_data_for_lvl)

        # if self.selected_world >= WORLD_1_INDEX:
        object_set_index = level_array[level_array_offset].real_obj_set
        self.object_set_dropdown.SetSelection(object_set_index)

        print(
            f"Level {self.selected_world}-{self.selected_level}, lvl_array_offset: {level_array_offset}, obj_index: {object_set_index}"
        )

    def on_ok(self, _):
        object_set = self.object_set_dropdown.GetSelection()
        object_data_offset = self.object_data_spinner.GetValue()
        enemy_data_offset = self.enemy_data_spinner.GetValue()

        self.GetParent().update_level(
            self.selected_world,
            self.selected_level,
            object_data_offset,
            enemy_data_offset,
            object_set,
        )
        self.Hide()

    def on_exit(self, _):
        self.Hide()
