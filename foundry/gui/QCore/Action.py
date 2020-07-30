

from typing import Optional, List
from abc import abstractmethod
from dataclasses import dataclass
from PySide2.QtWidgets import QWidget
from PySide2.QtCore import Signal

from foundry.core.Observables.ObservableDecorator import ObservableDecorator


def has_actions(action_object):
    """Raises an error if the action object does not have _actions"""
    if not hasattr(action_object, "_actions"):
        raise AttributeError(f"The object {action_object} does not have variable _actions")


@dataclass
class Action:
    """
    This class provides the basis for chaining actions together and making them inheritable
    name: The name of the action
    observer: The observer be called
    """
    name: str
    observer: ObservableDecorator

    @property
    def alt_name(self) -> str:
        """The alt name of the action"""
        return f"{self.name}_action"

    @classmethod
    def from_signal(cls, name: str, signal: Signal, pass_result: bool = True) -> "Action":
        """Makes an action from a signal"""
        if pass_result:
            observer = ObservableDecorator(lambda result: result)
        else:
            observer = ObservableDecorator(lambda *_: True)
        signal.connect(observer)
        return Action(name, observer)


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
        if not hasattr(action, "observer") or not hasattr(action, "alt_name"):
            raise AttributeError(f"{name} {action} is not an Action")
        name = name if name is not None else action.alt_name
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
