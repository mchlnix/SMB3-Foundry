"""
This module includes the default implementation of a drop down AKA combo box
ComboBoxOption: The tuple for adding an combobox option with a action built in
ComboBox: The drop down with extended functionality
"""

from typing import Optional, List
from collections import namedtuple
from PySide2.QtWidgets import QComboBox, QWidget

from foundry.gui.QCore.util import set_tight_size_policy
from foundry.core.Action import Action, AbstractActionObject


ComboBoxOption = namedtuple("ComboBoxOption", "name action")


class ComboBox(QComboBox, AbstractActionObject):
    """A default combobox with extended observer functionality"""
    def __init__(self, parent: Optional[QWidget], options: Optional[List[ComboBoxOption]] = None) -> None:
        QComboBox.__init__(self, parent)
        AbstractActionObject.__init__(self)
        self.parent = parent

        self._set_size_policies()

        self.items_count = 0
        if options is not None:
            for option in options:
                self.add_item(option)

    def add_item(self, option: ComboBoxOption) -> None:
        """Adds an item to the drop down with an action"""
        self.addItem(option.name)
        index = self.items_count
        self.index_changed_action.observer.attach_observer(lambda result: option.action() if result == index else result)
        self.items_count += 1

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action.from_signal("index_changed", self.currentIndexChanged),
        ]

    def _set_size_policies(self):
        """Sets the size policy and margin of the widget"""
        set_tight_size_policy(self)




