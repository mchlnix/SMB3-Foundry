

from foundry.gui.QMenus.Menu.Menu import Menu
from foundry.gui.QMenus.MenuElement.MenuElementSettings import MenuElementSettings
from foundry.gui.QMenus.MenuElement.MenuElementExitApplication import MenuElementExitApplication
from foundry.gui.QMenus.MenuElement.MenuElementNewOpen import MenuElementOpen
from foundry.gui.QMenus.MenuElement.MenuElementSaveAs import MenuElementSaveAs
from foundry.gui.QMenus.MenuElement.MenuElementNewSaveROM import MenuElementSaveROM


class FileMenu(Menu):
    """A menu for loading files"""
    def __init__(self, parent):
        super().__init__(parent, "File")
        self.parent = parent

        self.open_rom_action = MenuElementOpen.from_rom_file(self)
        self.open_m3l_action = MenuElementOpen.from_m3l_file(self)
        self.addSeparator()
        self.save_rom_action = MenuElementSaveROM(self)
        self.save_rom_as_action = MenuElementSaveAs.from_rom_file(self)
        self.save_m3l_action = MenuElementSaveAs.from_m3l_file(self)
        self.save_asm6_action = MenuElementSaveAs.from_asm6_file(self)
        self.addSeparator()
        self.settings_action = MenuElementSettings(self.parent, False)
        self.add_action(self.settings_action.name, self.settings_action.action)
        self.addSeparator()
        self.exit_action = MenuElementExitApplication(self.parent, False)
        self.add_action(self.exit_action.name, self.exit_action.action)