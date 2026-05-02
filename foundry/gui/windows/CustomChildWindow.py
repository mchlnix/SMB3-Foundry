"""Base window behavior for reusable Foundry child tools.

This module provides :class:`CustomChildWindow`, a small ``QMainWindow``
subclass used by inspector-style tools that should stay alive between shows.
It centralizes the "hide instead of close" behavior that lets menu actions and
toolbar commands reopen an existing child window without rebuilding its UI
state from scratch. Read the concrete viewer and inspector windows next to see
how individual tools layer their own controls on top of this lifecycle.
"""

from PySide6.QtGui import QKeyEvent, Qt
from PySide6.QtWidgets import QMainWindow


class CustomChildWindow(QMainWindow):
    """Small always-on-top utility window.

    Foundry uses this base for inspector-style windows that should hide, rather
    than close, when Escape is pressed. That keeps helper windows such as
    viewers and inspectors available without making users recreate them after
    every quick dismissal. Child windows inherit a common lifecycle from this
    base: the main window can keep one instance around, users can temporarily
    dismiss it with Escape, and later actions can show the same window again
    with its prior UI state intact.

    Parameters
    ----------
    parent : QWidget | None
        Parent Qt widget that owns this object.
    title : str, optional
        Window or menu title.

    Notes
    -----
    The class deliberately favors hiding over destruction. That matches how
    Foundry treats inspector windows elsewhere in the UI and avoids rebuilding
    heavier viewers every time the user closes one casually.
    """

    def __init__(self, parent, title="Title"):
        """Create a utility window.

        The constructor establishes the shared child-window lifecycle used by
        Foundry inspectors: the main window owns the instance, the window keeps
        an always-on-top presentation, and later open actions can reshow the
        same widget without reconstructing its contents. Subclasses only need
        to add their own controls after this common title and window-flag setup
        is in place.

        Parameters
        ----------
        parent : QWidget | None
            Parent Qt widget that owns this object.
        title : str, optional
            Window or menu title.
        """
        super(CustomChildWindow, self).__init__(parent)

        self.setWindowTitle(title)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

    def keyPressEvent(self, event: QKeyEvent):
        """Hide the window when Escape is pressed.

        Parameters
        ----------
        event : QKeyEvent
            Qt event delivered to the widget.
        """
        if event.key() == Qt.Key.Key_Escape:
            self.on_exit()

    def on_exit(self):
        """Hide the utility window."""
        self.hide()
