import wx

from Level import Level

LEVEL_LENGTHS = [0x0F + 0x10 * i for i in range(0, 2 ** 4)]
STR_LEVEL_LENGTHS = [
    f"{length:0=#4X} / {length} Blocks".replace("X", "x") for length in LEVEL_LENGTHS
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


class HeaderEditor(wx.Frame):
    def __init__(self, parent, level_view_ref):
        super(HeaderEditor, self).__init__(parent, title="Level Header Editor")

        self.level_view_ref = level_view_ref
        self.level_ref: Level = self.level_view_ref.level

        self.config_sizer = wx.FlexGridSizer(2, 0, 0)

        self.config_sizer.AddGrowableCol(0, 1)
        self.config_sizer.AddGrowableCol(1, 2)

        self.length_dropdown = wx.ComboBox(self, wx.ID_ANY, choices=STR_LEVEL_LENGTHS)
        self.music_dropdown = wx.ComboBox(self, wx.ID_ANY, choices=MUSIC_ITEMS)
        self.time_dropdown = wx.ComboBox(self, wx.ID_ANY, choices=TIMES)

        self.object_palette_spinner = wx.SpinCtrl(self, wx.ID_ANY, max=7)
        self.enemy_palette_spinner = wx.SpinCtrl(self, wx.ID_ANY, max=3)
        self.graphic_set_dropdown = wx.ComboBox(self, wx.ID_ANY, choices=GRAPHIC_SETS)

        self.level_pointer_entry = wx.TextCtrl(parent=self, style=wx.TE_RIGHT)
        self.level_pointer_entry.Disable()
        self.enemy_pointer_entry = wx.TextCtrl(parent=self, style=wx.TE_RIGHT)
        self.enemy_pointer_entry.Disable()

        self._add_label("Level Settings")
        self._add_widget("    Level length: ", self.length_dropdown)
        self._add_widget("    Music: ", self.music_dropdown)
        self._add_widget("    Time: ", self.time_dropdown)
        self._add_label("Graphical Settings")
        self._add_widget("    Object Palette: ", self.object_palette_spinner)
        self._add_widget("    Enemy Palette: ", self.enemy_palette_spinner)
        self._add_widget("    Graphic Set: ", self.graphic_set_dropdown)
        self._add_label("Next Area")
        self._add_widget("    Address of Objects: ", self.level_pointer_entry)
        self._add_widget("    Address of Enemies: ", self.enemy_pointer_entry)

        self.SetSizerAndFit(self.config_sizer)

        self._fill_widgets()

        self.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.Bind(wx.EVT_COMBOBOX, self.on_combo)
        self.Bind(wx.EVT_CLOSE, self.on_exit)

    def _add_widget(self, label, widget):
        _label = wx.StaticText(parent=self, label=label)

        self.config_sizer.Add(
            _label, border=20, flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT
        )
        self.config_sizer.Add(
            widget,
            border=3,
            flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT,
        )

    def _add_label(self, label):
        _label = wx.StaticText(parent=self, label=label)

        self.config_sizer.Add(
            _label, border=3, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT
        )
        self.config_sizer.Add(
            wx.StaticText(parent=self, label=""),
            border=3,
            flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT,
        )

    def _fill_widgets(self):
        length_index = LEVEL_LENGTHS.index(self.level_ref.width - 1)

        self.length_dropdown.SetSelection(length_index)
        self.music_dropdown.SetSelection(self.level_ref.music_index)
        self.time_dropdown.SetSelection(self.level_ref.time_index)

        self.object_palette_spinner.SetValue(self.level_ref.object_palette_index)
        self.enemy_palette_spinner.SetValue(self.level_ref.enemy_palette_index)
        self.graphic_set_dropdown.SetSelection(self.level_ref.graphic_set_index)

        self.level_pointer_entry.SetValue(hex(self.level_ref.level_pointer))
        self.enemy_pointer_entry.SetValue(hex(self.level_ref.enemy_pointer))

    def on_spin(self, event):
        spin_id = event.GetId()

        if spin_id == self.object_palette_spinner.GetId():
            new_index = self.object_palette_spinner.GetValue()
            self.level_ref.set_object_palette_index(new_index)

        elif spin_id == self.enemy_palette_spinner.GetId():
            new_index = self.enemy_palette_spinner.GetValue()
            self.level_ref.set_enemy_palette_index(new_index)

        self.level_ref.reload()
        self.level_view_ref.Refresh()

    def on_combo(self, event):
        combo_id = event.GetId()

        if combo_id == self.length_dropdown.GetId():
            new_width = LEVEL_LENGTHS[self.length_dropdown.GetSelection()]
            self.level_ref.set_width(new_width)

        elif combo_id == self.music_dropdown.GetId():
            new_music = self.music_dropdown.GetSelection()
            self.level_ref.set_music_index(new_music)

        elif combo_id == self.time_dropdown.GetId():
            new_time = self.time_dropdown.GetSelection()
            self.level_ref.set_time_index(new_time)

        elif combo_id == self.graphic_set_dropdown.GetId():
            new_gfx_set = self.graphic_set_dropdown.GetSelection()
            self.level_ref.set_gfx_index(new_gfx_set)

        self.level_ref.reload()
        self.level_view_ref.Refresh()

    def on_exit(self, _):
        self.Hide()
