"""
This module includes all the different Labels for including text
"""

from typing import Optional
from PySide2.QtWidgets import QWidget, QLabel, QSizePolicy


class Label(QLabel):
    """A generic spinner with extended functionality"""
    def __init__(self, parent: Optional[QWidget], text: str) -> None:
        super().__init__(parent=parent)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setFixedHeight(self.sizeHint().toTuple()[1] + 6)
        self.setText(text)

