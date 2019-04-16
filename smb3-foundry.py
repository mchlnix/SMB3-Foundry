import wx
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "gui"))

from MainWindow import SMB3Foundry


def main():
    app = wx.App()
    ex = SMB3Foundry(None)
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
