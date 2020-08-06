from foundry.core.util import GIT_LINK
from foundry.core.util.open_url import open_url
from foundry.gui.QMenus.MenuElement.AbstractMenuElementUpdater import AbstractMenuElementUpdater


class MenuElementGithub(AbstractMenuElementUpdater):
    """A menu element to load the github repository"""

    def action(self) -> None:
        """Loads git"""
        open_url(GIT_LINK)

    @property
    def base_name(self) -> str:
        """The base name fro the menu element"""
        return "Github Repository"