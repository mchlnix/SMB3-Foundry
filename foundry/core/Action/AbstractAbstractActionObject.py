from abc import abstractmethod
from typing import Optional, List

from PySide2.QtWidgets import QWidget

from foundry.core.Action import has_actions
from foundry.core.Action.Action import Action
from .ActionContainer import ActionContainer


class AbstractAbstractActionObject:
    def __init__(self, container: Optional[ActionContainer] = None) -> None:
        self.container = container

    def add_action(self, action: Action, force_name: Optional[str] = None) -> None:
        """Adds an action to the object"""
        self.container.add_action(action, force_name)

    def remove_action(self, name: str) -> None:
        """Removes an action to the object"""
        self.container.remove_action(name)

    @abstractmethod
    def steal_actions(self, container: ActionContainer):
