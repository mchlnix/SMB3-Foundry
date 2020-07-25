"""
This module contains the classes to combine or stack spinners together easily
SpinnerAttribute: A class to easily prefab spinners
MultiSpinner: Creates multiple spinners as one widget
MultiSpinnerPanel: Creates multiple spinner pannels as one widget
"""

from typing import Optional, Callable, List
from dataclasses import dataclass
from PySide2.QtWidgets import QWidget, QSizePolicy, QGridLayout, QLayout
from PySide2.QtGui import Qt

from foundry.gui.QLabel import Label
from foundry.gui.QSpinner import Spinner, SpinnerPanel
from foundry.decorators.Observer import Observed
from foundry.gui.QCore import MARGIN_TIGHT


@dataclass
class SpinnerAttributes:
    """Spinner attributes for quick creation"""
    name: str
    min: int = 0
    max: int = 0xFFFFFF


class MultiSpinner(QWidget):
    """A spinner in charge of the keeping the position"""
    def __init__(self, parent: Optional[QWidget], spinners: List[SpinnerAttributes]) -> None:
        super().__init__(parent)
        self.parent = parent

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.grid = QGridLayout()
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setDefaultPositioning(len(spinners), Qt.Horizontal)
        self.spinners = []
        self.action = Observed(lambda *_: [spinner.spinner.value() for spinner in self.spinners])
        for idx, spinner in enumerate(spinners):
            spin = SpinnerPanel(self, spinner.name, Spinner(self, spinner.min, spinner.max))
            spin.on_value_change.attach(self.action)
            self.spinners.append(spin)
            self.grid.addWidget(spin)
            self.grid.setColumnStretch(idx, 1)
        self.setLayout(self.grid)

    def add_observer(self, observer: Callable):
        """Adds an observer"""
        self.action.attach(observer)


class MultiSpinnerPanel(QWidget):
    """A spinner panel with a basic form layout"""
    def __init__(self, parent: Optional[QWidget], name: str, spinner: MultiSpinner):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setContentsMargins(0, 0, 0, 0)

        self.parent = parent
        self.spinner = spinner
        self.action = self.spinner.action
        self.add_observer = self.spinner.add_observer
        spinner_layout = QGridLayout()
        spinner_layout.setContentsMargins(0, MARGIN_TIGHT, 0, MARGIN_TIGHT)
        spinner_layout.setDefaultPositioning(2, Qt.Horizontal)
        label = Label(self, name)
        label.setFixedWidth(80)
        spinner_layout.addWidget(label)
        spinner_layout.addWidget(self.spinner)

        self.setLayout(spinner_layout)
