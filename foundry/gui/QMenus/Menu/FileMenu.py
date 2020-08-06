from foundry.gui.QMenus import Menu
from foundry.gui.QMenus.FileMenu import OpenRomMenuElement, OpenM3LMenuElement, SaveROMMenuElement, \
    SaveROMasMenuElement, SaveM3LMenuElement, SaveASM6MenuElement, SettingsMenuElement, ExitApplicationMenuElement


class FileMenu(Menu):
    """A menu for loading files"""
    def __init__(self, parent):
        super().__init__(parent, "File")
        self.parent = parent

        self.open_rom_action = OpenRomMenuElement(self)
        self.open_m3l_action = OpenM3LMenuElement(self)
        self.addSeparator()
        self.save_rom_action = SaveROMMenuElement(self)
        self.save_rom_as_action = SaveROMasMenuElement(self)
        self.save_m3l_action = SaveM3LMenuElement(self)
        self.save_asm6_action = SaveASM6MenuElement(self)
        self.addSeparator()
        self.settings_action = SettingsMenuElement(self.parent, False)
        self.add_action(self.settings_action.name, self.settings_action.action)
        self.addSeparator()
        self.exit_action = ExitApplicationMenuElement(self.parent, False)
        self.add_action(self.exit_action.name, self.exit_action.action)