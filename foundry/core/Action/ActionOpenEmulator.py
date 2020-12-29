

import tempfile
import pathlib
import shlex
import subprocess

from PySide2.QtWidgets import QWidget, QMessageBox

from foundry.game.File import ROM

from foundry.core.Settings.util import get_setting
from foundry.core.Observables.ObservableDecorator import ObservableDecorator
from foundry.core.Action.Action import Action


class ActionOpenEmulator(Action):
    """Saves the rom to the first level"""
    def __init__(self, name: str, parent: QWidget, action: Action):
        self.name = name
        self.open_action = action
        self.observer = ObservableDecorator(self._save_to_first_level)
        self.parent = parent

    def _save_to_first_level(self):
        """Does the action of saving to the first level"""
        result = _on_play(self.parent, self.open_action)
        return result


def _on_play(parent: QWidget, action: Action):
    """
    Copies the ROM, including the current level, to a temporary directory, saves the current level as level 1-1 and
    opens the rom in an emulator.
    """
    temp_dir = pathlib.Path(tempfile.gettempdir()) / "smb3foundry"
    temp_dir.mkdir(parents=True, exist_ok=True)

    path_to_temp_rom = temp_dir / "instaplay.rom"

    ROM().save_to(path_to_temp_rom)

    if not action(path_to_temp_rom):
        return False

    arg = str(get_setting("instaplay_arguments", ""))
    if not arg:
        arguments = str(path_to_temp_rom)
    else:
        arguments = str(get_setting("instaplay_arguments", "")).replace("%f", str(path_to_temp_rom))
    arguments = shlex.split(arguments, posix=False)

    emu_path = pathlib.Path(str(get_setting("instaplay_emulator", "")))

    if emu_path.is_absolute():
        if emu_path.exists():
            emulator = str(emu_path)
        else:
            QMessageBox.critical(
                parent, "Emulator not found", f"Check it under File > Settings.\nFile {emu_path} not found."
            )
            return False
    else:
        emulator = get_setting("instaplay_emulator", "")

    try:
        subprocess.run([emulator, *arguments])
    except Exception as e:
        QMessageBox.critical(parent, "Emulator command failed.", f"Check it under File > Settings.\n{str(e)}")

    return True
