"""
The container for all the local file menu functions
"""

from typing import Callable
from PySide2.QtWidgets import QAction, QMessageBox, QFileDialog
from PySide2.QtCore import QUrl
from PySide2.QtGui import QDesktopServices, QIcon
from abc import ABC

from foundry import icon_dir, data_dir
from foundry.core.Requirable.RequirableDecorator import RequirableDecorator
from foundry.core.Observables.ObservableDecorator import ObservableDecorator, ObservedAndRequired
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


class MenuElementSave(AbstractMenuElementSafe, ABC):
    """A Menu Element that contains tests required for saving"""
    def __init__(self, parent, add_action: bool = True) -> None:
        self.save = ObservableDecorator(self.save)
        self.can_change = RequirableDecorator(self.can_change)
        self.action = ObservedAndRequired(self.action)
        super().__init__(parent, add_action)
        self.action.attach_required(self.can_change)

    @property
    def path(self) -> str:
        """Gets the path to the desired location"""
        return QFileDialog.getSaveFileName(self.parent, caption=self.caption, filter=self.file_filter)[0]

    def can_change(self) -> bool:
        """Determines if it is safe to change"""
        return True

    def action(self):
        """Routine for handling the entire saving process"""
        path = self.path
        if not path:
            return False

        try:
            self.save(path)
        except IOError as exp:
            QMessageBox.warning(
                self.parent, f"{type(exp).__name__}", f"Cannot save ROM data to file '{path}'."
            )
            return False
        return True

    def save(self, path: str = "") -> str:
        """Saves to the file from path"""
        return path
