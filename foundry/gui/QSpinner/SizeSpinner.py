"""
This module contains the SizeSpinner
SizeSpinner: A spinner that has two spinners for width and height.  Has an update routine that returns a Size
action_size: An observer that returns the new Size
the_size: Returns the current size
"""

from typing import Optional, List
from PySide2.QtWidgets import QWidget

from foundry.gui.QSpinner.MultiSpinner import MultiSpinner, SpinnerAttributes
from foundry.game.Size import Size
from foundry.core.Observables.ObservableDecorator import ObservableDecorator
from foundry.gui.QCore.Action import Action


class SizeSpinner(MultiSpinner):
    """A spinner in charge of the keeping the size"""
    def __init__(self, parent: Optional[QWidget], size: Size = Size(0, 0)) -> None:
        MultiSpinner.__init__(self, parent, [SpinnerAttributes("Width", 0, 0xFF), SpinnerAttributes("Height", 0, 0xFF)])
        self.parent = parent
        self._size = size

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.parent}, {self.size})"

    def _update_changed_values(self):
        """Returns the changed values from the spinners"""
        self.values_changed_action.observer([spinner.value() for spinner in self.spinners])
        self._size = Size(self.spinners[0].value(), self.spinners[1].value())
        self.size_changed_action.observer(self.the_size)

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action("values_changed", ObservableDecorator(lambda value: value)),
            Action("size_changed", ObservableDecorator(lambda size: size)),
            Action("text_changed", ObservableDecorator(lambda text: text)),
        ]

    @property
    def the_size(self) -> Size:
        """The size we are tracking"""
        return self._size

    @the_size.setter
    def the_size(self, size: Size) -> None:
        self._size = size
        self.spinners[0].setValue(size.width)
        self.spinners[1].setValue(size.height)
        self._update_changed_values()
