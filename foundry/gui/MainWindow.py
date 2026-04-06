import shlex
import subprocess
from pathlib import Path

from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QCloseEvent, Qt, QUndoStack
from PySide6.QtWidgets import QMainWindow, QMessageBox, QPushButton

from foundry import (
    Settings,
    get_current_version_name,
    icon,
    open_url,
    releases_link,
)
from foundry.features.online_updates import check_for_update, is_nightly_new
from foundry.game.File import ROM
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.settings import ReleaseChannel
from foundry.gui.util import center_widget


class MainWindow(QMainWindow):
    undo_stack: QUndoStack
    settings: Settings

    def __init__(self):
        super(MainWindow, self).__init__()

        center_widget(self)

        self.level_ref = LevelRef()

    def check_for_update_on_startup(self):
        if not self._should_check():
            return

        self.check_for_update()

    def _should_check(self) -> bool:
        if not self.settings.value("editor/asked_for_startup"):
            self._ask_for_release_channel()

        return self.settings.value("editor/release_channel") != ReleaseChannel.NONE

    def _ask_for_release_channel(self):
        answer = QMessageBox.question(
            self,
            "Automatic Update Checks",
            "Do you want the editor to automatically check for updates on startup?",
        )

        self.settings.setValue("editor/asked_for_startup", True)

        if answer == QMessageBox.StandardButton.Yes:
            # default to stable on first try
            self.settings.setValue("editor/release_channel", ReleaseChannel.STABLE)
        else:
            self.settings.setValue("editor/release_channel", ReleaseChannel.NONE)

    def check_for_update(self, honor_ignore=True):
        self.setCursor(Qt.CursorShape.WaitCursor)

        latest_version, nightly_commit_hash = check_for_update(self)

        self._try_query_for_stable_update(latest_version, honor_ignore)
        self._try_query_for_nightly_update(nightly_commit_hash)

        self.setCursor(Qt.CursorShape.ArrowCursor)

    def _try_query_for_stable_update(self, stable_release_name: str, honor_ignore=True):
        if not stable_release_name:
            # error occurred
            return

        assert not stable_release_name.startswith("nightly")

        version_is_ignored = stable_release_name == self.settings.value("editor/version_to_ignore")
        if version_is_ignored and honor_ignore:
            # don't ask for this release again
            return

        if stable_release_name == get_current_version_name():
            # already have that version
            return

        latest_release_url = f"{releases_link}/tag/{stable_release_name}"

        go_to_github_button = QPushButton(icon("external-link.svg"), "Go to latest release")
        go_to_github_button.clicked.connect(lambda: open_url(latest_release_url))

        info_box = QMessageBox(
            QMessageBox.Icon.Information,
            "New release available",
            f"New Version '{stable_release_name}' is available.",
        )

        ignore_button = QPushButton(f"Don't ask again for '{stable_release_name}'")
        ignore_button.clicked.connect(lambda: self._ignore_latest_version(stable_release_name))
        info_box.addButton(ignore_button, QMessageBox.ButtonRole.NoRole)

        info_box.addButton(QMessageBox.StandardButton.Cancel)
        info_box.addButton(go_to_github_button, QMessageBox.ButtonRole.AcceptRole)

        info_box.exec()

    def _try_query_for_nightly_update(self, nightly_commit_hash: str):
        if not nightly_commit_hash:
            # error occurred
            return

        if self.settings.value("editor/release_channel") != ReleaseChannel.NIGHTLY:
            # not interested in nightly
            return

        if not is_nightly_new(nightly_commit_hash):
            # already have that version
            return

        info_box = QMessageBox(
            QMessageBox.Icon.Information,
            "Newer nightly release available",
            "A newer 'nightly' version is available for download.",
        )

        go_to_github_button = QPushButton(icon("external-link.svg"), "Go to latest nightly")
        go_to_github_button.clicked.connect(lambda: open_url(releases_link))

        info_box.addButton(QMessageBox.StandardButton.Cancel)
        info_box.addButton(go_to_github_button, QMessageBox.ButtonRole.AcceptRole)

        info_box.exec()

    def _ignore_latest_version(self, latest_version: str):
        self.settings.setValue("editor/version_to_ignore", latest_version)

    def safe_to_change(self) -> bool:
        return self.undo_stack.isClean() or self.confirm_changes()

    def confirm_changes(self):
        answer = QMessageBox.question(
            self,
            "Please confirm",
            "Current content has not been saved! Proceed?",
            QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
            QMessageBox.StandardButton.No,
        )

        return answer == QMessageBox.StandardButton.Yes

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

    def _save_current_changes_to_file(self, pathname: str, set_new_path: bool) -> bool:
        try:
            if self.level_ref:
                self.level_ref.save_to_rom()
        except LookupError as lue:
            QMessageBox.warning(self, type(lue).__name__, f"{lue}.")
            return False

        return self._write_to_rom(pathname, set_new_path)

    def _write_to_rom(self, pathname: str, set_new_path: bool):
        try:
            ROM.save_to_file(pathname, set_new_path)
        except IOError as exp:
            QMessageBox.warning(self, type(exp).__name__, f"Cannot save ROM data to file '{pathname}'.")

            return False

        return True

    def closeEvent(self, event: QCloseEvent):
        if not self.safe_to_change():
            event.ignore()
        else:
            super(MainWindow, self).closeEvent(event)
