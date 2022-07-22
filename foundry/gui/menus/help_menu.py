from PySide6.QtGui import QAction, Qt
from PySide6.QtWidgets import QMenu, QMessageBox, QPushButton

from foundry import (
    discord_link,
    enemy_compat_link,
    feature_video_link,
    get_current_version_name,
    get_latest_version_name,
    github_link,
    icon,
    open_url,
    releases_link,
)
from foundry.gui.AboutWindow import AboutDialog


class HelpMenu(QMenu):
    def __init__(self, parent, title="&Help"):
        super(HelpMenu, self).__init__(title)

        self._parent = parent

        self.triggered.connect(self._on_trigger)

        self._check_updates_action = self.addAction("Check for Updates")
        self._check_updates_action.setIcon(icon("bell.svg"))

        self.addSeparator()

        self._video_action = self.addAction("Feature Video on YouTube")
        self._video_action.setIcon(icon("youtube.svg"))

        self._repo_action = self.addAction("Github Repository")
        self._repo_action.setIcon(icon("github.svg"))

        self._discord_action = self.addAction("SMB3 Rom Hacking Discord")
        self._discord_action.setIcon(icon("message-square.svg"))

        self.addSeparator()

        self._enemy_compat_action = self.addAction("Enemy Compatibility")
        self._enemy_compat_action.setIcon(icon("compass.svg"))

        self.addSeparator()

        self._about_action = self.addAction("About")
        self._about_action.setIcon(icon("info.svg"))

    def _on_trigger(self, action: QAction):
        if action is self._check_updates_action:
            self._on_check_for_update()

        elif action is self._video_action:
            open_url(feature_video_link)

        elif action is self._repo_action:
            open_url(github_link)

        elif action is self._discord_action:
            open_url(discord_link)

        elif action is self._enemy_compat_action:
            open_url(enemy_compat_link)

        elif action is self._about_action:
            about = AboutDialog(self)

            about.show()

    def _on_check_for_update(self):
        self._parent.setCursor(Qt.WaitCursor)

        current_version = get_current_version_name()

        try:
            latest_version = get_latest_version_name()
        except ValueError as ve:
            QMessageBox.critical(self._parent, "Error while checking for updates", f"Error: {ve}")
            self._parent.setCursor(Qt.ArrowCursor)
            return

        if current_version != latest_version:
            latest_release_url = f"{releases_link}/tag/{latest_version}"

            go_to_github_button = QPushButton(icon("external-link.svg"), "Go to latest release")
            go_to_github_button.clicked.connect(lambda: open_url(latest_release_url))

            info_box = QMessageBox(
                QMessageBox.Information, "New release available", f"New Version '{latest_version}' is available."
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

        info_box.addButton(QMessageBox.Cancel)
        info_box.addButton(go_to_github_button, QMessageBox.AcceptRole)

        info_box.exec()

        self._parent.setCursor(Qt.ArrowCursor)
