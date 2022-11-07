from PySide6.QtGui import QCloseEvent, QUndoStack
from PySide6.QtWidgets import QMainWindow, QMessageBox

from foundry import Settings, check_for_update
from foundry.game.File import ROM
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.util import center_widget


class MainWindow(QMainWindow):
    undo_stack: QUndoStack
    settings: Settings

    def __init__(self):
        super(MainWindow, self).__init__()

        center_widget(self)

        self.level_ref = LevelRef()

    def check_for_update_on_startup(self):
        if not self.settings.value("editor/asked_for_startup"):
            answer = QMessageBox.question(
                self, "Automatic Update Checks", "Do you want the editor to automatically check for updates on startup?"
            )

            self.settings.setValue("editor/asked_for_startup", True)
            self.settings.setValue("editor/update_on_startup", answer == QMessageBox.Yes)

        if self.settings.value("editor/update_on_startup"):
            check_for_update(self, only_for_named_version=True)

    def safe_to_change(self) -> bool:
        return self.undo_stack.isClean() or self.confirm_changes()

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
