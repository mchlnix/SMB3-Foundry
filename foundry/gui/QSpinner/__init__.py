"""
This module contains the base functionality for spinners
Spinner: A generic spinner with extended functionality
"""

from PySide2.QtWidgets import QSpinBox

from foundry.decorators.Observer import Observed


class Spinner(QSpinBox):
    """A generic spinner with extended functionality"""
    def __init__(self, parent, minimum=0, maximum=0xFFFFFF):
        super(Spinner, self).__init__(parent)
        self.on_text_change = Observed(self.on_text_change)
        self.textChanged.connect(self.on_text_change)
        self.on_value_change = Observed(self.on_value_change)
        self.valueChanged.connect(self.on_value_change)
        self.parent = parent
        self.setRange(minimum, maximum)

    def on_text_change(self, new_text: str, *_) -> str:
        """
        Extends the connect functionality from Qt
        """
        return new_text

    def on_value_change(self, new_value: int, *_) -> int:
        """
        Extends the connect functionality from Qt
        """
        return new_value
