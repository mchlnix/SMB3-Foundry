#!/usr/bin/env python3
import logging
import os
import sys

from PySide6.QtWidgets import QApplication

from scribe.gui.main_window import ScribeMainWindow

logger = logging.getLogger(__name__)

# change into the tmp directory pyinstaller uses for the data
if hasattr(sys, "_MEIPASS"):
    logger.info(f"Changing current dir to {getattr(sys, '_MEIPASS')}")
    os.chdir(getattr(sys, "_MEIPASS"))


def main(path_to_rom):
    app = QApplication()

    window = ScribeMainWindow(path_to_rom)  # noqa
    app.exec()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = ""

    main(path)
