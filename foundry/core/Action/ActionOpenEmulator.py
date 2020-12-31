

import tempfile
import pathlib
import shlex
import subprocess

from PySide2.QtWidgets import QWidget, QMessageBox

from foundry.game.File import ROM

from foundry.core.Settings.util import get_setting
from foundry.core.Observables.ObservableDecorator import ObservableDecorator
from foundry.core.Action.Action import Action

from smb3parse.constants import Title_DebugMenu, Title_PrepForWorldMap
from foundry.gui.SettingsDialog import PowerUp, POWERUPS


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
    if not _set_default_powerup(path_to_temp_rom):
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


def _set_default_powerup(path_to_rom) -> bool:
    from smb3parse.util.rom import Rom as SMB3Rom
    with open(path_to_rom, "rb") as smb3_rom:
        data = smb3_rom.read()

    rom = SMB3Rom(bytearray(data))

    powerup: PowerUp = POWERUPS[get_setting("default_powerup", 0)]
    index: int = powerup.index
    pwing: bool = powerup.pwing_enable

    rom.write(Title_PrepForWorldMap + 0x1, bytes([index]))

    nop = 0xEA
    rts = 0x60
    lda = 0xA9
    staAbsolute = 0x8D

    # If a P-wing powerup is selected, another variable needs to be set with the P-wing value
    # This piece of code overwrites a part of Title_DebugMenu
    if pwing:
        Map_Power_DispHigh = 0x03
        Map_Power_DispLow = 0xF3

        # We need to start one byte before Title_DebugMenu to remove the RTS of Title_PrepForWorldMap
        # The assembly code below reads as follows:
        # LDA 0x08
        # STA $03F3
        # RTS
        rom.write(
            Title_DebugMenu - 0x1,
            bytes(
                [
                    lda,
                    0x8,
                    staAbsolute,
                    Map_Power_DispLow,
                    Map_Power_DispHigh,
                    # The RTS to get out of the now extended Title_PrepForWorldMap
                    rts,
                ]
            ),
        )

        # Remove code that resets the powerup value by replacing it with no-operations
        # Otherwise this code would copy the value of the normal powerup here
        # (So if the powerup would be Raccoon Mario, Map_Power_Disp would also be
        # set as Raccoon Mario instead of P-wing
        Map_Power_DispResetLocation = 0x3C5A2
        rom.write(Map_Power_DispResetLocation, bytes([nop, nop, nop]))

    rom.save_to(path_to_rom)
    return True