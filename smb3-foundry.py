#!/usr/bin/env python3
import logging
import os
import pathlib
import sys
import traceback
import warnings

from PySide6.QtWidgets import QApplication, QMessageBox

from foundry import auto_save_rom_path, github_issue_link
from foundry.gui.dialogs.AutoSaveDialog import AutoSaveDialog

# compatibility for dark mode
warnings.warning = warnings.warn

logger = logging.getLogger(__name__)

# change into the tmp directory pyinstaller uses for the data
if hasattr(sys, "_MEIPASS"):
    logger.info(f"Changing current dir to {getattr(sys, '_MEIPASS')}")
    os.chdir(getattr(sys, "_MEIPASS"))

from foundry.gui.FoundryMainWindow import FoundryMainWindow  # noqa


def main(path_to_rom, check_auto_save=True):
    app = QApplication()

    if check_auto_save and auto_save_rom_path.exists():
        result = AutoSaveDialog().exec()

        if result == QMessageBox.DialogCode.Accepted:
            path_to_rom = auto_save_rom_path

            QMessageBox.information(
                None, "Auto Save recovered", "Don't forget to save the loaded ROM under a new name!"
            )

    FoundryMainWindow(path_to_rom)
    app.exec()


if __name__ == "__main__":
    should_check_auto_save = True
    path = ""

    for arg in sys.argv[1:]:
        if "--dont-check-auto-save" in arg:
            should_check_auto_save = False
            continue

        if pathlib.Path(arg).exists():
            path = arg

    try:
        main(path, should_check_auto_save)
    except Exception as e:
        app = QApplication()

        box = QMessageBox()
        box.setWindowTitle("Crash report")
        box.setText(
            f"An unexpected error occurred! Please contact the developers at {github_issue_link} "
            f"with the error below:\n\n{e}\n\n{traceback.format_exc()}"
        )
        box.exec()

        app.exec()
        raise
