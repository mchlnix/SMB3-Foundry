"""
This module includes a radio button with extended functionality
"""

from typing import Callable, Optional
from PySide2.QtWidgets import QRadioButton, QFormLayout, QWidget, QSizePolicy

from foundry.gui.QLabel import Label
from foundry.decorators.Observer import Observed


class RadioButton(QRadioButton):
    """A generic radio button with extended functionality"""
    def __init__(self, parent: Optional[QWidget], name: Optional[str] = ""):
        super().__init__(parent=parent, text=name)
        self.action = Observed(self.action)
        self.clicked.connect(self.action)

    def add_observer(self, observer: Callable) -> None:
        """Adds an observer to the value"""
        self.aciton.attach_observer(observer)

    def action(self, new_value: int, *_) -> int:
        """
        Extends the connect functionality from Qt
        """
        return new_value


class RadioButtonPanel(QWidget):
    """A radio button panel with a basic form layout"""
    def __init__(self, parent: Optional[QWidget], name: str, button: RadioButton):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.parent = parent
        self.button = button
        self.action = self.button.action
        self.add_observer = self.button.add_observer
        panel_layout = QFormLayout()
        panel_layout.addRow(self.button, Label(self.parent, name))
        self.setLayout(panel_layout)
