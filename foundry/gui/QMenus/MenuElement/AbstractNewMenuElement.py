from abc import abstractmethod
from typing import Optional

from foundry.gui.QMenus import Menu


class AbstractMenuElement:
    """An element of a menu"""
    def __init__(self, parent: Optional[Menu] = None, add_action: Optional[bool] = True) -> None:
        self.parent = parent
        if add_action and parent is not None:
            add_action = getattr(parent, "add_action", None)
            if callable(add_action):
                add_action(self.name, self.action)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.parent})"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.parent})"

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the element"""

    @abstractmethod
    def action(self) -> None:
        """The action to be called"""
