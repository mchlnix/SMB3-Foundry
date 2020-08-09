

from abc import abstractmethod
from typing import Callable

from .Action import Action
from .ActionLock import ActionLock
from .AbstractActionSafe import AbstractActionSafe
from .ActionSafe import ActionSafe

from ..Requirable.Requirable import Requirable

from ..Observables.ObservableDecorator import ObservableDecorator


class AbstractActionSelectFile(Action):
    """An interface to select a file with multiple safety checks"""
    warning_action: AbstractActionSafe
    observable: ActionLock

    def __init__(self, name: str, action: Callable = ActionSafe) -> None:
        """
        :param name: The name of the action
        :param action: The constructor for an action for an AbstractActionSafe
        """
        self.name = name
        self.file_selected_observer = ObservableDecorator(lambda path: path)
        self.warning_action = action(f"{self.name}_warning", self.handle_file_path)
        self.observable = ActionLock(f"{self.name}_lock", self.warning_action.observable, Requirable())

    def attach_observer(self, observer: Callable) -> None:
        """A quick method for adding an observer to when a file is selected"""
        self.file_selected_observer.attach_observer(observer)

    def attach_warning(self, requirement: Callable):
        """Adds a warning for the user"""
        self.warning_action.warning_checks.attach_requirement(requirement)

    def attach_requirement(self, requirement: Callable):
        """Adds a requirement to the action lock"""
        self.observable.requirable.attach_requirement(requirement)

    def handle_file_path(self):
        """Handles getting the file path"""
        path = self.get_file_path()
        if not path:
            return False

        try:
            self.file_selected_observer(path)
        except IOError as error:
            self.invalid_file_warning(error, path)
            return False
        return True

    @abstractmethod
    def get_file_path(self) -> str:
        """Returns the file path selected"""

    @abstractmethod
    def invalid_file_warning(self, error: str, path: str) -> None:
        """The message provided to the user on an event that the file was invalid"""
