from functools import partial

from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import QMessageBox

from foundry import github_issue_link, root_dir


def popup_crash_dialog(traceback: str):
    crash_dialog = QMessageBox()
    crash_dialog.setWindowTitle("Crash Report")

    traceback = traceback.replace(str(root_dir) + "/", "")
    crash_dialog.setText(
        "<p>An unexpected error occurred! Please contact the developers with the error below at:<br>"
        f'<a href="{github_issue_link}">{github_issue_link}</a></p>'
        f"<pre>{traceback}</pre>"
    )

    crash_dialog.addButton(QMessageBox.StandardButton.Close)

    copy_button = crash_dialog.addButton(QMessageBox.StandardButton.Close)
    copy_button.setText("Copy && Close")

    copy_traceback = partial(QClipboard().setText, "```\n" + traceback + "```")

    copy_button.clicked.connect(copy_traceback)

    crash_dialog.exec()
