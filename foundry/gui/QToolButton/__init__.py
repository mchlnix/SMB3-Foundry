"""
This module includes a tool button with extended functionality
"""

from typing import Callable, Optional
from PySide2.QtWidgets import QToolButton, QFormLayout, QWidget, QSizePolicy

from foundry.gui.QCore import BUTTON_TINY, MARGIN_TIGHT
from foundry.gui.QLabel import Label
from foundry.decorators.Observer import Observed
from foundry.game.gfx.Palette import Color


class ColoredToolButton(QToolButton):
    """A generic tool button with extended functionality"""
    def __init__(self, parent: Optional[QWidget], color: Color, return_call=None):
        super().__init__(parent=parent)
        self.return_call = return_call
        self.color = color

        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.setContentsMargins(MARGIN_TIGHT, MARGIN_TIGHT, MARGIN_TIGHT, MARGIN_TIGHT)
        self._action = Observed(self._action)
        self.clicked.connect(self._action)

    @property
    def color(self) -> Color:
        """Returns the current color of the button"""
        return self._color

    @color.setter
    def color(self, color: Color) -> None:
        self._color = color
        self.setStyleSheet(f"background-color:rgb({color.red},{color.green},{color.blue})")

    def add_observer(self, observer: Callable) -> None:
        """Adds an observer to the value"""
        self._action.attach_observer(observer)

    def _action(self, *_) -> int:
        """
        Extends the connect functionality from Qt
        """
        return self.color if self.return_call is None else self.return_call

    @classmethod
    def as_tiny(cls, *args, **kwargs) -> "ColoredToolButton":
        """Makes a tiny push button"""
        button = cls(*args, **kwargs)
        button.setFixedWidth(BUTTON_TINY)
        button.setFixedHeight(BUTTON_TINY)
        return button


class ToolButtonPanel(QWidget):
    """A tool button panel with a basic form layout"""
    def __init__(self, parent: Optional[QWidget], name: str, button: ColoredToolButton):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.parent = parent
        self.button = button
        self.add_observer = self.button.add_observer
        panel_layout = QFormLayout()
        panel_layout.addRow(self.button, Label(self.parent, name))
        self.setLayout(panel_layout)
