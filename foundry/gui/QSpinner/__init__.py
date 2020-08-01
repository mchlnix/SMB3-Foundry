"""
This module contains the base functionality for spinners
Spinner: A generic spinner with extended functionality
SpinnerPanel: A generic spinner with a label
"""

from typing import Optional, List
from PySide2.QtWidgets import QSpinBox, QWidget

from foundry.gui.QCore.util import DefaultSizePartial
from foundry.core.Action.Action import Action, AbstractActionObject


class Spinner(QSpinBox, AbstractActionObject, DefaultSizePartial):
    """A generic spinner with extended functionality"""
    def __init__(self, parent: Optional[QWidget], minimum=0, maximum=0xFFFFFF):
        QSpinBox.__init__(self, parent)
        AbstractActionObject.__init__(self)
        DefaultSizePartial.__init__(self)
        self.parent = parent

        self.setRange(minimum, maximum)

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action.from_signal("value_changed", self.valueChanged),
            Action.from_signal("text_changed", self.textChanged),
        ]
