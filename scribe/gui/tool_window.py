from PySide6.QtGui import Qt
from PySide6.QtWidgets import QLabel, QMainWindow, QTabWidget


class ToolWindow(QMainWindow):
    def __init__(self, parent):
        super(ToolWindow, self).__init__(parent)

        self.setWindowFlag(Qt.Tool, True)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)

        self.tabbed_widget = QTabWidget()
        self.tabbed_widget.addTab(QLabel(), "Tiles")
        self.tabbed_widget.addTab(QLabel(), "Level Pointers")
        self.tabbed_widget.addTab(QLabel(), "Sprites")

        self.setCentralWidget(self.tabbed_widget)
