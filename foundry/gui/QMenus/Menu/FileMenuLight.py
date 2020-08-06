from foundry.gui.QMenus import Menu
from foundry.gui.QMenus.FileMenu import OpenRomMenuElement, SaveROMMenuElement, SaveROMasMenuElement, \
    SaveASM6MenuElement, SettingsMenuElement
from foundry.gui.QMenus.MenuElement.MenuElementExitApplication import MenuElementExitApplication


class FileMenuLight(Menu):
    """A menu for loading files"""
    def __init__(self, parent):
        super().__init__(parent, "File")
        self.parent = parent

        self.open_rom_action = OpenRomMenuElement(self)
        self.addSeparator()
        self.save_rom_action = SaveROMMenuElement(self)
        self.save_rom_as_action = SaveROMasMenuElement(self)
        self.save_asm6_action = SaveASM6MenuElement(self)
        self.addSeparator()
        self.settings_action = SettingsMenuElement(self.parent, False)
        self.add_action(self.settings_action.name, self.settings_action.action)
        self.addSeparator()
        self.exit_action = MenuElementExitApplication(self.parent, False)
        self.add_action(self.exit_action.name, self.exit_action.action)