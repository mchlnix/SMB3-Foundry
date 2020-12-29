

from PySide2.QtWidgets import QMessageBox


def ask_user_to_proceed(parent, reason: str, additional_information: str):
    """Asks the user if we should continue"""
    return QMessageBox.warning(
        parent,
        reason,
        f"{additional_information}\n\nDo you want to proceed?",
        QMessageBox.No | QMessageBox.Yes,
        QMessageBox.No,
    )