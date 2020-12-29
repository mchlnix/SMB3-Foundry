

from PySide2.QtWidgets import QFileDialog


def ask_user_to_save_as(caption: str, filter: str):
    """Asks the user for a file and returns the result"""
    return QFileDialog.getSaveFileName(None, caption=caption, filter=filter)[0]
