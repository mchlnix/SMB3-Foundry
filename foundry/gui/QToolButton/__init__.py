"""
This module includes a tool button with extended functionality
"""

from typing import List, Optional
from PySide2.QtWidgets import QToolButton, QWidget
from PySide2.QtCore import QSize

from foundry.gui.QCore import BUTTON_TINY
from foundry.game.gfx.Palette import Color
from foundry.gui.QCore.util import DefaultSizePartial
from foundry.gui.QCore.Action import Action, AbstractActionObject
from foundry.core.Observables.ObservableDecorator import ObservableDecorator


class ColoredToolButton(QToolButton, AbstractActionObject, DefaultSizePartial):
    """A generic tool button with extended functionality"""
    def __init__(self, parent: Optional[QWidget], color: Color):
        QToolButton.__init__(self, parent)
        DefaultSizePartial.__init__(self)
        AbstractActionObject.__init__(self)
        self.color = color

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.parent}, {self.color})"

    def sizeHint(self) -> QSize:
        """The size hint for the button"""
        return QSize(BUTTON_TINY, BUTTON_TINY)

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action.from_signal("clicked", self.clicked, False),
            Action.from_signal("pressed", self.pressed, False),
            Action.from_signal("released", self.released, False),
            Action("color_change", ObservableDecorator(lambda color: color))
        ]

    @property
    def color(self) -> Color:
        """Returns the current color of the button"""
        return self._color

    @color.setter
    def color(self, color: Color) -> None:
        self._set_color(color)
        self.color_change_action.observer(color)

    def _set_color(self, color: Color) -> None:
        """Sets the color without sending a message to the signal, use sparingly"""
        self._color = color
        self.setStyleSheet(f"background-color:rgb({color.red},{color.green},{color.blue})")

    @classmethod
    def as_tiny(cls, *args, **kwargs) -> "ColoredToolButton":
        """Makes a tiny push button"""
        try:
            button = cls(*args, **kwargs)
            button.setBaseSize(BUTTON_TINY, BUTTON_TINY)
            button.setMinimumWidth(BUTTON_TINY)
            button.setMinimumHeight(BUTTON_TINY)
            return button
        except TypeError as err:
            raise TypeError(err, f"Did not create {cls} from {args} and {kwargs}")
