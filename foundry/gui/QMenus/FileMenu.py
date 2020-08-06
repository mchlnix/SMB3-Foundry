"""
File menus to help streamline gui in regards to loading and saving files of different types
ROM_FILE_FILTER: The file filter for loading ROM (.nes or .rom) files
M3L_FILE_FILTER: The file filter for loading M3L files
ASM6_FILE_FILTER: The file filter for loading ASM6 (.asm) files
IMG_FILE_FILTER: The file filter for loading IMG (.png) files
FileMenu: The default file menu (used by the MainWindow)
FileMenuLight: A more reusable form the FileMenu
MenuElementExitApplication: An element to exit the program
MenuElementSettings: An element to load the settings
OpenROMMenuElement: An element to load the ROM
MenuElementOpenM3L: An element to load a M3L file
MenuElementSaveROM: An element to save the ROM directly from the ROM's path
MenuElementSaveROMas: An element to save the ROM
MenuElementSaveM3L: An element to save M3L files
MenuElementSaveASM6: An element to save ASM6 files
"""

from .MenuElement.AbstractMenuElementSave import AbstractMenuElementSave


ROM_FILE_FILTER = "ROM files (*.nes *.rom);;All files (*)"
M3L_FILE_FILTER = "M3L files (*.m3l);;All files (*)"
ASM6_FILE_FILER = "ASM files (*.asm);; All files (*)"
IMG_FILE_FILTER = "Screenshots (*.png);;All files (*)"


class MenuElementSaveROMas(AbstractMenuElementSave):
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


class MenuElementSaveM3L(AbstractMenuElementSave):
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


class MenuElementSaveASM6(AbstractMenuElementSave):
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
