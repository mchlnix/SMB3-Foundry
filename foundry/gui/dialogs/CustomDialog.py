"""Provide Foundry's shared base class for small Qt dialogs.

This module centralizes the dialog behavior that Foundry wants almost
everywhere: always-on-top windows, Escape-key dismissal, and one close hook
that subclasses can override to flush staged UI state before the dialog hides.
It is a small widget helper, but it defines a repeated GUI lifecycle boundary
used by many editor dialogs.

See Also
--------
foundry.gui.dialogs.AboutWindow
    Example dialog module that builds on this shared behavior.
"""

from PySide6.QtGui import QKeyEvent, Qt
from PySide6.QtWidgets import QDialog


class CustomDialog(QDialog):
    """Base dialog with Foundry's standard close behavior.

    Dialog subclasses inherit the always-on-top flag and the Escape-key close
    path. ``closeEvent`` delegates to ``on_exit`` so subclasses can persist or
    stage final UI state before the dialog is hidden.

    Parameters
    ----------
    parent : object
        Parent Qt widget that owns this object.
    title : str, optional
        Window or menu title.
    """

    def __init__(self, parent, title="Title"):
        """Create a standard Foundry dialog.

        The constructor applies the shared dialog policy up front: set the
        window title, keep the dialog above the editor shell, and leave the
        close-time state handling to ``on_exit`` for subclasses that need it.

        Parameters
        ----------
        parent : object
            Parent Qt widget that owns this object.
        title : str, optional
            Window or menu title.
        """
        super(CustomDialog, self).__init__(parent)

        self.setWindowTitle(title)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

    def keyPressEvent(self, event: QKeyEvent):
        """Close the dialog when Escape is pressed.


        Parameters
        ----------
        event : QKeyEvent
            Qt event delivered to the widget.
        """
        if event.key() == Qt.Key.Key_Escape:
            self.close()

    def on_exit(self):
        """Hide the dialog during close handling.

        Subclasses may override this to sync settings or commit staged state
        before delegating back here.
        """
        self.hide()

    def closeEvent(self, event):
        """Run Foundry dialog exit handling for a Qt close event.


        Parameters
        ----------
        event : object
            Qt event delivered to the widget.
        """
        self.on_exit()
