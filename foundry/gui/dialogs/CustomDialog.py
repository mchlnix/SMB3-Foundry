from PySide6.QtGui import QKeyEvent, Qt
from PySide6.QtWidgets import QDialog


class CustomDialog(QDialog):
    def __init__(self, parent, title="Title"):
        super(CustomDialog, self).__init__(parent)

        self.setWindowTitle(title)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

    def on_exit(self):
        self.hide()

    def closeEvent(self, event):
        self.on_exit()
