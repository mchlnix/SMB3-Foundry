from foundry.gui.QMenus.FileMenu import ROM_FILE_FILTER
from foundry.gui.QMenus.MenuElement.AbstractMenuElementSave import AbstractMenuElementSave


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