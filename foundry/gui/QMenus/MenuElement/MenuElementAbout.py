from foundry.gui.AboutWindow import AboutDialog
from foundry.gui.QMenus.MenuElement.AbstractMenuElementUpdater import AbstractMenuElementUpdater


class MenuElementAbout(AbstractMenuElementUpdater):
    """A menu element to give a discord invite"""

    def action(self) -> None:
        """Loads git"""
        about_dialog = AboutDialog(self.parent)
        about_dialog.show()

    @property
    def base_name(self) -> str:
        """The base name fro the menu element"""
        return "About"