"""
This module includes a push button with extended functionality
"""

from typing import List, Optional
from PySide2.QtWidgets import QPushButton, QWidget
from PySide2.QtGui import QColor

from foundry.gui.QCore.util import DefaultSizePartial
from foundry.core.Action.Action import Action, AbstractActionObject


class PushButton(QPushButton, AbstractActionObject, DefaultSizePartial):
    """A generic push button with extended functionality"""
    def __init__(self, parent: Optional[QWidget], name: Optional[str] = ""):
        QPushButton.__init__(parent, name)
        DefaultSizePartial.__init__(self)
        AbstractActionObject.__init__(self)

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action.from_signal("clicked", self.clicked, False),
            Action.from_signal("pressed", self.pressed, False),
            Action.from_signal("released", self.released, False)
        ]


class ColoredPushButton(PushButton):
    """A colored push button"""
    def __init__(self, parent: Optional[QWidget], color: QColor):
        super().__init__(parent=parent)
        self.setStyleSheet(f"background-color:rgb({color.red},{color.green},{color.blue})")
