#!/usr/bin/env python3
import os
import sys

import wx

# change into the tmp directory pyinstaller uses for the data
if hasattr(sys, "_MEIPASS"):
    print(f"Changing current dir to {getattr(sys, '_MEIPASS')}")
    os.chdir(getattr(sys, "_MEIPASS"))

from foundry.gui.MainWindow import SMB3Foundry


def main():
    app = wx.App()
    ex = SMB3Foundry(None)
    ex.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
