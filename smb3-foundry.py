#!/usr/bin/env python3
import logging
import os
import sys
import traceback
import warnings
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox

from foundry import auto_save_rom_path, is_pyinstalled
from foundry.game.File import ROM
from foundry.gui.dialogs.AutoSaveDialog import AutoSaveDialog
from foundry.gui.dialogs.crash_dialog import popup_crash_dialog
from smb3parse.levels import WORLD_COUNT
from smb3parse.util import clamp

LOAD_LEVEL = "--load-level"

LOAD_M3L = "--load-m3l"

SKIP_AUTO_SAVE = "--dont-check-auto-save"

# compatibility for dark mode
warnings.warning = warnings.warn  # type: ignore

logger = logging.getLogger(__name__)


# change into the tmp directory pyinstaller uses for the data
if is_pyinstalled():
    logger.info(f"Changing current dir to {getattr(sys, '_MEIPASS')}")
    os.chdir(getattr(sys, "_MEIPASS"))

from foundry.gui.FoundryMainWindow import FoundryMainWindow  # noqa

app = None


def main(
    path_to_rom: Path,
    check_auto_save=True,
    level_data_tuple_=(0, 0, 0, 0),
    m3l_path_="",
):
    global app
    app = QApplication()

    main_window = FoundryMainWindow()

    have_level_data = m3l_path or level_data_tuple_ and 0 not in level_data_tuple_

    if check_auto_save and main_window.settings.value("editor/auto_save_enabled") and auto_save_rom_path.exists():
        result = AutoSaveDialog().exec()

        if result == QMessageBox.DialogCode.Accepted:
            path_to_rom = auto_save_rom_path
            have_level_data = True

            QMessageBox.information(
                None,
                "Auto Save recovered",
                "Don't forget to save the loaded ROM under a new name!",
            )

    if not have_level_data and main_window.settings.value("editor/remember_last_level"):
        last_rom = Path(main_window.settings.value("editor/remember_last_level_path"))
        object_set = main_window.settings.value("editor/remember_last_level_object_set")
        level_address_ = main_window.settings.value("editor/remember_last_level_lvl_address")
        enemy_address_ = main_window.settings.value("editor/remember_last_level_enemy_address")
        world_number = main_window.settings.value("editor/remember_last_level_world_number")
        world_number = clamp(1, world_number, WORLD_COUNT - 1)

        if last_rom.is_file() and 0 not in (level_address_, enemy_address_, object_set):
            path_to_rom = last_rom
            level_data_tuple_ = (
                level_address_,
                enemy_address_,
                object_set,
                world_number,
            )

            have_level_data = True

    main_window.on_open_rom(path_to_rom, try_opening_level=not have_level_data)

    if ROM.is_loaded():
        if m3l_path_:
            main_window.load_m3l(m3l_path_)

        elif level_data_tuple_:
            main_window.update_level("", *level_data_tuple_)

    main_window.enable_disable_gui_elements()

    app.exec()


if __name__ == "__main__":
    should_check_auto_save = True
    path = Path()
    m3l_path = ""
    level_data_tuple: tuple[int, int, int, int] = (0, 0, 0, 0)

    args = sys.argv[1:]

    try:
        while args:
            arg = args.pop(0)

            if arg == SKIP_AUTO_SAVE:
                should_check_auto_save = False

            elif arg == LOAD_M3L:
                if not args:
                    raise ValueError("Did not provide a file path after --load-m3l")

                m3l_path = args.pop(0)

                if not Path(m3l_path).exists():
                    raise ValueError(f"M3L path '{m3l_path}' does not exist.")

            elif arg == LOAD_LEVEL:
                if len(args) < 3:
                    raise ValueError("Needs level address, enemy address and object set number to load a level.")

                try:
                    level_address = int(args.pop(0), 16)
                    enemy_address = int(args.pop(0), 16)
                    object_set_number = int(args.pop(0), 16)
                    # add proper command line support for worlds
                    world_number = 1
                except ValueError:
                    raise ValueError("Level address, enemy address and object set number must be hex integers.")

                level_data_tuple = (level_address, enemy_address, object_set_number)

            elif Path(arg).exists():
                path = Path(arg)

            else:
                raise ValueError(f"Unknown command line argument '{arg}'")

        print(f"{path=}, {should_check_auto_save=}, {m3l_path=}")

        main(path, should_check_auto_save, level_data_tuple, m3l_path)

    except Exception:
        if app is None:
            app = QApplication()

        popup_crash_dialog(traceback.format_exc())

        raise
