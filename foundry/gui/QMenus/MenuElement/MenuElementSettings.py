from foundry.gui.QMenus.MenuElement.AbstractMenuElement import AbstractMenuElement
from foundry.gui.SettingsDialog import SettingsDialog


class MenuElementSettings(AbstractMenuElement):
    """A menu element that handles opening the settings"""
    @property
    def base_name(self) -> str:
        """The real name of the element"""
        return "Settings"

    def action(self):
        """Shows the settings"""
        SettingsDialog(self.parent, self.parent).exec_()
