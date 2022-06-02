from PySide6.QtGui import Qt, QKeyEvent
from PySide6.QtWidgets import QMainWindow


class CustomChildWindow(QMainWindow):
    """
    A customized Mainwindow replacement, allowing to set a central widget.
    """

    def __init__(self, parent, title="Title"):
        super(CustomChildWindow, self).__init__(parent)

        self.setWindowTitle(title)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.on_exit()

    def on_exit(self):
        self.hide()
