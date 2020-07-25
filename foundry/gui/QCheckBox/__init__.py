

from typing import Callable, Optional
from PySide2.QtWidgets import QCheckBox, QFormLayout, QWidget, QSizePolicy

from foundry.gui.QLabel import Label
from foundry.decorators.Observer import Observed
from foundry.gui.QCore import MARGIN_TIGHT


class CheckBox(QCheckBox):
    """A generic spinner with extended functionality"""
    def __init__(self, parent, name):
        super().__init__(parent=parent, text=name)
        self.action = Observed(self.action)
        self.stateChanged.connect(self.action)

    def add_observer(self, observer: Callable) -> None:
        """Adds an observer to the value"""
        self.aciton.attach_observer(observer)

    def action(self, new_value: int, *_) -> int:
        """
        Extends the connect functionality from Qt
        """
        return new_value


class CheckboxPanel(QWidget):
    """A spinner panel with a basic form layout"""
    def __init__(self, parent: Optional[QWidget], name: str, checkbox: CheckBox):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        self.parent = parent
        self.checkbox = checkbox
        self.action = self.checkbox.action
        self.add_observer = self.checkbox.add_observer
        spinner_layout = QFormLayout()
        spinner_layout.setContentsMargins(MARGIN_TIGHT, MARGIN_TIGHT, MARGIN_TIGHT, MARGIN_TIGHT)
        spinner_layout.addRow(self.checkbox, Label(self.parent, name))
        self.setLayout(spinner_layout)
