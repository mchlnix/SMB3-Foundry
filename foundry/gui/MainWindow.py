import shlex
import subprocess
from pathlib import Path

from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QCloseEvent, QUndoStack, Qt
from PySide6.QtWidgets import QMainWindow, QMessageBox, QPushButton

from foundry import (
    Settings,
    check_for_update,
    get_current_version_name,
    icon,
    open_url,
    releases_link,
)
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
                self,
                "Automatic Update Checks",
                "Do you want the editor to automatically check for updates on startup?",
            )

            self.settings.setValue("editor/asked_for_startup", True)
            self.settings.setValue("editor/update_on_startup", answer == QMessageBox.Yes)

        if not self.settings.value("editor/update_on_startup"):
            return

        self.check_for_update(ask_for_nightly=False)

    def check_for_update(self, ask_for_nightly=True, honor_ignore=True):
        # Retrieve current version from GitHub
        self.setCursor(Qt.WaitCursor)

        latest_version = check_for_update(self)
        current_version = get_current_version_name()

        error = not latest_version
        version_is_ignored = latest_version == self.settings.value("editor/version_to_ignore")
        should_ignore = version_is_ignored and honor_ignore

        update_available = latest_version != current_version
        nothing_to_update = not update_available and not ask_for_nightly

        if error or should_ignore or nothing_to_update:
            self.setCursor(Qt.ArrowCursor)
            return

        if update_available:
            latest_release_url = f"{releases_link}/tag/{latest_version}"

            go_to_github_button = QPushButton(icon("external-link.svg"), "Go to latest release")
            go_to_github_button.clicked.connect(lambda: open_url(latest_release_url))

            info_box = QMessageBox(
                QMessageBox.Information,
                "New release available",
                f"New Version '{latest_version}' is available.",
            )
        else:
            nightly_release_url = f"{releases_link}/tag/nightly"

            go_to_github_button = QPushButton(icon("external-link.svg"), "Check for nightly release")
            go_to_github_button.clicked.connect(lambda: open_url(nightly_release_url))

            info_box = QMessageBox(
                QMessageBox.Information,
                "No newer release",
                f"Stable version '{current_version}' is up to date. But there might be a newer 'nightly' version "
                f"available.",
            )

        if not version_is_ignored:
            ignore_button = QPushButton(f"Don't ask again for '{latest_version}'")
            ignore_button.clicked.connect(lambda: self._ignore_latest_version(latest_version))
            info_box.addButton(ignore_button, QMessageBox.ButtonRole.NoRole)

        info_box.addButton(QMessageBox.Cancel)
        info_box.addButton(go_to_github_button, QMessageBox.AcceptRole)

        info_box.exec()

        self.setCursor(Qt.ArrowCursor)

    def _ignore_latest_version(self, latest_version: str):
        self.settings.setValue("editor/version_to_ignore", latest_version)

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
                    self,
                    "Emulator not found",
                    f"Check it under File > Settings.\nFile {emu_path} not found.",
                )
                return
        else:
            emulator = self.settings.value("editor/instaplay_emulator")

        self.setDisabled(True)

        try:
            subprocess.run([emulator, *arguments])
        except Exception as e:
            QMessageBox.critical(
                self,
                "Emulator command failed.",
                f"Check it under File > Settings.\n{e}",
            )
        finally:
            QCoreApplication.processEvents()

            self.setDisabled(False)

    def _save_changes_to_instaplay_rom(self, path_to_temp_rom) -> bool:
        return False

    def _save_current_changes_to_file(self, pathname: str, set_new_path: bool):
        try:
            if self.level_ref:
                self.level_ref.save_to_rom()
        except LookupError as lue:
            QMessageBox.warning(self, f"{type(lue).__name__}", f"{lue}.")
            return

        try:
            ROM.save_to_file(pathname, set_new_path)
        except IOError as exp:
            QMessageBox.warning(
                self,
                f"{type(exp).__name__}",
                f"Cannot save ROM data to file '{pathname}'.",
            )

    def closeEvent(self, event: QCloseEvent):
        if not self.safe_to_change():
            event.ignore()
        else:
            super(MainWindow, self).closeEvent(event)
