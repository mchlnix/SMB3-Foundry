"""
This module includes Action
This serves as the base implementation of an Action
"""

from typing import Callable, Any

from ..Action.Action import Action

from foundry.core.Observables.Observable import Observable


class State:
    """
    This class provides the basis for holding a state and being an action
    name: The name of the state
    state: The state of the object
    action_constructor: The action constructor of the object
    """
    name: str
    state: Any
    action: Action

    def __init__(self, name: str, state: Any, action_constructor: Callable) -> None:
        self.name = name
        self._state = state
        self.action = action_constructor(self.name, Observable())
        self.observer.attach_observer(lambda value: setattr(self, '_state', value))

    @property
    def state(self) -> Any:
        """The current state of the object"""
        return self._state

    @state.setter
    def state(self, state: Any) -> None:
        self._state = state
        self.action.observer(state)

    @property
    def observer(self) -> Observable:
        """A property to help provide similar action functionality"""
        return self.action.observer

    @property
    def reference_name(self) -> str:
        """The alt name of the action"""
        return f"{self.name}_state"
