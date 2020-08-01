

from typing import Optional, List
from PySide2.QtWidgets import QWidget, QLayout, QFormLayout

from foundry.gui.QCore import MARGIN_TIGHT
from foundry.gui.QCore.util import set_tight_size_policy
from foundry.gui.QLabel import Label
from foundry.core.Action import Action, AbstractActionWidget


class Panel(AbstractActionWidget):
    """A panel that inherits the widgets actions"""
    def __init__(self, parent: Optional[QWidget], name: str, element: AbstractActionWidget):
        self.parent = parent
        self.element = element
        QWidget.__init__(self, parent)
        self._set_size_policies()

        self.label = Label(self, name)
        self.setLayout(self._get_layout())

    def _get_layout(self) -> QLayout:
        """
        Configures the layout to be used as the panel's main layout
        :return: QLayout
        """
        layout = QFormLayout()
        layout.setContentsMargins(MARGIN_TIGHT, 0, MARGIN_TIGHT, 0)
        layout.addRow(self.label, self.element)
        return layout

    def _set_size_policies(self) -> None:
        """Sets the size policy and margin of the widget"""
        set_tight_size_policy(self)

    def get_actions(self) -> List[Action]:
        """Gets the actions for the panel"""
        self.steal_actions(default_name=self.element.default_name, action_object=self.element)
        return []


class ReversedPanel(Panel):
    """A panel with the label and widget reversed"""
    def _get_layout(self) -> QLayout:
        """
        Configures the layout to be used as the panel's main layout
        :return: QLayout
        """
        layout = QFormLayout()
        layout.setContentsMargins(MARGIN_TIGHT, 0, MARGIN_TIGHT, 0)
        layout.addRow(self.element, self.label)
        return layout
