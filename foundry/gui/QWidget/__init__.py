

from typing import Optional
from PySide2.QtWidgets import QWidget

from foundry.gui.QCore.util import DefaultSizePartial


class Widget(QWidget, DefaultSizePartial):
    """QWidget with extended functionality"""
    def __init__(self, parent: Optional[QWidget] = None):
        QWidget.__init__(self, parent)
        DefaultSizePartial.__init__(self)
        self.parent = parent

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.parent})"
