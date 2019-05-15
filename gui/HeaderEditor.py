import wx


LEVEL_LENGTHS = [0x0F + 0x10 * i for i in range(0, 16)]
STR_LEVEL_LENGTHS = [str(length) for length in LEVEL_LENGTHS]


class HeaderEditor(wx.Frame):
    def __init__(self, parent):
        super(HeaderEditor, self).__init__(parent)

        config_sizer = wx.FlexGridSizer(cols=2, vgap=0, hgap=0)

        config_sizer.AddGrowableCol(0)

        config_sizer.Add(
            wx.StaticText(self, label="Level Length: "),
            flag=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT,
        )

        self.length_dropdown = wx.ComboBox(
            self, id=wx.ID_ANY, choices=STR_LEVEL_LENGTHS
        )

        config_sizer.Add(self.length_dropdown)

        self.SetSizer(config_sizer)
