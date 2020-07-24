"""
This module contains the SizeSpinner
SizeSpinner: A spinner that has two spinners for width and height.  Has an update routine that returns a Size
action_size: An observer that returns the new Size
the_size: Returns the current size
"""

from typing import Optional, Callable
from PySide2.QtWidgets import QWidget

from foundry.gui.QSpinner.MultiSpinner import MultiSpinner, SpinnerAttributes
from foundry.game.Size import Size
from foundry.decorators.Observer import Observed


class SizeSpinner(MultiSpinner):
    """A spinner in charge of the keeping the size"""
    def __init__(self, parent: Optional[QWidget], size: Size = Size(0, 0)) -> None:
        super().__init__(parent, [SpinnerAttributes("Width", 0, 0xFF), SpinnerAttributes("Height", 0, 0xFF)])
        self.parent = parent
        self.action_size = Observed(lambda siz: Size(siz[0], siz[1]))
        self.the_size = size
        self.action.attach(self.action_size)
        self.action_size.attach(lambda siz: self.__setattr__("_size", siz))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.parent}, {self.size})"

    @property
    def the_size(self) -> Size:
        """The size we are tracking"""
        return self._size

    @the_size.setter
    def the_size(self, size: Size) -> None:
        self._size = size
        self.spinners[0].spinner.setValue(size.width)
        self.spinners[1].spinner.setValue(size.height)
        self.action_size.notify(size)  # update observers

    def add_observer(self, observer: Callable):
        """Adds an observer"""
        self.action_size.attach(observer)
