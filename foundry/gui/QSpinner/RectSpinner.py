"""
This module includes the RectSpinner
RectSpinner: A spinner that automatically keeps tracks of a Rect.
the_rect: The rect provided from the RectSpinner
"""

from typing import Optional, List
from PySide2.QtWidgets import QWidget, QGridLayout, QVBoxLayout
from PySide2.QtGui import Qt

from foundry.gui.QLabel import Label
from foundry.core.ObservableDecorator import Observable
from foundry.gui.QWidget import Widget
from foundry.gui.QCore.Action import Action, AbstractActionObject
from foundry.gui.QSpinner.PositionSpinner import PositionSpinner
from foundry.gui.QSpinner.SizeSpinner import SizeSpinner
from foundry.game.Rect import Rect


class RectSpinner(Widget, AbstractActionObject):
    """A class for keeping track of a rect"""
    def __init__(self, parent: Optional[QWidget], name: str, rect: Rect = Rect(0, 0, 0, 0)) -> None:
        Widget.__init__(self, parent)
        AbstractActionObject.__init__(self)
        self.name = name
        self._rect = rect

        self._set_up_layout()
        self._initialize_internal_observers()
        self.rect_changed_action.observer.attach(lambda rect: print(rect))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.parent}, {self.name}, {self.the_rect})"

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action("rect_changed", Observable(lambda rect: rect)),
        ]

    def _initialize_internal_observers(self) -> None:
        """Initializes internal observers for special events"""
        self.position_spinner.position_changed_action.observer.attach(lambda *_: self._update_rect())
        self.size_spinner.size_changed_action.observer.attach(lambda *_: self._update_rect())

    def _update_rect(self) -> None:
        self._rect = Rect.from_size_and_position(self.size_spinner.the_size, self.position_spinner.position)
        self.rect_changed_action.observer(self.the_rect)

    def _set_up_layout(self) -> None:
        """Returns the widgets layout"""
        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)

        self.label = Label(self, self.name)
        self.label.setAlignment(Qt.AlignCenter)

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.position_spinner = PositionSpinner(self, self.the_rect.abs_pos)
        self.size_spinner = SizeSpinner(self, self.the_rect.abs_size)
        layout.setDefaultPositioning(2, Qt.Horizontal)
        layout.addWidget(Label(self, "Position"))
        layout.addWidget(self.position_spinner)
        layout.addWidget(Label(self, "Size"))
        layout.addWidget(self.size_spinner)

        vbox.addWidget(self.label)
        vbox.addLayout(layout)
        self.setLayout(vbox)

    @property
    def the_rect(self) -> Rect:
        """The rect we are keeping track of"""
        return self._rect

    @the_rect.setter
    def the_rect(self, rect: Rect) -> None:
        self._rect = rect
        self._update_rect()
