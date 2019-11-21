from PySide2.QtGui import Qt, QKeyEvent
from PySide2.QtWidgets import QMainWindow, QDialog


class CustomDialog(QDialog):
    def __init__(self, parent, title="Title"):
        super(CustomDialog, self).__init__(parent)

        self.setWindowTitle(title)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.on_exit()

    def on_exit(self):
        self.hide()
