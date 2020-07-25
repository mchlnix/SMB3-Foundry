"""
This module includes the default implementation of a drop down AKA combo box
ComboBoxOption: The tuple for adding an combobox option with a action built in
ComboBox: The drop down with extended functionality
"""

from typing import Callable, Optional, List
from collections import namedtuple
from PySide2.QtWidgets import QComboBox, QWidget, QSizePolicy, QFormLayout

from foundry.gui.QCore import MARGIN_TIGHT
from foundry.gui.QLabel import Label
from foundry.decorators.Observer import Observed


ComboBoxOption = namedtuple("ComboBoxOption", "name action")


class ComboBox(QComboBox):
    """A default combobox with extended observer functionality"""
    def __init__(self, parent: Optional[QWidget], options: Optional[List[ComboBoxOption]] = None) -> None:
        super().__init__(parent)
        self.parent = parent
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setContentsMargins(MARGIN_TIGHT, MARGIN_TIGHT, MARGIN_TIGHT, MARGIN_TIGHT)

        self.action = Observed(lambda opt: opt)
        self.items_count = 0
        if options is not None:
            for option in options:
                self.add_item(option)
        self.currentIndexChanged.connect(self.action)

    def add_item(self, option: ComboBoxOption) -> None:
        """Adds an item to the drop down with an action"""
        self.addItem(option.name)
        index = self.items_count
        self.add_observer(lambda result: option.action() if result == index else result)
        self.items_count += 1

    def add_observer(self, observer: Callable) -> None:
        """Adds an observer to the value"""
        self.action.attach(observer)


class ComboBoxPanel(QWidget):
    """A tool button panel with a basic form layout"""
    def __init__(self, parent: Optional[QWidget], name: str, combo_box: ComboBox):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setContentsMargins(0, 0, 0, 0)

        self.parent = parent
        self.combo_box = combo_box
        self.add_observer = self.combo_box.add_observer
        self.add_item = self.combo_box.add_item
        panel_layout = QFormLayout()
        panel_layout.setContentsMargins(MARGIN_TIGHT, 0, MARGIN_TIGHT, 0)
        panel_layout.addRow(Label(self.parent, name), self.combo_box)
        self.setLayout(panel_layout)




