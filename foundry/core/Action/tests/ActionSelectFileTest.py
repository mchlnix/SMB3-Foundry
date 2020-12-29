

from foundry.core.Action.AbstractActionSelectFile import AbstractActionSelectFile
from foundry.core.Action.tests.ActionSafeTest import ActionSafeTest


class ActionSelectFileTest(AbstractActionSelectFile):
    """A concrete implementation of ActionSelectFile used for testing"""
    warning_action: ActionSafeTest

    def __init__(self, name: str, path: str):
        AbstractActionSelectFile.__init__(self, name, ActionSafeTest)
        self.path = path
        self.error = False

    def get_file_path(self) -> str:
        """Returns the file's path"""
        return self.path

    def invalid_file_warning(self, error: str, path: str) -> None:
        """The message provided to the user on an event that the file was invalid"""
        self.error = True

