from foundry.gui.QMenus.MenuElement.AbstractMenuElement import AbstractMenuElement


class MenuElementExitApplication(AbstractMenuElement):
    """A menu element that handles exiting the window"""
    @property
    def base_name(self) -> str:
        """The real name of the element"""
        return "Exit"

    def action(self):
        """Exits the window"""
        self.parent.close()