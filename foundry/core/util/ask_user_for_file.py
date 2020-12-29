

from PySide2.QtWidgets import QFileDialog


def ask_user_for_file(caption: str, filter: str):
    """Asks the user for a file and returns the result"""
    return QFileDialog.getOpenFileName(None, caption=caption, filter=filter)[0]
