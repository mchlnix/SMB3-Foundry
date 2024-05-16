#!/usr/bin/env python3
import logging
import os
import pathlib
import sys
import traceback
import warnings

from PySide6.QtWidgets import QApplication, QMessageBox

from foundry import auto_save_rom_path, github_issue_link
from foundry.game.File import ROM
from foundry.gui.dialogs.AutoSaveDialog import AutoSaveDialog

LOAD_LEVEL = "--load-level"

LOAD_M3L = "--load-m3l"

CHECK_AUTO_SAVE = "--dont-check-auto-save"

# compatibility for dark mode
warnings.warning = warnings.warn

logger = logging.getLogger(__name__)

# change into the tmp directory pyinstaller uses for the data
if hasattr(sys, "_MEIPASS"):
    logger.info(f"Changing current dir to {getattr(sys, '_MEIPASS')}")
    os.chdir(getattr(sys, "_MEIPASS"))

from foundry.gui.FoundryMainWindow import FoundryMainWindow  # noqa

app = None


def main(path_to_rom, check_auto_save=True, level_data_tuple=(), m3l_path=""):
    global app
    app = QApplication()

    if check_auto_save and auto_save_rom_path.exists():
        result = AutoSaveDialog().exec()

        if result == QMessageBox.DialogCode.Accepted:
            path_to_rom = auto_save_rom_path

            QMessageBox.information(
                None, "Auto Save recovered", "Don't forget to save the loaded ROM under a new name!"
            )

    main_window = FoundryMainWindow(path_to_rom, m3l_path)

    main_window.on_open_rom(path_to_rom)

    if ROM.is_loaded():
        if m3l_path:
            main_window.load_m3l(m3l_path)

        elif level_data_tuple:
            main_window.update_level("", *level_data_tuple)

        elif not main_window.open_level_selector(None):
            main_window.on_new_level(dont_check=True)

    main_window.enable_disable_gui_elements()

    app.exec()


if __name__ == "__main__":
    should_check_auto_save = True
    path = ""
    m3l_path = ""
    level_data_tuple = tuple()

    args = sys.argv[1:]

    try:
        while args:
            arg = args.pop(0)

            if arg == CHECK_AUTO_SAVE:
                should_check_auto_save = False

            elif arg == LOAD_M3L:
                if not args:
                    raise ValueError("Did not provide a file path after --load-m3l")

                m3l_path = args.pop(0)

                if not pathlib.Path(m3l_path).exists():
                    raise ValueError(f"M3L path '{m3l_path}' does not exist.")

            elif arg == LOAD_LEVEL:
                if len(args) < 3:
                    raise ValueError("Needs level address, enemy address and object set number to load a level.")

                try:
                    level_address = int(args.pop(0), 16)
                    enemy_address = int(args.pop(0), 16)
                    object_set_number = int(args.pop(0), 16)
                except ValueError:
                    raise ValueError("Level address, enemy address and object set number must be hex integers.")

                level_data_tuple = (level_address, enemy_address, object_set_number)

            elif pathlib.Path(arg).exists():
                path = arg

            else:
                raise ValueError(f"Unknown command line argument '{arg}'")

        print(f"{path=}, {should_check_auto_save=}, {m3l_path=}")

        main(path, should_check_auto_save, level_data_tuple, m3l_path)

    except Exception as e:
        if app is None:
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
