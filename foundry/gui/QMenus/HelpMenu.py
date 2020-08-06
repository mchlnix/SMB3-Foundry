"""
Prefabs for help menus
"""

from ...core.util import DISCORD_LINK
from ...core.util.open_url import open_url
from .MenuElement.AbstractMenuElementUpdater import AbstractMenuElementUpdater
from foundry.gui.AboutWindow import AboutDialog


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