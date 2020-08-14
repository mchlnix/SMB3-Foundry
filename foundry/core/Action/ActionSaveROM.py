

from PySide2.QtWidgets import QMessageBox

from foundry.game.File import ROM
from .AbstractActionSelectFile import AbstractActionSelectFile


class ActionSaveROM(AbstractActionSelectFile):
    """A generic implementation of an action for saving the rom"""
    def get_file_path(self) -> str:
        """Returns the file path selected"""
        return ROM().path

    def invalid_file_warning(self, error: str, path: str) -> None:
        """The message provided to the user on an event that the file was invalid"""
        QMessageBox.warning(None, type(error).__name__, f"Cannot open file '{path}'.")