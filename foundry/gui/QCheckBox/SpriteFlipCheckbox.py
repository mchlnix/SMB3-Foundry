"""
This module provides a way to easily keep track of sprite mirroring
SpriteFlipCheckbox: A class that handles both horizontal and vertical flipping
"""

from typing import Optional
from PySide2.QtWidgets import QWidget

from .MultiCheckbox import MultiCheckbox


class SpriteFlipCheckbox(MultiCheckbox):
    """A spinner in charge of the keeping the position"""
    def __init__(self, parent: Optional[QWidget], h_flip: bool = False, v_flip: bool = False) -> None:
        MultiCheckbox.__init__(self, parent, ["Flip X", "Flip Y"])
        self.parent = parent
        self.horizontal_flip = h_flip
        self.vertical_flip = v_flip

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.parent}, {self._horizontal_flip}, {self._vertical_flip})"

    @property
    def horizontal_flip(self) -> bool:
        """Returns the horizontal flip"""
        return self._horizontal_flip

    @horizontal_flip.setter
    def horizontal_flip(self, flip: bool) -> None:
        self._horizontal_flip = flip
        self.checkboxes[0].setChecked(flip)
        self._update_changed_values()

    @property
    def vertical_flip(self) -> bool:
        """Returns the vertical flip"""
        return self._horizontal_flip

    @vertical_flip.setter
    def vertical_flip(self, flip: bool) -> None:
        self._vertical_flip = flip
        self.checkboxes[1].setChecked(flip)
        self._update_changed_values()
