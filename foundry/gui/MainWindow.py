import shlex
import subprocess
from pathlib import Path

from PySide6.QtGui import QCloseEvent, QUndoStack
from PySide6.QtWidgets import QMainWindow, QMessageBox

from foundry import Settings, check_for_update
from foundry.game.File import ROM
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.util import center_widget


class MainWindow(QMainWindow):
    undo_stack: QUndoStack
    settings: Settings

    def __init__(self):
        super(MainWindow, self).__init__()

        center_widget(self)

        self.level_ref = LevelRef()

    def check_for_update_on_startup(self):
        if not self.settings.value("editor/asked_for_startup"):
            answer = QMessageBox.question(
                self, "Automatic Update Checks", "Do you want the editor to automatically check for updates on startup?"
            )

            self.settings.setValue("editor/asked_for_startup", True)
            self.settings.setValue("editor/update_on_startup", answer == QMessageBox.Yes)

        if self.settings.value("editor/update_on_startup"):
            check_for_update(self, only_for_named_version=True)

    def safe_to_change(self) -> bool:
        return self.undo_stack.isClean() or self.confirm_changes()

    def confirm_changes(self):
        answer = QMessageBox.question(
            self,
            "Please confirm",
            "Current content has not been saved! Proceed?",
            QMessageBox.No | QMessageBox.Yes,
            QMessageBox.No,
        )

        return answer == QMessageBox.Yes

    def on_play(self, temp_dir=Path()):
        """
        Copies the ROM, including the current level, to a temporary directory and opens the rom in an emulator.
        """
        if not temp_dir.exists():
            QMessageBox.critical(self, "File Error", "No temp directory found.")
            return

        path_to_temp_rom = temp_dir / "instaplay.nes"

        ROM().save_to(path_to_temp_rom)

        if not self._save_changes_to_instaplay_rom(path_to_temp_rom):
            QMessageBox.critical(self, "File Error", "Couldn't save changes to temporary Rom.")
            return

        arguments = self.settings.value("editor/instaplay_arguments").replace("%f", str(path_to_temp_rom))
        arguments = shlex.split(arguments, posix=False)

        emu_path = Path(self.settings.value("editor/instaplay_emulator"))

        if emu_path.is_absolute():
            if emu_path.exists():
                emulator = str(emu_path)
            else:
                QMessageBox.critical(
                    self, "Emulator not found", f"Check it under File > Settings.\nFile {emu_path} not found."
                )
                return
        else:
            emulator = self.settings.value("editor/instaplay_emulator")

        try:
            subprocess.run([emulator, *arguments])
        except Exception as e:
            QMessageBox.critical(self, "Emulator command failed.", f"Check it under File > Settings.\n{e}")

    def _save_changes_to_instaplay_rom(self, path_to_temp_rom) -> bool:
        return False

    def _save_current_changes_to_file(self, pathname: str, set_new_path: bool):
        if self.level_ref:
            self.level_ref.save_to_rom()

        try:
            ROM().save_to_file(pathname, set_new_path)
        except IOError as exp:
            QMessageBox.warning(self, f"{type(exp).__name__}", f"Cannot save ROM data to file '{pathname}'.")

    def closeEvent(self, event: QCloseEvent):
        if not self.safe_to_change():
            event.ignore()
        else:
            super(MainWindow, self).closeEvent(event)
