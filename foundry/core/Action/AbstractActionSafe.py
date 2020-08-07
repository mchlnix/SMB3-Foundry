"""
An action that provides an additional check for if it is 'safe' to execute
"""

from typing import Callable
from abc import abstractmethod

from .Action import Action
from ..Observables.ObservableDecorator import ObservableDecorator
from ..Requirable.RequirableSmartDecorator import SmartRequirableDecorator


class AbstractActionSafe(Action):
    """A action that provides an additional check for if it is 'safe' to execute"""
    def __init__(self, name: str, func: Callable) -> None:
        self.name = name

        def no_warnings_found():
            """The function ran when no warnings are found"""
            return True, "", ""

        self.warning_checks = SmartRequirableDecorator(no_warnings_found)

        def action(*args, **kwargs):
            """The action of the object"""
            safe, reason, additional_info = self.warning_checks()
            if not safe and not self.proceed_message(reason, additional_info):
                return False
            return func(*args, **kwargs)

        self.observable = ObservableDecorator(action)

    @abstractmethod
    def proceed_message(self, reason: str, additional_information: str) -> bool:
        """The message if something is not safe"""
