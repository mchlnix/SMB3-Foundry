"""
This module includes Action
This serves as the base implementation of an Action
"""

from dataclasses import dataclass
from PySide2.QtCore import Signal

from foundry.core.Observables.Observable import Observable
from foundry.core.Observables.ObservableDecorator import ObservableDecorator


@dataclass
class Action:
    """
    This class provides the basis for chaining actions together and making them inheritable
    name: The name of the action
    observer: The observer be called
    """
    name: str
    observer: Observable

    def __call__(self, *args, **kwargs) -> None:
        """Calls the observer as if we wrote self.observer(*args, **kwargs)"""
        return self.observer(*args, **kwargs)

    @property
    def reference_name(self) -> str:
        """The alt name of the action"""
        return f"{self.name}_action"

    @classmethod
    def from_signal(cls, name: str, signal: Signal, pass_result: bool = True, observer_name: str = None) -> "Action":
        """Makes an action from a signal"""
        if pass_result:
            observer = ObservableDecorator(lambda result: result, observer_name)
        else:
            observer = ObservableDecorator(lambda *_: True, observer_name)
        signal.connect(observer)
        return Action(name, observer)
