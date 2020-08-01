"""
This module contains the base functionality for spinners
Spinner: A generic spinner with extended functionality
"""

from typing import List
from PySide2.QtWidgets import QLineEdit

from foundry.gui.QCore.util import DefaultSizePartial
from foundry.core.Action.Action import Action, AbstractActionObject


class LineEdit(QLineEdit, AbstractActionObject, DefaultSizePartial):
    """A generic spinner with extended functionality"""

    def __init__(self, parent, text):
        QLineEdit.__init__(self, parent)
        DefaultSizePartial.__init__(self)
        AbstractActionObject.__init__(self)
        self.parent = parent

        self.setText(text)

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action.from_signal("text_edited", self.textEdited),
            Action.from_signal("text_changed", self.textChanged),
        ]

    @property
    def the_text(self):
        """Returns the text of the line editor as a property"""
        return self.text()
