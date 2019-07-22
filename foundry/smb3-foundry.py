#!/usr/bin/env python3
import wx

from gui.MainWindow import SMB3Foundry


def main():
    app = wx.App()
    ex = SMB3Foundry(None)
    ex.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
