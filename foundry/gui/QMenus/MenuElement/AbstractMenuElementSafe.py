from abc import ABC, abstractmethod

from PySide2.QtWidgets import QFileDialog, QMessageBox

from foundry.core.Requirable.RequirableSmartDecorator import SmartRequirableDecorator
from foundry.gui.QMenus import AbstractMenuElement


class AbstractMenuElementSafe(AbstractMenuElement, ABC):
    """A Menu Element that contains a test to see if something is safe to do"""
    def __init__(self, parent, add_action: bool = True) -> None:
        self.find_warnings = SmartRequirableDecorator(self.find_warnings)
        super().__init__(parent, add_action)
        self.path_to_rom = ""
        self.action.attach_required(self.safe_to_change)

    @property
    def path(self) -> str:
        """Gets the path to the desired location"""
        return QFileDialog.getOpenFileName(self.parent, caption=self.caption, filter=self.file_filter)[0]

    @property
    @abstractmethod
    def caption(self) -> str:
        """Provides the caption to ask for a file"""

    @property
    @abstractmethod
    def file_filter(self) -> str:
        """Provides the filter for finding the desired file"""

    def find_warnings(self):
        """Returns true or false depending if we make it through all the routines"""
        return True, '', ''

    def safe_to_change(self) -> bool:
        """Determines if it is safe to change"""
        safe, reason, additional_info = self.find_warnings()

        if safe:
            return True
        else:
            answer = QMessageBox.warning(
                self.parent,
                reason,
                f"{additional_info}\n\nDo you want to proceed?",
                QMessageBox.No | QMessageBox.Yes,
                QMessageBox.No,
            )
            return answer == QMessageBox.Yes

    @abstractmethod
    def action(self) -> bool:
        """The action of the object"""