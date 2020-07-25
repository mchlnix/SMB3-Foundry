"""
This module includes the RectSpinner
RectSpinner: A spinner that automatically keeps tracks of a Rect.
the_rect: The rect provided from the RectSpinner
"""

from typing import Optional
from PySide2.QtWidgets import QWidget, QSizePolicy, QVBoxLayout, QLayout
from PySide2.QtGui import Qt

from foundry.gui.QLabel import Label
from foundry.decorators.Observer import Observed
from foundry.gui.QSpinner.MultiSpinner import MultiSpinnerPanel
from foundry.gui.QSpinner.PositionSpinner import PositionSpinner
from foundry.gui.QSpinner.SizeSpinner import SizeSpinner
from foundry.game.Rect import Rect
from foundry.gui.QCore import MARGIN_TIGHT


class RectSpinner(QWidget):
    """A class for keeping track of a rect"""
    def __init__(self, parent: Optional[QWidget], name: str, rect: Rect = Rect(0, 0, 0, 0)) -> None:
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        layout = QVBoxLayout()
        layout.setContentsMargins(MARGIN_TIGHT, MARGIN_TIGHT, MARGIN_TIGHT, MARGIN_TIGHT)

        self.label = Label(self, name)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        self.position_spinner = MultiSpinnerPanel(self, "Position", PositionSpinner(self))
        layout.addWidget(self.position_spinner)
        self.size_spinner = MultiSpinnerPanel(self, "Size", SizeSpinner(self))
        layout.addWidget(self.size_spinner)

        self.setLayout(layout)

        self.action = Observed(
            lambda *_: Rect.from_size_and_position(
                self.size_spinner.spinner.the_size, self.position_spinner.spinner.position
            )
        )
        self.the_rect = rect
        self.size_spinner.add_observer(self.action)
        self.position_spinner.add_observer(self.action)
        self.action.attach(lambda rec: self.__setattr__("_rect", rec))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.parent}, {self.name}, {self.the_rect})"

    @property
    def the_rect(self) -> Rect:
        """The rect we are keeping track of"""
        return self._rect

    @the_rect.setter
    def the_rect(self, rect: Rect) -> None:
        self._rect = rect
        self.position_spinner.spinner.position = rect.abs_pos
        self.size_spinner.spinner.the_size = rect.abs_size
        self.action.notify(rect)
