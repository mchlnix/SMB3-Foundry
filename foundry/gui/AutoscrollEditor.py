import wx

from game.gfx.objects.EnemyItem import EnemyObject

WATER_LINE_MODE_IDENTIFIER = 0x60


class AutoscrollEditor(wx.Frame):
    def __init__(self, parent, autoscroll_object):
        super(AutoscrollEditor, self).__init__(parent)

        self.SetTitle("Autoscroll Editor")

        self._autoscroll_object: EnemyObject = autoscroll_object

        if self._autoscroll_object.x_position == WATER_LINE_MODE_IDENTIFIER:
            # used in 3-2 to draw the water texture on the bottom it seems like
            # only seems to work with horizontal scrolling
            self._waterline_mode = True

        self.config_sizer = wx.FlexGridSizer(2, 0, 0)

        self.config_sizer.AddGrowableCol(0, 1)
        self.config_sizer.AddGrowableCol(1, 2)

        self.Y = self._autoscroll_object.x_position & 0b0000_1111
        self.Level_AScrlSelect = self._autoscroll_object.x_position >> 4

        if self.Level_AScrlSelect < 3:
            if self.Level_AScrlSelect == 1:
                self.Y |= 0x10

        ok_button = wx.Button(parent=self, id=wx.ID_OK)
        cancel_button = wx.Button(parent=self, id=wx.ID_CANCEL)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(ok_button)
        button_sizer.Add(cancel_button)

        self._add_widget("", button_sizer)

        self.SetSizerAndFit(self.config_sizer)

        self.Bind(wx.EVT_BUTTON, self.on_button)

        self._set_widget_values()

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

    def _set_widget_values(self):
        pass

    def on_button(self, event):
        if event.GetId() == wx.ID_OK:
            pass

            self.Close()
        elif event.GetId() == wx.ID_CANCEL:
            self.Close()
