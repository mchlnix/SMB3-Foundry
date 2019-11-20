import wx
import wx.lib.newevent

from foundry.gui.LevelSelector import OBJECT_SET_ITEMS
from foundry.gui.LevelView import LevelView

LEVEL_LENGTHS = [0x0F + 0x10 * i for i in range(0, 2 ** 4)]
STR_LEVEL_LENGTHS = [f"{length:0=#4X} / {length} Blocks".replace("X", "x") for length in LEVEL_LENGTHS]

# todo check if correct order
X_POSITIONS = [0x01, 0x07, 0x08, 0x0D]
STR_X_POSITIONS = [f"{position:0=#4X} / {position}. Block".replace("X", "x") for position in X_POSITIONS]

# todo check if correct order
Y_POSITIONS = [0x01, 0x05, 0x08, 0x0C, 0x10, 0x14, 0x17, 0x18]
STR_Y_POSITIONS = [f"{position:0=#4X} / {position}. Block".replace("X", "x") for position in Y_POSITIONS]

ACTIONS = [
    "None",
    "Sliding",
    "Out of pipe ↑",
    "Out of pipe ↓",
    "Out of pipe ←",
    "Out of pipe →",
    "Running and climbing up ship",
    "Ship auto scrolling",
]

MUSIC_ITEMS = [
    "Plain level",
    "Underground",
    "Water level",
    "Fortress",
    "Boss",
    "Ship",
    "Battle",
    "P-Switch/Mushroom house (1)",
    "Hilly level",
    "Castle room",
    "Clouds/Sky",
    "P-Switch/Mushroom house (2)",
    "No music",
    "P-Switch/Mushroom house (1)",
    "No music",
    "World 7 map",
]

GRAPHIC_SETS = [
    "Mario graphics (1)",
    "Plain",
    "Fortress",
    "Underground (1)",
    "Sky",
    "Pipe/Water (1, Piranha Plant)",
    "Pipe/Water (2, Water)",
    "Mushroom house (1)",
    "Pipe/Water (3, Pipe)",
    "Desert",
    "Ship",
    "Giant",
    "Ice",
    "Clouds",
    "Underground (2)",
    "Spade bonus room",
    "Spade bonus",
    "Mushroom house (2)",
    "Pipe/Water (4)",
    "Hills",
    "Plain 2",
    "Tank",
    "Castle",
    "Mario graphics (2)",
    "Animated graphics (1)",
    "Animated graphics (2)",
    "Animated graphics (3)",
    "Animated graphics (4)",
    "Animated graphics (P-Switch)",
    "Game font/Course Clear graphics",
    "Animated graphics (5)",
    "Animated graphics (6)",
]

TIMES = ["300", "400", "200", "Unlimited"]

SCROLL_DIRECTIONS = [
    "Locked, unless climbing/flying",
    "Free vertical scrolling",
    "Locked 'by start coordinates'?",
    "Shouldn't appear in game, do not use.",
]


HeaderChangedEvent, EVT_HEADER_CHANGED = wx.lib.newevent.NewCommandEvent()
ID_HEADER_EDITOR = wx.NewId()

SPINNER_MAX_VALUE = 0x0F_FF_FF


class HeaderEditor(wx.Frame):
    def __init__(self, parent: wx.Window, level_view_ref: LevelView):
        super(HeaderEditor, self).__init__(
            parent, title="Level Header Editor", style=wx.FRAME_FLOAT_ON_PARENT | wx.DEFAULT_FRAME_STYLE
        )

        self.level_view_ref: LevelView = level_view_ref
        self.level_ref = self.level_view_ref.level

        self.SetId(ID_HEADER_EDITOR)

        self.config_sizer = wx.FlexGridSizer(2, 0, 0)

        self.config_sizer.AddGrowableCol(0, 1)
        self.config_sizer.AddGrowableCol(1, 2)

        self.length_dropdown = wx.ComboBox(self, wx.ID_ANY, choices=STR_LEVEL_LENGTHS)
        self.music_dropdown = wx.ComboBox(self, wx.ID_ANY, choices=MUSIC_ITEMS)
        self.time_dropdown = wx.ComboBox(self, wx.ID_ANY, choices=TIMES)
        self.v_scroll_direction_dropdown = wx.ComboBox(self, wx.ID_ANY, choices=SCROLL_DIRECTIONS)
        self.level_is_vertical_cb = wx.CheckBox(self)
        self.pipe_ends_level_cb = wx.CheckBox(self)

        self.x_position_dropdown = wx.ComboBox(self, wx.ID_ANY, choices=STR_X_POSITIONS)
        self.y_position_dropdown = wx.ComboBox(self, wx.ID_ANY, choices=STR_Y_POSITIONS)
        self.action_dropdown = wx.ComboBox(self, wx.ID_ANY, choices=ACTIONS)

        self.object_palette_spinner = wx.SpinCtrl(self, wx.ID_ANY, max=7)
        self.enemy_palette_spinner = wx.SpinCtrl(self, wx.ID_ANY, max=3)
        self.graphic_set_dropdown = wx.ComboBox(self, wx.ID_ANY, choices=GRAPHIC_SETS)

        self.level_pointer_spinner = wx.SpinCtrl(self, min=0, max=SPINNER_MAX_VALUE)
        self.level_pointer_spinner.SetBase(16)
        self.enemy_pointer_spinner = wx.SpinCtrl(self, min=0, max=SPINNER_MAX_VALUE)
        self.enemy_pointer_spinner.SetBase(16)
        self.next_area_object_set_dropdown = wx.ComboBox(self, wx.ID_ANY, choices=OBJECT_SET_ITEMS)

        self._add_label("Level Settings")
        self._add_widget("    Level length: ", self.length_dropdown)
        self._add_widget("    Music: ", self.music_dropdown)
        self._add_widget("    Time: ", self.time_dropdown)
        self._add_widget("    Scroll direction: ", self.v_scroll_direction_dropdown)
        self._add_widget("    Is Vertical: ", self.level_is_vertical_cb)
        self._add_widget("    Pipe ends level: ", self.pipe_ends_level_cb)
        self._add_label("Player Settings")
        self._add_widget("    Starting X: ", self.x_position_dropdown)
        self._add_widget("    Starting Y: ", self.y_position_dropdown)
        self._add_widget("    Action: ", self.action_dropdown)
        self._add_label("Graphical Settings")
        self._add_widget("    Object Palette: ", self.object_palette_spinner)
        self._add_widget("    Enemy Palette: ", self.enemy_palette_spinner)
        self._add_widget("    Graphic Set: ", self.graphic_set_dropdown)
        self._add_label("Next Area")
        self._add_widget("    Address of Objects: ", self.level_pointer_spinner)
        self._add_widget("    Address of Enemies: ", self.enemy_pointer_spinner)
        self._add_widget("    Object Set: ", self.next_area_object_set_dropdown)

        self.SetSizerAndFit(self.config_sizer)

        self._fill_widgets()

        self.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.Bind(wx.EVT_COMBOBOX, self.on_combo)
        self.Bind(wx.EVT_CHECKBOX, self.on_check_box)
        self.Bind(wx.EVT_CLOSE, self.on_exit)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_press)

    def _add_widget(self, label: str, widget: wx.Control):
        _label = wx.StaticText(parent=self, label=label)

        self.config_sizer.Add(_label, border=20, flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT)
        self.config_sizer.Add(widget, border=3, flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT)

    def _add_label(self, label: str):
        _label = wx.StaticText(parent=self, label=label)

        self.config_sizer.Add(_label, border=3, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT)
        self.config_sizer.Add(
            wx.StaticText(parent=self, label=""),
            border=3,
            flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT,
        )

    def _fill_widgets(self):
        length_index = LEVEL_LENGTHS.index(self.level_ref.length - 1)

        self.length_dropdown.SetSelection(length_index)
        self.music_dropdown.SetSelection(self.level_ref.music_index)
        self.time_dropdown.SetSelection(self.level_ref.time_index)
        self.v_scroll_direction_dropdown.SetSelection(self.level_ref.scroll_type)
        self.level_is_vertical_cb.SetValue(self.level_ref.is_vertical)
        self.pipe_ends_level_cb.SetValue(self.level_ref.pipe_ends_level)

        self.x_position_dropdown.SetSelection(self.level_ref.start_x_index)
        self.y_position_dropdown.SetSelection(self.level_ref.start_y_index)
        self.action_dropdown.SetSelection(self.level_ref.start_action)

        self.object_palette_spinner.SetValue(self.level_ref.object_palette_index)
        self.enemy_palette_spinner.SetValue(self.level_ref.enemy_palette_index)
        self.graphic_set_dropdown.SetSelection(self.level_ref.graphic_set)

        self.level_pointer_spinner.SetValue(self.level_ref.next_area_objects)
        self.enemy_pointer_spinner.SetValue(self.level_ref.next_area_enemies)
        self.next_area_object_set_dropdown.SetSelection(self.level_ref.next_area_object_set)

    def reload_level(self):
        self.level_ref = self.level_view_ref.level

        self._fill_widgets()

    def on_spin(self, event: wx.SpinEvent):
        if self.level_ref is None:
            return

        spin_id = event.GetId()

        if spin_id == self.object_palette_spinner.GetId():
            new_index = self.object_palette_spinner.GetValue()
            self.level_ref.object_palette_index = new_index

        elif spin_id == self.enemy_palette_spinner.GetId():
            new_index = self.enemy_palette_spinner.GetValue()
            self.level_ref.enemy_palette_index = new_index

        elif spin_id == self.level_pointer_spinner.GetId():
            new_offset = self.level_pointer_spinner.GetValue()
            self.level_ref.next_area_objects = new_offset

        elif spin_id == self.enemy_pointer_spinner:
            new_offset = self.enemy_pointer_spinner.GetValue()
            self.level_ref.next_area_enemies = new_offset

        wx.PostEvent(self, HeaderChangedEvent(self.GetId()))

        self.level_ref.reload()
        self.level_view_ref.update_size()
        self.level_view_ref.Refresh()

    def on_combo(self, event):
        combo_id = event.GetId()

        if combo_id == self.length_dropdown.GetId():
            new_length = LEVEL_LENGTHS[self.length_dropdown.GetSelection()]
            self.level_ref.length = new_length

        elif combo_id == self.music_dropdown.GetId():
            new_music = self.music_dropdown.GetSelection()
            self.level_ref.music_index = new_music

        elif combo_id == self.time_dropdown.GetId():
            new_time = self.time_dropdown.GetSelection()
            self.level_ref.time_index = new_time

        elif combo_id == self.x_position_dropdown.GetId():
            new_x = self.x_position_dropdown.GetSelection()
            self.level_ref.start_x_index = new_x

        elif combo_id == self.v_scroll_direction_dropdown.GetId():
            new_scroll = self.v_scroll_direction_dropdown.GetSelection()
            self.level_ref.scroll_type = new_scroll

        elif combo_id == self.y_position_dropdown.GetId():
            new_y = self.y_position_dropdown.GetSelection()
            self.level_ref.start_y_index = new_y

        elif combo_id == self.action_dropdown.GetId():
            new_action = self.action_dropdown.GetSelection()
            self.level_ref.start_action = new_action

        elif combo_id == self.graphic_set_dropdown.GetId():
            new_gfx_set = self.graphic_set_dropdown.GetSelection()
            self.level_ref.graphic_set = new_gfx_set

        elif combo_id == self.next_area_object_set_dropdown.GetId():
            new_object_set = self.next_area_object_set_dropdown.GetSelection()
            self.level_ref.next_area_object_set = new_object_set

        wx.PostEvent(self, HeaderChangedEvent(self.GetId()))

        self.level_ref.reload()
        self.level_view_ref.update_size()
        self.level_view_ref.Refresh()

    def on_check_box(self, event):
        cb_id = event.GetId()

        if cb_id == self.pipe_ends_level_cb.GetId():
            self.level_ref.pipe_ends_level = self.pipe_ends_level_cb.GetValue()
        elif cb_id == self.level_is_vertical_cb.GetId():
            self.level_ref.is_vertical = self.level_is_vertical_cb.GetValue()

        wx.PostEvent(self, HeaderChangedEvent(self.GetId()))

        self.level_ref.reload()
        self.level_view_ref.update_size()
        self.level_view_ref.Refresh()

    def refresh(self):
        self._fill_widgets()

    def Show(self, **kwargs):
        self._fill_widgets()
        super(HeaderEditor, self).Show(**kwargs)

    def on_key_press(self, event):
        key = event.GetKeyCode()

        if key == wx.WXK_ESCAPE:
            self.on_exit(None)

    def on_exit(self, _):
        self.Hide()
