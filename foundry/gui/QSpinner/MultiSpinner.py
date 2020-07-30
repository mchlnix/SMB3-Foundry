"""
This module contains the classes to combine or stack spinners together easily
SpinnerAttribute: A class to easily prefab spinners
MultiSpinner: Creates multiple spinners as one widget
MultiSpinnerPanel: Creates multiple spinner pannels as one widget
"""

from typing import Optional, List
from dataclasses import dataclass
from PySide2.QtWidgets import QWidget, QGridLayout
from PySide2.QtGui import Qt

from . import Spinner
from foundry.core.Observables.ObservableDecorator import ObservableDecorator
from foundry.gui.QWidget import Widget
from foundry.gui.QWidget.Panel import Panel
from foundry.gui.QCore.Action import Action, AbstractActionObject


@dataclass
class SpinnerAttributes:
    """Spinner attributes for quick creation"""
    name: str
    min: int = 0
    max: int = 0xFFFFFF


class MultiSpinner(Widget, AbstractActionObject):
    """A spinner in charge of the keeping the position"""
    def __init__(self, parent: Optional[QWidget], spinners: List[SpinnerAttributes]) -> None:
        Widget.__init__(self, parent)
        AbstractActionObject.__init__(self)

        self._set_up_layout(spinners)
        self._initialize_internal_observers()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.parent}, {self.spinners})"

    def _set_up_layout(self, spinners: List[SpinnerAttributes]) -> None:
        """Returns the widgets layout"""
        self.spinners = []
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setDefaultPositioning(len(spinners), Qt.Horizontal)

        for idx, spinner in enumerate(spinners):
            spin = Spinner(self, spinner.min, spinner.max)
            self.spinners.append(spin)
            grid.addWidget(Panel(self, spinner.name, spin))
        self.setLayout(grid)

    def _initialize_internal_observers(self) -> None:
        """Initializes internal observers for special events"""
        for spinner in self.spinners:
            spinner.value_changed_action.observer.attach_observer(lambda *_: self._update_changed_values())
            spinner.text_changed_action.observer.attach_observer(lambda *_: self._update_text_values())

    def _update_changed_values(self):
        """Returns the changed values from the spinners"""
        self.values_changed_action.observer([spinner.value() for spinner in self.spinners])

    def _update_text_values(self):
        """Returns the changed text from the spinners"""
        self.text_changed_action.observer([spinner.text() for spinner in self.spinners])

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action("values_changed", ObservableDecorator(lambda palette_set: palette_set)),
            Action("text_changed", ObservableDecorator(lambda palette_set: palette_set)),
        ]
