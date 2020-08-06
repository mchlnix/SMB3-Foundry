from abc import ABC

from PySide2.QtWidgets import QFileDialog, QMessageBox

from foundry.core.Observables.ObservableDecorator import ObservableDecorator, ObservedAndRequired
from foundry.core.Requirable.RequirableDecorator import RequirableDecorator
from foundry.gui.QMenus import AbstractMenuElementSafe


class AbstractMenuElementSave(AbstractMenuElementSafe, ABC):
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