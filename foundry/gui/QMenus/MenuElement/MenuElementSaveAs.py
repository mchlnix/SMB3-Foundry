

from foundry.gui.QMenus import Menu

from foundry.core.util import ROM_FILE_FILTER, M3L_FILE_FILTER, ASM6_FILE_FILTER

from foundry.core.Action.ActionSaveAs import ActionSaveAs
from foundry.core.Action.ActionSafe import ActionSafe
from .AbstractNewMenuElement import AbstractMenuElement


class MenuElementSaveAs(AbstractMenuElement):
    """A menu element for opening files"""
    def __init__(
            self,
            parent: Menu,
            caption: str,
            file_filter: str,
            name: str = "save_file_as",
            menu_name: str = "Save File",
            add_action: bool = True
    ):
        self.name = menu_name
        super().__init__(parent, add_action)
        self._action = ActionSaveAs(name, ActionSafe, caption, file_filter)

    def action(self) -> None:
        """The action to be called"""
        self._action.observable.observable()

    @classmethod
    def from_rom_file(cls, parent: Menu, menu_name: str = "Save ROM as", add_action: bool = True) -> "MenuElementSaveAs":
        """Makes a menu element open for a rom"""
        return cls(parent, "Save ROM as", ROM_FILE_FILTER, "save_rom_as", menu_name, add_action)

    @classmethod
    def from_m3l_file(cls, parent: Menu, menu_name: str = "Save M3L as", add_action: bool = True) -> "MenuElementSaveAs":
        """Makes a menu element open for a m3l"""
        return cls(parent, "Save M3L as", M3L_FILE_FILTER, "save_m3l_as", menu_name, add_action)

    @classmethod
    def from_asm6_file(cls, parent: Menu, menu_name: str = "Save ASM6 as", add_action: bool = True) -> "MenuElementSaveAs":
        """Makes a menu element open for a asm6"""
        return cls(parent, "Save ASM6 as", ASM6_FILE_FILTER, "save_asm6_as", menu_name, add_action)
