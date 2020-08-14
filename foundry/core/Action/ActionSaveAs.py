

from typing import Callable
from PySide2.QtWidgets import QMessageBox

from .AbstractActionSelectFile import AbstractActionSelectFile
from ..util.ask_user_to_save_as import ask_user_to_save_as


class ActionSaveAs(AbstractActionSelectFile):
    """A generic implementation of an action for opening files"""
    def __init__(self, name: str, func: Callable, caption: str, file_filter: str) -> None:
        super().__init__(name, func)
        self.caption = caption
        self.file_filter = file_filter

    def get_file_path(self) -> str:
        """Returns the file path selected"""
        return ask_user_to_save_as(self.caption, self.file_filter)

    def invalid_file_warning(self, error: str, path: str) -> None:
        """The message provided to the user on an event that the file was invalid"""
        QMessageBox.warning(None, type(error).__name__, f"Cannot open file '{path}'.")