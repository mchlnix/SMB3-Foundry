"""
The container for all the local file menu functions
"""

from typing import Callable
from PySide2.QtWidgets import QAction
from PySide2.QtCore import QUrl
from PySide2.QtGui import QDesktopServices, QIcon

from foundry import icon_dir, data_dir
from foundry.core.Observables.ObservableDecorator import ObservableDecorator
from foundry.gui.QMenus.Menu.Menu import Menu
from foundry.gui.QMenus.MenuElement.AbstractMenuElementSafe import AbstractMenuElementSafe
from foundry.gui.QMenus.MenuElement.AbstractMenuElement import AbstractMenuElement


def open_url(url: str):
    """Opens a given URL"""
    QDesktopServices.openUrl(QUrl(url))


def icon(icon_name: str):
    """Gets an icon"""
    icon_path = icon_dir / icon_name
    data_path = data_dir / icon_name

    if icon_path.exists():
        return QIcon(str(icon_path))
    elif data_path.exists():
        return QIcon(str(data_path))
    else:
        raise FileNotFoundError(icon_path)


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

