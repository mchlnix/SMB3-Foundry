from foundry.gui.QMenus.FileMenu import M3L_FILE_FILTER
from foundry.gui.QMenus.MenuElement.AbstractMenuElementOpen import MenuElementOpen


class MenuElementOpenM3L(MenuElementOpen):
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