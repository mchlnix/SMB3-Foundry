"""
Prefabs for help menus
"""

from PySide2.QtGui import Qt
from PySide2.QtWidgets import QMessageBox, QPushButton
from typing import Tuple, Optional

from .Menu.Menu import Menu
from ...core.util import RELEASES_LINK, FEATURE_VIDEO_LINK, GIT_LINK, DISCORD_LINK
from ...core.util.get_current_version_name import get_current_version_name
from ...core.util.get_latest_version_name import get_latest_version_name
from ...core.util.icon import icon
from ...core.util.open_url import open_url
from .MenuElement.AbstractMenuElementUpdater import AbstractMenuElementUpdater
from foundry.gui.AboutWindow import AboutDialog


class HelpMenu(Menu):
    """A menu for providing help"""
    def __init__(self, parent):
        super().__init__(parent, "Help")
        self.parent = parent

        self.updater_action = CheckForUpdateMenuElement(self.parent, False)
        self.add_action(self.updater_action.name, self.updater_action.action)
        self.addSeparator()
        self.feature_video_action = FeatureVideoMenuElement(self)
        self.git_action = GitMenuElement(self)
        self.discord_action = DiscordMenuElement(self)
        self.about_action = AboutMenuElement(self.parent, False)
        self.addSeparator()
        self.add_action(self.about_action.name, self.about_action.action)


def ask_for_update(needs_updating: bool, _: str, latest_version: str) -> None:
    """Asks the player for an update if needed"""
    if needs_updating is None:
        return
    elif needs_updating:
        latest_release_url = f"{RELEASES_LINK}/tag/{latest_version}"

        go_to_github_button = QPushButton(icon("external-link.svg"), "Go to latest release")
        go_to_github_button.clicked.connect(lambda *_: open_url(latest_release_url))

        info_box = QMessageBox(
            QMessageBox.Information, "New release available", f"New Version {latest_version} is available."
        )

        info_box.addButton(QMessageBox.Cancel)
        info_box.addButton(go_to_github_button, QMessageBox.AcceptRole)

        info_box.exec_()


class CheckForUpdateMenuElement(AbstractMenuElementUpdater):
    """Menu Element that checks for an update"""
    def __init__(self, parent, add_action: bool = True) -> None:
        super().__init__(parent, add_action)
        self.action.attach_observer(ask_for_update)
        self.action.attach_observer(self.confirm_up_to_date)
        self.action.attach_observer(lambda *_: self.parent.setCursor(Qt.ArrowCursor))

    def action(self) -> Tuple[Optional[bool], Optional[str], Optional[str]]:
        """The main method for the Menu Element"""
        self.parent.setCursor(Qt.WaitCursor)

        current_version = get_current_version_name()

        try:
            latest_version = get_latest_version_name()
        except ValueError as ve:
            QMessageBox.critical(self.parent, "Error while checking for updates", f"Error: {ve}")
            return None, current_version, None

        return current_version != latest_version, current_version, latest_version

    def confirm_up_to_date(self, needs_updating: bool, current_version: str, _: str):
        """Confirms we are up to data"""
        if needs_updating is None:
            return
        elif not needs_updating:
            QMessageBox.information(self.parent, "No newer release", f"Version {current_version} is up to date.")

    @property
    def base_name(self) -> str:
        """The base name for menu element"""
        return "Check For Updates"


class FeatureVideoMenuElement(AbstractMenuElementUpdater):
    """A menu element to load the feature video's link"""
    def action(self) -> None:
        """Loads the feature video"""
        open_url(FEATURE_VIDEO_LINK)

    @property
    def base_name(self) -> str:
        """The base name fro the menu element"""
        return "Feature Video on YouTube"


class GitMenuElement(AbstractMenuElementUpdater):
    """A menu element to load the github repository"""

    def action(self) -> None:
        """Loads git"""
        open_url(GIT_LINK)

    @property
    def base_name(self) -> str:
        """The base name fro the menu element"""
        return "Github Repository"


class DiscordMenuElement(AbstractMenuElementUpdater):
    """A menu element to give a discord invite"""

    def action(self) -> None:
        """Loads git"""
        open_url(DISCORD_LINK)

    @property
    def base_name(self) -> str:
        """The base name fro the menu element"""
        return "SMB3 Rom Hacking Discord"


class AboutMenuElement(AbstractMenuElementUpdater):
    """A menu element to give a discord invite"""

    def action(self) -> None:
        """Loads git"""
        about_dialog = AboutDialog(self.parent)
        about_dialog.show()

    @property
    def base_name(self) -> str:
        """The base name fro the menu element"""
        return "About"