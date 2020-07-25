"""
This module contains the base functionality for spinners
Spinner: A generic spinner with extended functionality
SpinnerPanel: A generic spinner with a label
"""

from typing import Optional
from PySide2.QtWidgets import QWidget, QSpinBox, QSizePolicy, QFormLayout

from foundry.decorators.Observer import Observed
from foundry.gui.QCore import MARGIN_TIGHT, LABEL_TINY
from foundry.gui.QLabel import Label


class Spinner(QSpinBox):
    """A generic spinner with extended functionality"""
    def __init__(self, parent, minimum=0, maximum=0xFFFFFF):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
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


class SpinnerPanel(QWidget):
    """A spinner panel with a basic form layout"""
    def __init__(self, parent: Optional[QWidget], name: str, spinner: Spinner):
        super(SpinnerPanel, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setContentsMargins(0, 0, 0, 0)

        self.parent = parent
        self.spinner = spinner
        self.on_text_change = self.spinner.on_text_change
        self.on_value_change = self.spinner.on_value_change
        spinner_layout = QFormLayout()
        spinner_layout.setContentsMargins(MARGIN_TIGHT, 0, MARGIN_TIGHT, 0)
        spinner_layout.addRow(Label(self, name), self.spinner)
        self.setLayout(spinner_layout)







