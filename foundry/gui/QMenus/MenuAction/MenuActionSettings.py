

from typing import Optional

from foundry.gui.QMenus import Menu
from foundry.gui.QMenus.MenuAction.MenuAction import MenuAction
from foundry.gui.settings import get_setting, set_setting, _main_container
from foundry.core.Settings.SettingsContainer import SettingsContainer


class MenuActionSettings(MenuAction):
    """Provides an easy interface to change settings from the Menu"""
    def __init__(
            self,
            parent: Menu,
            setting: str,
            name: str = "",
            add_action: bool = True,
            container: Optional[SettingsContainer] = None
    ) -> None:
        if container is None:
            super(MenuActionSettings, self).__init__(parent, get_setting(setting, True), name, add_action)
        else:
            super(MenuActionSettings, self).__init__(parent, container.safe_get_setting(setting, True), name, add_action)
        if container is None:
            self.add_observer(lambda value: set_setting(setting, value))
        else:
            self.add_observer(lambda value: container.set_setting(setting, value))
