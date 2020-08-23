#!/usr/bin/env python3
import os
import sys

from PySide2.QtWidgets import QApplication

# change into the tmp directory pyinstaller uses for the data
from foundry.core.Settings.util import load_settings, save_settings

if hasattr(sys, "_MEIPASS"):
    print(f"Changing current dir to {getattr(sys, '_MEIPASS')}")
    os.chdir(getattr(sys, "_MEIPASS"))

from foundry.gui.MainWindow import MainWindow


def main(path_to_rom):
    load_settings()

    app = QApplication()
    MainWindow(path_to_rom)
    app.exec_()

    save_settings()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = ""

    main(path)
