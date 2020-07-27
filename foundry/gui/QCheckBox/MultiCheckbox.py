"""
This module contains the classes to combine or stack checkboxes together easily
MultiCheckbox: Creates multiple spinners as one widget
"""

from typing import Optional, List
from PySide2.QtWidgets import QWidget, QGridLayout
from PySide2.QtGui import Qt

from . import CheckBox
from foundry.decorators.Observer import Observed
from foundry.gui.QWidget import Widget
from foundry.gui.QWidget.Panel import Panel
from foundry.gui.QCore.Action import Action, AbstractActionObject


class MultiCheckbox(Widget, AbstractActionObject):
    """A spinner in charge of the keeping the position"""
    def __init__(self, parent: Optional[QWidget], names: List[str]) -> None:
        Widget.__init__(self, parent)
        AbstractActionObject.__init__(self)

        self._set_up_layout(names)
        self._initialize_internal_observers()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.parent}, {self.checkboxes})"

    def _set_up_layout(self, names: List[str]) -> None:
        """Returns the widgets layout"""
        self.checkboxes = []
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setDefaultPositioning(len(names), Qt.Horizontal)

        for idx, name in enumerate(names):
            spin = CheckBox(self)
            self.checkboxes.append(spin)
            grid.addWidget(Panel(self, name, spin))
        self.setLayout(grid)

    def _initialize_internal_observers(self) -> None:
        """Initializes internal observers for special events"""
        for checkbox in self.checkboxes:
            checkbox.state_changed_action.observer.attach(lambda *_: self._update_changed_values())

    def _update_changed_values(self):
        """Returns the changed values from the spinners"""
        self.values_changed_action.observer([checkbox.checkState() for checkbox in self.checkboxes])

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action("values_changed", Observed(lambda palette_set: palette_set)),
        ]
