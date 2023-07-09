from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu

from foundry import (
    discord_link,
    enemy_compat_link,
    feature_video_link,
    github_link,
    icon,
    open_url,
)
from foundry.gui.dialogs.AboutWindow import AboutDialog
from foundry.gui.MainWindow import MainWindow


class HelpMenu(QMenu):
    def __init__(self, parent: MainWindow, title="&Help"):
        super(HelpMenu, self).__init__(title)

        self._parent = parent

        self.triggered.connect(self._on_trigger)

        self.check_updates_action = self.addAction("Check for Updates")
        self.check_updates_action.setIcon(icon("bell.svg"))

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
        if action is self.check_updates_action:
            self._parent.check_for_update(ask_for_nightly=True, honor_ignore=False)

        elif action is self._video_action:
            open_url(feature_video_link)

        elif action is self._repo_action:
            open_url(github_link)

        elif action is self._discord_action:
            open_url(discord_link)

        elif action is self._enemy_compat_action:
            open_url(enemy_compat_link)

        elif action is self._about_action:
            self.on_about()

    def on_about(self):
        about = AboutDialog(self._parent)

        about.show()
