from PySide2.QtGui import Qt
from PySide2.QtWidgets import QToolBar, QSizePolicy


class MovableToolbar(QToolBar):
    """A QToolbar that allows dynamic movement on the screen"""

    def __init__(self, title: str, parent):
        super().__init__(title, parent)

        self.setContextMenuPolicy(Qt.PreventContextMenu)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.setOrientation(Qt.Horizontal)
        self.setFloatable(True)
        self.setAllowedAreas(Qt.LeftToolBarArea | Qt.BottomToolBarArea | Qt.RightToolBarArea)
