from foundry.gui.QMenus import Menu
from foundry.gui.QMenus.MenuAction.MenuAction import MenuAction
from foundry.gui.settings import get_setting, set_setting


class MenuActionSettings(MenuAction):
    """Provides an easy interface to change settings from the Menu"""
    def __init__(self, parent: Menu, setting: str, name: str = "", add_action: bool = True) -> None:
        super(MenuActionSettings, self).__init__(parent, get_setting(setting, True), name, add_action)
        self.add_observer(lambda value: set_setting(setting, value))