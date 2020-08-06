from foundry.core.util import M3L_FILE_FILTER
from foundry.gui.QMenus.MenuElement.AbstractMenuElementSave import AbstractMenuElementSave


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