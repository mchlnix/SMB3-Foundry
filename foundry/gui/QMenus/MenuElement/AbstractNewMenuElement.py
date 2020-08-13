from abc import abstractmethod
from typing import Optional

from foundry.gui.QMenus.Menu.Menu import Menu
from foundry.core.Action.Action import Action


class AbstractMenuElement:
    """An element of a menu"""
    def __init__(self, parent: Optional[Menu] = None, add_action: Optional[bool] = True) -> None:
        self.parent = parent
        self.name = ""
        if add_action and parent is not None:
            add_action = getattr(parent, "add_action", None)
            if callable(add_action):
                add_action(self.name, self.action)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.parent})"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.parent})"

    @abstractmethod
    def action(self) -> None:
        """The action to be called"""


def generate_menu_element(suffix: str, name: str, action: Action):
    """create the subclasses dynamically"""
    return type(
        f"{AbstractMenuElement.__class__.__name__}{suffix}",
        (AbstractMenuElement, object),
        {'action': action, 'name': name}
    )
