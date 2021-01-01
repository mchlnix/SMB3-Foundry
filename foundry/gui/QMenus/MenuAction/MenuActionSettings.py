

from typing import Optional

from foundry.gui.QMenus import Menu
from foundry.gui.QMenus.MenuAction.MenuAction import MenuAction
from foundry.core.Settings.util import _main_container, get_setting, set_setting
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
        self.setting_name = setting
        self.container = _main_container if container is None else container
        super(MenuActionSettings, self).__init__(parent, self.setting, name, add_action)
        self.add_observer(lambda value: container.set_setting(setting, value))

    @property
    def setting(self) -> bool:
        """The value of the setting"""
        return self.container.safe_get_setting(self.setting_name, True)
