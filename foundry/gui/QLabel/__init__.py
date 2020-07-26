"""
This module includes all the different Labels for including text
"""

from typing import Optional
from PySide2.QtWidgets import QWidget, QLabel

from foundry.gui.QCore.util import DefaultSizePartial


class Label(QLabel, DefaultSizePartial):
    """A generic spinner with extended functionality"""
    def __init__(self, parent: Optional[QWidget], text: str) -> None:
        QLabel.__init__(self, parent)
        DefaultSizePartial.__init__(self)
        self.setText(text)

