"""
This module provides a PositionSpinner
PositionSpinner: A class that handles both a x and y spinner and has its own position update
action_position: An observer that returns the updated position
position: The current position of the spinner
"""

from typing import Optional, List
from PySide2.QtWidgets import QWidget

from foundry.gui.QSpinner.MultiSpinner import MultiSpinner, SpinnerAttributes
from foundry.game.Position import Position
from foundry.core.Observable import Observed
from foundry.gui.QCore.Action import Action


class PositionSpinner(MultiSpinner):
    """A spinner in charge of the keeping the position"""
    def __init__(self, parent: Optional[QWidget], position: Position = Position(0, 0)):
        MultiSpinner.__init__(self, parent, [SpinnerAttributes("Pos X", 0, 0xFF), SpinnerAttributes("Pos Y", 0, 0xFF)])
        self.parent = parent
        self._position = position

        self.position_changed_action.observer.attach(lambda rect: print(rect))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.parent}, {self.position})"

    def _update_changed_values(self):
        """Returns the changed values from the spinners"""
        self.values_changed_action.observer([spinner.value() for spinner in self.spinners])
        self._position = Position(self.spinners[0].value(), self.spinners[1].value())
        self.position_changed_action.observer(self.position)

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action("values_changed", Observed(lambda value: value)),
            Action("position_changed", Observed(lambda pos: pos)),
            Action("text_changed", Observed(lambda text: text)),
        ]

    @property
    def position(self) -> Position:
        """Returns the current position"""
        return self._position

    @position.setter
    def position(self, pos: Position) -> None:
        self._position = pos
        self.spinners[0].setValue(pos.x)
        self.spinners[1].setValue(pos.y)
        self._update_changed_values()
