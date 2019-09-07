import wx

from foundry.game.gfx.objects.Jump import Jump
from foundry.gui.Events import JumpUpdate

JUMP_ACTIONS = [
    "Downward Pipe 1",
    "Upward Pipe",
    "Downward Pipe 2",
    "Right Pipe",
    "Left Pipe",
    "?",
    "?",
    "Jump on Noteblock",
    "Door",
    "?",
    "?",
    "?",
    "?",
    "?",
    "?",
    "?",
]

VERT_POSITIONS = [
    "00",
    "05",
    "08",
    "12",
    "16",
    "20",
    "23",
    "24",
    "00 (Vertical)",
    "05 (Vertical)",
    "08 (Vertical)",
    "12 (Vertical)",
    "16 (Vertical)",
    "20 (Vertical)",
    "23 (Vertical)",
    "24 (Vertical)",
]

MAX_SCREEN_INDEX = 0x0F
MAX_HORIZ_POSITION = 0xFF


class JumpEditor(wx.Frame):
    def __init__(self, parent: wx.Window, jump: Jump, index: int):
        super(JumpEditor, self).__init__(
            parent, style=wx.FRAME_FLOAT_ON_PARENT | wx.DEFAULT_FRAME_STYLE
        )

        self.SetTitle("Jump Editor")

        self._jump = jump
        self._jump_index = index

        self.config_sizer = wx.FlexGridSizer(2, 0, 0)

        self.config_sizer.AddGrowableCol(0, 1)
        self.config_sizer.AddGrowableCol(1, 2)

        self._add_label("Level position:")

        self.screen_spinner = wx.SpinCtrl(parent=self, max=MAX_SCREEN_INDEX)
        self._add_widget("Jump on screen: ", self.screen_spinner)

        self._add_label("Exit options:")

        self.exit_action = wx.ComboBox(parent=self, choices=JUMP_ACTIONS)
        self._add_widget("Exit action:", self.exit_action)

        self.exit_horizontal = wx.SpinCtrl(parent=self, max=MAX_HORIZ_POSITION)
        self._add_widget("Exit position x:", self.exit_horizontal)

        self.exit_vertical = wx.ComboBox(parent=self, choices=VERT_POSITIONS)
        self._add_widget("Exit position y:", self.exit_vertical)

        ok_button = wx.Button(parent=self, id=wx.ID_OK)
        cancel_button = wx.Button(parent=self, id=wx.ID_CANCEL)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(ok_button)
        button_sizer.Add(cancel_button)

        self._add_widget("", button_sizer)

        self.SetSizerAndFit(self.config_sizer)

        self.Bind(wx.EVT_BUTTON, self.on_button)

        self._set_widget_values()

    def _add_widget(self, label: str, widget: wx.Object):
        _label = wx.StaticText(parent=self, label=label)

        self.config_sizer.Add(
            _label, border=20, flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT
        )
        self.config_sizer.Add(
            widget,
            border=3,
            flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT,
        )

    def _add_label(self, label: str):
        _label = wx.StaticText(parent=self, label=label)

        self.config_sizer.Add(
            _label, border=3, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT
        )
        self.config_sizer.Add(
            wx.StaticText(parent=self, label=""),
            border=3,
            flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT,
        )

    def _set_widget_values(self):
        self.screen_spinner.SetValue(self._jump.screen_index)

        self.exit_action.SetSelection(self._jump.exit_action)
        self.exit_horizontal.SetValue(self._jump.exit_horizontal)
        self.exit_vertical.SetSelection(self._jump.exit_vertical)

    def on_button(self, event):
        if event.GetId() == wx.ID_OK:
            jump = Jump.from_properties(
                self.screen_spinner.GetValue(),
                self.exit_action.GetSelection(),
                self.exit_horizontal.GetValue(),
                self.exit_vertical.GetSelection(),
            )

            evt = JumpUpdate(id=wx.ID_ANY, jump=jump, index=self._jump_index)

            wx.PostEvent(self, evt)

            self.Close()
        elif event.GetId() == wx.ID_CANCEL:
            self.Close()
