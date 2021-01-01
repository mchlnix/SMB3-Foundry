from typing import Callable

from PySide2.QtWidgets import QAction

from foundry.core.Observables.ObservableDecorator import ObservableDecorator
from foundry.gui.QMenus import Menu


class MenuAction(QAction):
    """An action from a menu"""
    def __init__(self, parent: Menu, value: bool, name: str = "", add_action: bool = True) -> None:
        super().__init__(parent)
        self.action = ObservableDecorator(self.action)
        self._menu_value = value
        self.parent = parent
        self.name = name
        self.setCheckable(True)
        self.setChecked(value)
        self.setText(name)
        self.triggered.connect(lambda: setattr(self, "menu_value", not self.menu_value))
        if add_action:
            self.parent.addAction(self)

    def add_observer(self, observer: Callable) -> None:
        """Adds an observer"""
        self.action.attach_observer(observer)

    @property
    def menu_value(self) -> bool:
        """Sets the value of the object"""
        return self._menu_value

    @menu_value.setter
    def menu_value(self, value: bool) -> None:
        if value != self.menu_value:
            self._menu_value = value
            self.action(value)

    def action(self, value: bool) -> bool:
        """The action of the object"""
        self.setChecked(value)
        return value