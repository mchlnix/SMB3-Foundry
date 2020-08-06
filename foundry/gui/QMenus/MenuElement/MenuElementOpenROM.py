from foundry.gui.QMenus.FileMenu import ROM_FILE_FILTER
from foundry.gui.QMenus.MenuElement.AbstractMenuElementOpen import MenuElementOpen


class MenuElementOpenROM(MenuElementOpen):
    """A menu element that handles opening a ROM"""

    def __init__(self, parent, add_action: bool = True) -> None:
        from foundry.game.File import load_from_file
        super().__init__(parent, add_action)
        self.open.attach_observer(load_from_file)

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