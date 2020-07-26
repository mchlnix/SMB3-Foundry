"""
This module includes a radio button with extended functionality
"""

from typing import List, Optional
from PySide2.QtWidgets import QRadioButton, QWidget

from foundry.gui.QCore.util import DefaultSizePartial
from foundry.gui.QCore.Action import Action, AbstractActionObject


class RadioButton(QRadioButton, AbstractActionObject, DefaultSizePartial):
    """A generic radio button with extended functionality"""
    def __init__(self, parent: Optional[QWidget], name: Optional[str] = ""):
        QRadioButton.__init__(parent, name)
        DefaultSizePartial.__init__(self)
        AbstractActionObject.__init__(self)

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action.from_signal("clicked", self.clicked, False),
            Action.from_signal("pressed", self.pressed, False),
            Action.from_signal("released", self.released, False)
        ]
