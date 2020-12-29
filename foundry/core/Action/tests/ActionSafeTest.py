from typing import Callable

from foundry.core.Action.AbstractActionSafe import AbstractActionSafe


class ActionSafeTest(AbstractActionSafe):
    """A concrete implementation of ActionSafe used for testing"""
    def __init__(self, name: str, func: Callable, proceed: bool = False) -> None:
        AbstractActionSafe.__init__(self, name, func)
        self.proceed = proceed
        self.reason, self.additional_info = None, None

    def proceed_message(self, reason: str, additional_information: str) -> bool:
        """THe proceed message"""
        self.reason, self.additional_info = reason, additional_information
        return self.proceed
