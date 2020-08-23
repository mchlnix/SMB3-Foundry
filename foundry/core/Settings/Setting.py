

from typing import Callable, Any

from ..State.State import State


class Setting(State):
    """A state that has a receiver to keep a copy of the setting's state for other actions"""

    def __init__(self, name: str, state: Any, receiver: Callable, action_constructor: Callable) -> None:
        super().__init__(name, state, action_constructor)
        self.observer.attach_observer(lambda value: receiver(value))

    @property
    def reference_name(self) -> str:
        """The alt name of the setting"""
        return f"{self.name}_setting"
