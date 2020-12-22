

from typing import Dict
from PySide2.QtWidgets import QAbstractButton

from foundry.core.Action.Action import Action
from foundry.gui.QCore.ExclusiveGroup import ExclusiveGroup


class ButtonGroupExclusive(ExclusiveGroup):
    """A group of buttons that are exclusive"""
    def __init__(self, buttons: Dict[str, QAbstractButton]):
        self.actions = [Action.from_signal(name, button.setChecked) for name, button in buttons.items()]
        super().__init__([action.observer for action in self.actions])


