import wx

from MainWindow import SMB3Foundry


def main():
    app = wx.App()
    ex = SMB3Foundry(None)
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
