"""
This module provides a PositionSpinner
PositionSpinner: A class that handles both a x and y spinner and has its own position update
action_position: An observer that returns the updated position
position: The current position of the spinner
"""

from typing import Optional, Callable
from PySide2.QtWidgets import QWidget

from foundry.gui.QSpinner.MultiSpinner import MultiSpinner, SpinnerAttributes
from foundry.game.Position import Position
from foundry.decorators.Observer import Observed


class PositionSpinner(MultiSpinner):
    """A spinner in charge of the keeping the position"""
    def __init__(self, parent: Optional[QWidget], position: Position = Position(0, 0)):
        super().__init__(parent, [SpinnerAttributes("Pos X", 0, 0xFF), SpinnerAttributes("Pos Y", 0, 0xFF)])
        self.parent = parent
        self.action_position = Observed(lambda pos: Position(pos[0], pos[1]))
        self.position = position
        self.action.attach(self.action_position)
        self.action_position.attach(lambda pos: self.__setattr__("_position", pos))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.parent}, {self.position})"

    @property
    def position(self) -> Position:
        """Returns the current position"""
        return self._position

    @position.setter
    def position(self, pos: Position) -> None:
        self._position = pos
        self.spinners[0].spinner.setValue(pos.x)
        self.spinners[1].spinner.setValue(pos.y)
        self.action_position.notify(pos)

    def add_observer(self, observer: Callable):
        """Adds an observer"""
        self.action_position.attach(observer)
