from PySide6.QtGui import Qt
from PySide6.QtWidgets import QLabel, QMainWindow, QTabWidget

from scribe.gui.tool_window.block_picker import BlockPicker


class ToolWindow(QMainWindow):
    def __init__(self, parent):
        super(ToolWindow, self).__init__(parent)

        self.setWindowFlag(Qt.Tool, True)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)

        self.tabbed_widget = QTabWidget()

        self.tile_picker = BlockPicker()

        self.tabbed_widget.addTab(self.tile_picker, "Tiles")
        self.tabbed_widget.addTab(QLabel(), "Level Pointers")
        self.tabbed_widget.addTab(QLabel(), "Sprites")

        self.setCentralWidget(self.tabbed_widget)

    def set_zoom(self, zoom_level=2):
        self.tile_picker.set_zoom(zoom_level)
