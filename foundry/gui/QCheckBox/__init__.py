

from typing import List, Optional
from PySide2.QtWidgets import QCheckBox

from foundry.gui.QCore.util import DefaultSizePartial
from foundry.core.Action.Action import Action, AbstractActionObject


class CheckBox(QCheckBox, AbstractActionObject, DefaultSizePartial):
    """A generic spinner with extended functionality"""
    def __init__(self, parent, name : Optional[str] = ""):
        QCheckBox.__init__(self, parent, name)
        DefaultSizePartial.__init__(self)
        AbstractActionObject.__init__(self)
        self.parent = parent

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action.from_signal("state_changed", self.stateChanged),
        ]
