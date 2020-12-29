"""
This module includes Event
This serves as the base implementation of an Event
"""

from typing import Callable
from dataclasses import dataclass


@dataclass
class Event:
    """
    This class provides the basis for connecting simple events together
    name: The name of the event
    function: The function be called
    """
    name: str
    function: Callable

    @property
    def reference_name(self) -> str:
        """The alt name of the action"""
        return f"{self.name}_event"
