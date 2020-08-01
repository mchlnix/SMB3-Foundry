from abc import abstractmethod
from typing import Optional, List

from PySide2.QtWidgets import QWidget

from foundry.core.Action import has_actions
from foundry.core.Action.Action import Action


class AbstractActionObject:
    """
    This class provides the basis for automatically predefining actions for a class
    """
    default_name = "default"

    def __init__(self) -> None:
        self._actions = {}
        for action in self.get_actions():
            self.add_action(action)

    def add_action(self, action: Action, name: Optional[str] = None) -> None:
        """Adds an action"""
        if not hasattr(action, "observer") or not hasattr(action, "reference_name"):
            raise AttributeError(f"{name} {action} is not an Action")
        name = name if name is not None else action.reference_name
        self._actions[name] = action
        setattr(self, name, action)  # sets the class variable reflectively

    @abstractmethod
    def get_actions(self) -> List[Action]:
        """The predefined actions to create"""

    def steal_actions(self, action_object: "AbstractActionObject", default_name: Optional[str] = None) -> None:
        """Steals another action object's actions"""
        has_actions(action_object)

        default_name = default_name if default_name is not None else action_object.default_name
        for name, action in action_object._actions.items():
            if name in self._actions:
                self.steal_action(name, action_object, default_name)
            else:
                self.steal_action(name, action_object)

    def steal_action(self, action_name: str, action_object: "AbstractActionObject", prefix: Optional[str] = ""):
        """Steals a single action from an action object"""
        has_actions(action_object)
        if action_name not in action_object._actions:
            raise KeyError(f"The action {action_name} does not exist in {action_object}")
        self.add_action(action_object._actions[action_name], f"{prefix}_{action_name}")


class AbstractActionWidget(QWidget, AbstractActionObject):
    """This class acts as a QWidget and keeps all the features of an abstract action object"""
    def __init__(self, parent: Optional[QWidget]) -> None:
        QWidget.__init__(self, parent)
        AbstractActionObject.__init__(self)