

from typing import Optional, List
from dataclasses import dataclass
from PySide2.QtWidgets import QWidget, QGridLayout
from PySide2.QtGui import Qt


from foundry.core.Observables.ObservableDecorator import ObservableDecorator

from foundry.core.Action.Action import Action
from foundry.gui.QCore.Tracker import AbstractActionObject

from foundry.gui.Custom.Block.Block import BlockWidget
from foundry.gui.QSpinner import Spinner
from foundry.gui.QSpinner.HexSpinner import HexSpinner
from foundry.gui.QWidget import Widget
from foundry.gui.QWidget.Panel import Panel


class BlockEditor(Widget, AbstractActionObject):
    """A spinner in charge of the keeping the position"""
    def __init__(self, parent: Optional[QWidget], block: BlockWidget) -> None:
        Widget.__init__(self, parent)
        AbstractActionObject.__init__(self)

        self.block = block
        self._set_up_layout()
        self._initialize_internal_observers()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.parent}, {self.spinners})"

    def _set_up_layout(self) -> None:
        """Returns the widgets layout"""
        self.spinners = []
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)

        top_left_spinner = HexSpinner(self, maximum=0xFF)
        grid.addWidget(top_left_spinner, 0, 0)

        top_right_spinner = HexSpinner(self, maximum=0xFF)
        grid.addWidget(top_right_spinner, 0, 2)

        grid.addWidget(self.block, 0, 1, 0, 1, Qt.AlignCenter)

        bottom_left_spinner = HexSpinner(self, maximum=0xFF)
        grid.addWidget(bottom_left_spinner, 1, 0)

        bottom_right_spinner = HexSpinner(self, maximum=0xFF)
        grid.addWidget(bottom_right_spinner, 1, 2)

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


