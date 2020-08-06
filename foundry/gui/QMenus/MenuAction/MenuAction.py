from typing import Callable

from PySide2.QtWidgets import QAction

from foundry.core.Observables.ObservableDecorator import ObservableDecorator
from foundry.gui.QMenus import Menu


class MenuAction(QAction):
    """An action from a menu"""
    def __init__(self, parent: Menu, value: bool, name: str = "", add_action: bool = True) -> None:
        super().__init__(parent)
        self.action = ObservableDecorator(self.action)
        self.parent = parent
        self.name = name
        self.setCheckable(True)
        self.setChecked(value)
        if add_action:
            self.parent.add_action(self.name, lambda: setattr(self, "value", not self.isChecked()))

    def add_observer(self, observer: Callable) -> None:
        """Adds an observer"""
        self.action.attach_observer(observer)

    @property
    def value(self) -> bool:
        """Sets the value of the object"""
        return self.isChecked()

    @value.setter
    def value(self, value: bool) -> None:
        self.action(value)

    def action(self, value: bool) -> bool:
        """The action of the object"""
        self.setChecked(value)
        return self.value