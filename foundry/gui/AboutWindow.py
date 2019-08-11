import wx
import wx.adv


class AboutDialog(wx.Frame):
    def __init__(self, parent):
        super(AboutDialog, self).__init__(parent, title="About SMB3Foundry")

        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        image = wx.Image("data/foundry.ico")
        image.Rescale(200, 200)

        bitmap = wx.Bitmap(image)

        icon = wx.StaticBitmap(self, wx.ID_ANY, bitmap)

        main_sizer.Add(icon, proportion=1, border=20, flag=wx.ALL)

        info_sizer = wx.BoxSizer(wx.VERTICAL)

        info_sizer.Add(wx.StaticText(self, wx.ID_ANY, "SMB3 Foundry"))
        info_sizer.Add(
            wx.StaticLine(self, wx.ID_ANY),
            border=5,
            flag=wx.EXPAND | wx.TOP | wx.BOTTOM,
        )
        info_sizer.Add(
            wx.adv.HyperlinkCtrl(
                self,
                wx.ID_ANY,
                url="https://github.com/mchlnix/SMB3-Foundry",
                label="By Michael",
            )
        )
        info_sizer.Add(wx.StaticText(self, wx.ID_ANY, ""))
        info_sizer.Add(wx.StaticText(self, wx.ID_ANY, "With thanks to:"))
        info_sizer.Add(
            wx.adv.HyperlinkCtrl(
                self,
                wx.ID_ANY,
                url="http://hukka.ncn.fi/index.php?about",
                label="Hukka for SMB3 Workshop",
            )
        )
        info_sizer.Add(
            wx.adv.HyperlinkCtrl(
                self,
                wx.ID_ANY,
                url="https://github.com/captainsouthbird",
                label="Captain Southbird for the SMB3 Disassembly",
            )
        )
        info_sizer.Add(
            wx.adv.HyperlinkCtrl(
                self,
                wx.ID_ANY,
                url="https://www.twitch.tv/bluefinch3000",
                label="BlueFinch for testing and sanity checking",
            )
        )

        main_sizer.Add(info_sizer, proportion=1, border=20, flag=wx.ALL | wx.CENTER)

        self.SetSizerAndFit(main_sizer)
