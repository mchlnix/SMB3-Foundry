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



def main(path_to_rom, check_auto_save=True, m3l_path=""):
    app = QApplication()

    if check_auto_save and auto_save_rom_path.exists():
        result = AutoSaveDialog().exec()

        if result == QMessageBox.DialogCode.Accepted:
            path_to_rom = auto_save_rom_path

            QMessageBox.information(
                None, "Auto Save recovered", "Don't forget to save the loaded ROM under a new name!"
            )

    FoundryMainWindow(path_to_rom, m3l_path)
    app.exec()


if __name__ == "__main__":
    should_check_auto_save = True
    path = ""
    m3l_path = ""

    args = sys.argv[1:]

    try:
        while args:
            arg = args.pop(0)

            if arg == "--dont-check-auto-save":
                should_check_auto_save = False

            elif arg == "--load-m3l":
                if not args:
                    raise ValueError("Did not provide a file path after --load-m3l")

                m3l_path = args.pop(0)

                if not pathlib.Path(m3l_path).exists():
                    raise ValueError(f"M3L path '{m3l_path}' does not exist.")

            elif pathlib.Path(arg).exists():
                path = arg

            else:
                raise ValueError(f"Unknown command line argument '{arg}'")

        print(f"{path=}, {should_check_auto_save=}, {m3l_path=}")

        main(path, should_check_auto_save, m3l_path)

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
