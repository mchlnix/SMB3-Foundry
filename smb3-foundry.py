#!/usr/bin/env python3
import logging
import os
import sys
import traceback

from PySide2.QtWidgets import QApplication, QMessageBox

from foundry import auto_save_rom_path, github_issue_link
from foundry.gui.AutoSaveDialog import AutoSaveDialog
from foundry.gui.settings import load_settings, save_settings

logger = logging.getLogger(__name__)

# change into the tmp directory pyinstaller uses for the data
if hasattr(sys, "_MEIPASS"):
    logger.info(f"Changing current dir to {getattr(sys, '_MEIPASS')}")
    os.chdir(getattr(sys, "_MEIPASS"))

from foundry.gui.MainWindow import MainWindow


def main(path_to_rom):
    load_settings()

    app = QApplication()

    if auto_save_rom_path.exists():
        result = AutoSaveDialog().exec_()

        if result == QMessageBox.AcceptRole:
            path_to_rom = auto_save_rom_path

            QMessageBox.information(
                None, "Auto Save recovered", "Don't forget to save the loaded ROM under a new name!"
            )

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
