from foundry.core.util import DISCORD_LINK
from foundry.core.util.open_url import open_url
from foundry.gui.QMenus.MenuElement.AbstractMenuElementUpdater import AbstractMenuElementUpdater


class MenuElementDiscord(AbstractMenuElementUpdater):
    """A menu element to give a discord invite"""

    def action(self) -> None:
        """Loads git"""
        open_url(DISCORD_LINK)

    @property
    def base_name(self) -> str:
        """The base name fro the menu element"""
        return "SMB3 Rom Hacking Discord"