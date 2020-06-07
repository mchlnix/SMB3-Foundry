#!/usr/bin/env python3
import os
import sys
import traceback
import logging

from foundry import github_issue_link

logger = logging.getLogger(__name__)

from PySide2.QtWidgets import QApplication, QMessageBox

# change into the tmp directory pyinstaller uses for the data
from foundry.gui.settings import load_settings, save_settings

if hasattr(sys, "_MEIPASS"):
    logger.info(f"Changing current dir to {getattr(sys, '_MEIPASS')}")
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

    try:
        main(path)
    except Exception as e:
        box = QMessageBox()
        box.setWindowTitle("Crash report")
        box.setText(
            f"An unexpected error occurred! Please contact the developers at {github_issue_link} "
            f"with the error below:\n\n{str(e)}\n\n{traceback.format_exc()}"
        )
        box.exec_()
        raise
