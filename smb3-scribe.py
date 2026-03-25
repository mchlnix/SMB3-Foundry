#!/usr/bin/env python3
import logging
import os
import sys
import traceback

from PySide6.QtWidgets import QApplication

from foundry import is_pyinstalled
from foundry.gui.dialogs.crash_dialog import popup_crash_dialog
from scribe.gui.main_window import ScribeMainWindow

logger = logging.getLogger(__name__)

# change into the tmp directory pyinstaller uses for the data
if is_pyinstalled():
    logger.info(f"Changing current dir to {getattr(sys, '_MEIPASS')}")
    os.chdir(getattr(sys, "_MEIPASS"))

app = None


def main(path_to_rom):
    global app

    app = QApplication()

    window = ScribeMainWindow(path_to_rom)  # noqa
    app.exec()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = ""

    try:
        main(path)
    except Exception:
        if app is None:
            app = QApplication()

        popup_crash_dialog(traceback.format_exc())

        raise
