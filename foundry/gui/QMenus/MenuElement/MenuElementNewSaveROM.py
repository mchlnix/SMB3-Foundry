

from foundry.gui.QMenus import Menu


from foundry.core.Action.ActionSaveROM import ActionSaveROM
from .AbstractNewMenuElement import AbstractMenuElement


class MenuElementSaveROM(AbstractMenuElement):
    """A menu element for saving the rom directly"""
    def __init__(
            self,
            parent: Menu,
            name: str = "save_rom",
            menu_name: str = "Save ROM",
            add_action: bool = True
    ):
        self.name = menu_name
        super().__init__(parent, add_action)
        self._action = ActionSaveROM(name)

    def action(self) -> None:
        """The action to be called"""
        self._action.observable.observable()
