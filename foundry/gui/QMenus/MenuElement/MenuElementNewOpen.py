

from foundry.gui.QMenus import Menu

from foundry.core.util import ROM_FILE_FILTER, M3L_FILE_FILTER, ASM6_FILE_FILER

from foundry.core.Action.ActionSelectFileToOpen import ActionSelectFileToOpen
from foundry.core.Action.ActionSafe import ActionSafe
from .AbstractNewMenuElement import AbstractMenuElement


class MenuElementOpen(AbstractMenuElement):
    """A menu element for opening files"""
    def __init__(
            self,
            parent: Menu,
            caption: str,
            file_filter: str,
            name: str = "open_file",
            menu_name: str = "Open File",
            add_action: bool = True
    ):
        self.name = menu_name
        super().__init__(parent, add_action)
        self._action = ActionSelectFileToOpen(name, ActionSafe, caption, file_filter)

    def action(self) -> None:
        """The action to be called"""
        self._action.observable.observable()

    @classmethod
    def from_rom_file(cls, parent: Menu, menu_name: str = "Open ROM", add_action: bool = True) -> "MenuElementOpen":
        """Makes a menu element open for a rom"""
        return cls(parent, "Select ROM", ROM_FILE_FILTER, "open_rom_file", menu_name, add_action)

    @classmethod
    def from_m3l_file(cls, parent: Menu, menu_name: str = "Open M3L", add_action: bool = True) -> "MenuElementOpen":
        """Makes a menu element open for a m3l"""
        return cls(parent, "Select M3L", M3L_FILE_FILTER, "open_m3l_file", menu_name, add_action)

    @classmethod
    def from_asm6_file(cls, parent: Menu, menu_name: str = "Open ASM6", add_action: bool = True) -> "MenuElementOpen":
        """Makes a menu element open for a asm6"""
        return cls(parent, "Select ASM6", ASM6_FILE_FILER, "open_asm6_file", menu_name, add_action)
