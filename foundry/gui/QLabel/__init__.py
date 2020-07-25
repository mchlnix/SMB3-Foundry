"""
This module includes all the different Labels for including text
"""

from typing import Optional
from PySide2.QtWidgets import QWidget, QLabel, QSizePolicy


from foundry.gui.QCore import MARGIN_TIGHT


class Label(QLabel):
    """A generic spinner with extended functionality"""
    def __init__(self, parent: Optional[QWidget], text: str) -> None:
        super().__init__(parent=parent)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setContentsMargins(0, 0, 0, 0)
        self.setText(text)

