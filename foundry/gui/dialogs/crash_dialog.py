"""Display crash reports and copyable traceback text.

This module owns the last-resort crash dialog shown after an unexpected
exception reaches the GUI boundary. It strips local repository prefixes from
the traceback before display, links users to the project issue tracker, and
lets the same sanitized traceback be copied as a fenced Markdown block.
"""

from functools import partial

from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import QMessageBox

from foundry import github_issue_link, root_dir
from foundry.gui.localization import tr


def popup_crash_dialog(traceback: str):
    """Show an unexpected-error dialog for a sanitized traceback.

    The Qt dialog is display-only: it does not persist Foundry crash state or
    mutate the active editor model. Its only side effect is copying the
    sanitized traceback to the clipboard when the user chooses the
    copy-and-close button. The text remains localized UI copy, while the
    traceback payload remains the original diagnostic data with local path
    prefixes removed.

    Parameters
    ----------
    traceback : str
        Exception traceback to display and optionally copy.
    """
    crash_dialog = QMessageBox()
    crash_dialog.setWindowTitle(tr("Common", "crash_report", "Crash Report"))

    traceback = traceback.replace(str(root_dir) + "/", "")
    crash_dialog.setText(
        tr(
            "Common",
            "error.unexpected_crash_html",
            '<p>An unexpected error occurred! Please contact the developers with the error below at:<br><a href="{issue_link}">{issue_link}</a></p><pre>{traceback}</pre>',
        ).format(issue_link=github_issue_link, traceback=traceback)
    )

    crash_dialog.addButton(QMessageBox.StandardButton.Close)

    copy_button = crash_dialog.addButton(QMessageBox.StandardButton.Close)
    copy_button.setText(tr("Common", "copy_close", "Copy && Close"))

    copy_traceback = partial(QClipboard().setText, "```\n" + traceback + "```")

    copy_button.clicked.connect(copy_traceback)

    crash_dialog.exec()
