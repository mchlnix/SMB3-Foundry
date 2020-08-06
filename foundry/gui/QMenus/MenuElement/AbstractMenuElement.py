from abc import abstractmethod

from foundry.gui.QMenus import Menu


class MenuElement:
    """An element of a menu"""
    def __init__(self, parent: Menu, add_action: bool = True) -> None:
        self.parent = parent
        if add_action:
            self.parent.add_action(self.name, self.action)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.parent})"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.parent})"

    @property
    @abstractmethod
    def base_name(self) -> str:
        """The base name of the element"""

    @property
    def bold(self) -> bool:
        """Determines if the element is bold"""
        return False

    @property
    def italic(self) -> bool:
        """Determines if the element is italic"""
        return False

    @property
    def name(self) -> str:
        """The real name of the element"""
        return f"{'*' if self.italic else ''}{'&' if self.bold else ''}{self.base_name}"

    @abstractmethod
    def action(self) -> None:
        """The action to be called"""