from typing import Callable

from PySide2.QtWidgets import QMenu, QAction


class Menu(QMenu):
    """A default menu"""
    def __init__(self, parent, title="", *args, **kwargs) -> None:
        super().__init__(parent=parent, title=title)
        self.parent = parent

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.parent})"

    """The custom extensions for the QMenu class"""
    def add_action(self, name: str, on_click: Callable) -> QAction:
        """
        Adds an item to the list automatically and makes a trigger that connects to the callable
        :param name: The name of the menu item
        :param on_click: The callable to be called
        :return: None
        """
        action = self.addAction(name)
        action.triggered.connect(on_click)
        return action