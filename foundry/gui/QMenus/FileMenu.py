
from typing import Callable
from functools import wraps, update_wrapper
from abc import abstractmethod
from PySide2.QtWidgets import QFileDialog, QMessageBox, QWidget

from foundry.gui.SettingsDialog import show_settings
from foundry.decorators.Observer import Observed, ObservedAndRequired
from . import Menu, MenuElement, MenuElementOpen, MenuElementSave


ROM_FILE_FILTER = "ROM files (*.nes *.rom);;All files (*)"
M3L_FILE_FILTER = "M3L files (*.m3l);;All files (*)"
ASM6_FILE_FILER = "ASM files (*.asm);; All files (*)"
IMG_FILE_FILTER = "Screenshots (*.png);;All files (*)"


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
        self.exit_action = ExitMenuElement(self.parent, False)
        self.add_action(self.exit_action.name, self.exit_action.action)


class ExitMenuElement(MenuElement):
    """A menu element that handles exiting the window"""
    @property
    def base_name(self) -> str:
        """The real name of the element"""
        return "Exit"

    def action(self):
        """Exits the window"""
        self.parent.close()


class SettingsMenuElement(MenuElement):
    """A menu element that handles opening the settings"""
    @property
    def base_name(self) -> str:
        """The real name of the element"""
        return "Settings"

    def action(self):
        """Shows the settings"""
        show_settings(self.parent)


class OpenRomMenuElement(MenuElementOpen):
    """A menu element that handles opening a ROM"""

    def __init__(self, parent, add_action: bool = True) -> None:
        from foundry.game.File import ROM
        super().__init__(parent, add_action)
        self.open.attach_observer(ROM.load_from_file)

    @property
    def base_name(self) -> str:
        """The real name of the element"""
        return "Open ROM"

    @property
    def caption(self) -> str:
        """Provides the caption to ask for a file"""
        return "Select ROM"

    @property
    def file_filter(self) -> str:
        """Provides the filter for finding the desired file"""
        return ROM_FILE_FILTER


class OpenM3LMenuElement(MenuElementOpen):
    """A menu element that handles opening a M3L"""
    @property
    def base_name(self) -> str:
        """The real name of the element"""
        return "Open M3L"

    @property
    def caption(self) -> str:
        """Provides the caption to ask for a file"""
        return "Select M3L"

    @property
    def file_filter(self) -> str:
        """Provides the filter for finding the desired file"""
        return M3L_FILE_FILTER


class SaveROMMenuElement(MenuElementSave):
    """A menu element that handles saving a ROM"""
    @property
    def path(self) -> str:
        """Gets the path to the desired location"""
        from foundry.game.File import ROM
        return ROM.path

    @property
    def base_name(self) -> str:
        """The real name of the element"""
        return "Save ROM"

    @property
    def caption(self) -> str:
        """Provides the caption to ask for a file"""
        return "Save ROM"

    @property
    def file_filter(self) -> str:
        """Provides the filter for finding the desired file"""
        return ROM_FILE_FILTER


class SaveROMasMenuElement(MenuElementSave):
    """A menu element that handles saving a ROM"""
    @property
    def base_name(self) -> str:
        """The real name of the element"""
        return "Save ROM as"

    @property
    def caption(self) -> str:
        """Provides the caption to ask for a file"""
        return "Save ROM"

    @property
    def file_filter(self) -> str:
        """Provides the filter for finding the desired file"""
        return ROM_FILE_FILTER


class SaveM3LMenuElement(MenuElementSave):
    """A menu element that handles saving a ROM"""
    @property
    def base_name(self) -> str:
        """The real name of the element"""
        return "Save M3L"

    @property
    def caption(self) -> str:
        """Provides the caption to ask for a file"""
        return "Save M3L as"

    @property
    def file_filter(self) -> str:
        """Provides the filter for finding the desired file"""
        return M3L_FILE_FILTER


class SaveASM6MenuElement(MenuElementSave):
    """A menu element that handles saving a ROM"""
    @property
    def base_name(self) -> str:
        """The real name of the element"""
        return "Save ASM6"

    @property
    def caption(self) -> str:
        """Provides the caption to ask for a file"""
        return "Save ASM6 as"

    @property
    def file_filter(self) -> str:
        """Provides the filter for finding the desired file"""
        return ASM6_FILE_FILER
