from foundry.gui.QMenus import Menu
from foundry.gui.QMenus.FileMenu import MenuElementOpenRom, MenuElementSaveROM, MenuElementSaveROMas, \
    MenuElementSaveASM6
from foundry.gui.QMenus.MenuElement.MenuElementSettings import MenuElementSettings
from foundry.gui.QMenus.MenuElement.MenuElementExitApplication import MenuElementExitApplication


class FileMenuLight(Menu):
    """A menu for loading files"""
    def __init__(self, parent):
        super().__init__(parent, "File")
        self.parent = parent

        self.open_rom_action = MenuElementOpenRom(self)
        self.addSeparator()
        self.save_rom_action = MenuElementSaveROM(self)
        self.save_rom_as_action = MenuElementSaveROMas(self)
        self.save_asm6_action = MenuElementSaveASM6(self)
        self.addSeparator()
        self.settings_action = MenuElementSettings(self.parent, False)
        self.add_action(self.settings_action.name, self.settings_action.action)
        self.addSeparator()
        self.exit_action = MenuElementExitApplication(self.parent, False)
        self.add_action(self.exit_action.name, self.exit_action.action)