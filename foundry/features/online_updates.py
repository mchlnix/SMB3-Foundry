import json
import urllib.error
import urllib.request
from http.client import IncompleteRead
from typing import Callable

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import QMessageBox, QPushButton

from foundry import Settings, get_current_version_name, icon, open_url, releases_link
from foundry.gui.settings import ReleaseChannel

SHORT_COMMIT_LENGTH = 8  # characters


def get_release_data(timeout: int = 10) -> bytes:
    owner = "mchlnix"
    repo = "SMB3-Foundry"

    api_call = f"https://api.github.com/repos/{owner}/{repo}/releases"

    try:
        request = urllib.request.urlopen(api_call, timeout=timeout)
    except urllib.error.URLError as ue:
        raise ValueError(f"Network error {ue}")

    try:
        return request.read()
    except IncompleteRead as icr:
        raise ValueError("Read corrupted data from the internet.") from icr


def get_latest_version_name_from_data(data: bytes) -> str:
    try:
        json_data = json.loads(data)

        for release_info in json_data:
            version_name = release_info["tag_name"].strip()

            if version_name != "nightly":
                return version_name
        else:
            raise LookupError("Couldn't find a non-nightly release.")

    except (KeyError, IndexError, LookupError, json.JSONDecodeError):
        raise ValueError("Parsing the received information failed.")


def get_latest_nightly_hash(data: bytes) -> str:
    try:
        json_data = json.loads(data)

        for release_info in json_data:
            version_name = release_info["tag_name"].strip()

            if version_name == "nightly":
                return release_info["target_commitish"][:SHORT_COMMIT_LENGTH]
        else:
            # couldn't find nightly release
            return ""

    except (KeyError, IndexError, LookupError, json.JSONDecodeError):
        return ""


def is_nightly_new(new_nightly_hash: str):
    current_version = get_current_version_name()

    if not current_version.startswith("nightly-"):
        # current version is a stable release, nightly releases should always be newer than stable releases
        return True

    current_nightly_hash = current_version.removeprefix("nightly-")

    # we expect new hashes to be the same length or longer, but just in case make sure they are the same size
    if len(new_nightly_hash) < len(current_nightly_hash):
        current_nightly_hash = current_nightly_hash[: len(new_nightly_hash)]

    # there's always only one nightly release, and it's the most up to date, so if these don't match, there's a new one
    return not new_nightly_hash.startswith(current_nightly_hash)


def check_for_update() -> tuple[str, str]:
    data = get_release_data()

    latest_version_name = get_latest_version_name_from_data(data)
    latest_nightly_hash = get_latest_nightly_hash(data)

    return latest_version_name, latest_nightly_hash


class UpdateChecker(QThread):
    check_finished = Signal(str, str)
    check_failed = Signal(str)

    def __init__(self):
        super().__init__()

        self.honor_ignore = False
        """A config that gets set from the outside and that we return to the connected slots."""

        self.blocking = False

    def run_blocking(self, honor_ignore):
        self.honor_ignore = honor_ignore
        self.blocking = True

        self.run()

    def run_in_background(self, honor_ignore):
        self.honor_ignore = honor_ignore
        self.blocking = False

        self.start()

    def run(self):
        try:
            latest_version_name, latest_nightly_hash = check_for_update()
            self.check_finished.emit(latest_version_name, latest_nightly_hash)
        except Exception as e:
            self.check_failed.emit(str(e))


class UpdateCheckMixin:
    settings: Settings
    setCursor: Callable

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._update_checker = UpdateChecker()
        self._update_checker.check_finished.connect(self._on_update_finished)
        self._update_checker.check_failed.connect(self._on_update_failed)

    def _on_update_failed(self, error_message: str):
        QMessageBox.critical(self, "Update Error", error_message)

    def _on_update_finished(self, stable_version: str, nightly_commit_hash: str):
        stable_asked = self._try_query_for_stable_update(stable_version, self._update_checker.honor_ignore)
        nightly_asked = self._try_query_for_nightly_update(nightly_commit_hash)

        # only show this message if we were blocking, aka manually checked for an update
        if not stable_asked and not nightly_asked and self._update_checker.blocking:
            QMessageBox.information(self, "Update", "Already up to date.")

    def _try_query_for_stable_update(self, stable_release_name: str, honor_ignore=True) -> bool:
        assert not stable_release_name.startswith("nightly")

        version_is_ignored = stable_release_name == self.settings.value("editor/version_to_ignore")
        if version_is_ignored and honor_ignore:
            # don't ask for this release again
            return False

        if stable_release_name == get_current_version_name():
            # already have that version
            return False

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

        return True

    def _try_query_for_nightly_update(self, nightly_commit_hash: str) -> bool:
        if self.settings.value("editor/release_channel") != ReleaseChannel.NIGHTLY:
            # not interested in nightly
            return False

        if not is_nightly_new(nightly_commit_hash):
            # already have that version
            return False

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

        return True

    def _ignore_latest_version(self, latest_version: str):
        self.settings.setValue("editor/version_to_ignore", latest_version)

    def check_for_update(self, honor_ignore=True, in_background=True):
        self.setCursor(Qt.CursorShape.WaitCursor)

        if self._update_checker.isRunning():
            QMessageBox.critical(self, "Update Error", "An update check is already running.")

        elif in_background:
            self._update_checker.run_in_background(honor_ignore)

        else:
            self._update_checker.run_blocking(honor_ignore)

        self.setCursor(Qt.CursorShape.ArrowCursor)

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
