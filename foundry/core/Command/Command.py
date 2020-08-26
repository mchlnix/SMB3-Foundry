

from dataclasses import dataclass
from typing import Callable


@dataclass
class Command:
    """A group of actions that allow for doing and undoing the operation"""
    name: str
    do_action: Callable
    undo_action: Callable

    def __call__(self, *args, **kwargs) -> None:
        """Calls the observer as if we wrote self.observer(*args, **kwargs)"""
        self.do_action(*args, **kwargs)

    def do(self, *args, **kwargs) -> None:
        """Does the action"""
        self.do_action(*args, **kwargs)

    def undo(self, *args, **kwargs) -> None:
        """Undo the command"""
        self.undo_action(*args, **kwargs)

    @property
    def reference_name(self) -> str:
        """The alt name of the action"""
        return f"{self.name}_command"