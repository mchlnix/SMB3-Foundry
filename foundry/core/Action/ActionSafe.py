

from .AbstractActionSafe import AbstractActionSafe
from ..util.ask_user_to_proceed import ask_user_to_proceed


class ActionSafe(AbstractActionSafe):
    """A default implementation of AbstractActionSafe"""
    def proceed_message(self, reason: str, additional_information: str) -> bool:
        """The message if something is not safe"""
        return ask_user_to_proceed(None, reason, additional_information)
