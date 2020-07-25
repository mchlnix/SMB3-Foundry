"""
This module includes a push button with extended functionality
"""

from typing import Callable, Optional
from PySide2.QtWidgets import QPushButton, QFormLayout, QWidget, QSizePolicy
from PySide2.QtGui import QColor

from foundry.gui.QCore import BUTTON_TINY
from foundry.gui.QLabel import Label
from foundry.decorators.Observer import Observed


class PushButton(QPushButton):
    """A generic push button with extended functionality"""
    def __init__(self, parent: Optional[QWidget], name: Optional[str] = ""):
        super().__init__(parent=parent, text=name)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.action = Observed(self.action)
        self.clicked.connect(self.action)

    def add_observer(self, observer: Callable) -> None:
        """Adds an observer to the value"""
        self.action.attach_observer(observer)

    def action(self, new_value: int, *_) -> int:
        """
        Extends the connect functionality from Qt
        """
        return new_value

    @classmethod
    def as_tiny(cls, *args, **kwargs) -> "PushButton":
        """Makes a tiny push button"""
        button = cls(*args, **kwargs)
        button.setMinimumHeight(BUTTON_TINY)
        button.setMinimumWidth(BUTTON_TINY)
        button.setMinimumWidth(BUTTON_TINY)
        button.setMaximumHeight(BUTTON_TINY)
        return button


class ColoredPushButton(PushButton):
    """A colored push button"""
    def __init__(self, parent: Optional[QWidget], color: QColor):
        super().__init__(parent=parent)
        self.setStyleSheet(f"background-color:rgb({color.red},{color.green},{color.blue})")


class PushButtonPanel(QWidget):
    """A push button panel with a basic form layout"""
    def __init__(self, parent: Optional[QWidget], name: str, button: PushButton):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        self.parent = parent
        self.button = button
        self.action = self.button.action
        self.add_observer = self.button.add_observer
        panel_layout = QFormLayout()
        panel_layout.addRow(self.button, Label(self.parent, name))
        self.setLayout(panel_layout)
