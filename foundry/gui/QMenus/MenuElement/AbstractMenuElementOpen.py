from abc import ABC

from PySide2.QtWidgets import QMessageBox

from foundry.core.Observables.ObservableDecorator import ObservedAndRequired, ObservableDecorator
from foundry.gui.QMenus import AbstractMenuElementSafe


class MenuElementOpen(AbstractMenuElementSafe, ABC):
    """A Menu Element that contains tests required for opening"""
    def __init__(self, parent, add_action: bool = True) -> None:
        self.action = ObservedAndRequired(self.action)
        self.open = ObservableDecorator(lambda path: path)
        super().__init__(parent, add_action)

    def action(self):
        """Routine for handling the entire opening process"""
        path = self.path
        if not path:
            return False

        try:
            self.open(path)
        except IOError as exp:
            QMessageBox.warning(self.parent, type(exp).__name__, f"Cannot open file '{path}'.")
            return False
        return True