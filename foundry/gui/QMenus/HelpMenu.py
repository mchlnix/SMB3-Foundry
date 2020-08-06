"""
Prefabs for help menus
"""

from ...core.util import FEATURE_VIDEO_LINK, GIT_LINK, DISCORD_LINK
from ...core.util.open_url import open_url
from .MenuElement.AbstractMenuElementUpdater import AbstractMenuElementUpdater
from foundry.gui.AboutWindow import AboutDialog


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