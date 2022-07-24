from PySide6.QtGui import QCloseEvent, QUndoStack
from PySide6.QtWidgets import QMainWindow, QMessageBox

from foundry.game.File import ROM
from foundry.game.level.LevelRef import LevelRef


class MainWindow(QMainWindow):
    undo_stack: QUndoStack

    def __init__(self):
        super(MainWindow, self).__init__()

        self.level_ref = LevelRef()

    def safe_to_change(self) -> bool:
        if not (self.level_ref and self.level_ref.level.changed) and self.undo_stack.isClean():
            return True

        return self.confirm_changes()

    def confirm_changes(self):
        answer = QMessageBox.question(
            self,
            "Please confirm",
            "Current content has not been saved! Proceed?",
            QMessageBox.No | QMessageBox.Yes,
            QMessageBox.No,
        )

        return answer == QMessageBox.Yes

    def _save_current_changes_to_file(self, pathname: str, set_new_path: bool):
        self.level_ref.save_to_rom()

        try:
            ROM().save_to_file(pathname, set_new_path)
        except IOError as exp:
            QMessageBox.warning(self, f"{type(exp).__name__}", f"Cannot save ROM data to file '{pathname}'.")

    def closeEvent(self, event: QCloseEvent):
        if not self.safe_to_change():
            event.ignore()
        else:
            super(MainWindow, self).closeEvent(event)
