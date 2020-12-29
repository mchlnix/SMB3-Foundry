from foundry.core.util import ASM6_FILE_FILTER
from foundry.gui.QMenus.MenuElement.AbstractMenuElementSave import AbstractMenuElementSave


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
        return ASM6_FILE_FILTER