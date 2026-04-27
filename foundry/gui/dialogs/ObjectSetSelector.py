"""Prompt for the SMB3 object set when a workflow needs one immediate choice.

This module owns the small modal selector used by new-level and similar flows
that need a single object-set decision before more editor state can be built.
It intentionally returns a compact integer result instead of a longer-lived
settings object so callers can feed the choice straight into level creation.

See Also
--------
foundry.gui.dialogs.LevelHeaderEditor
    Edits the next-area object-set field after a level already exists.
foundry.gui.dialogs.level_selector.LevelSelector
    Broader level-picking workflow that also exposes object-set information.
"""

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from foundry.gui import OBJECT_SET_ITEMS


class ObjectSetSelector(QDialog):
    """Ask the user which SMB3 object set a new level should use.

    Foundry uses this dialog when a workflow needs one object-set choice and
    the result should come back immediately as an integer rather than through a
    longer-lived settings surface.

    Parameters
    ----------
    parent : QDialog | None, optional
        Parent Qt widget that owns this object.

    Attributes
    ----------
    cancel_button : QPushButton
        Button that rejects the dialog.
    object_set_dropdown : QComboBox
        Dropdown containing selectable object sets.
    ok_button : QPushButton
        Button that accepts the selected object set.
    result : int
        One-based object set chosen by the user.

    Notes
    -----
    The dialog warns that the object set cannot be changed later because object
    set selection determines the level's available object definitions and theme.
    """

    def __init__(self, parent=None):
        """Build the modal object-set selection dialog.

        Construction creates the explanatory label, the constrained object-set
        dropdown, and the accept or reject buttons that collapse the user's
        choice into one integer result. The dialog therefore acts as a short
        staging step at the start of level-creation workflows: callers pause
        just long enough to collect the object-set choice, then continue
        building the new level from that selection.

        Parameters
        ----------
        parent : QDialog | None, optional
            Parent Qt widget that owns this object.
        """
        super(ObjectSetSelector, self).__init__(parent)

        self.setWindowTitle("Object Set Selector")
        self.setModal(True)

        self.result = 1

        layout = QVBoxLayout(self)

        description = QLabel("Choose the object set for this new level.\nThis cannot be changed afterwards.\n")
        layout.addWidget(description)

        self.object_set_dropdown = QComboBox()
        self.object_set_dropdown.addItems(OBJECT_SET_ITEMS[1:-1])
        layout.addWidget(self.object_set_dropdown)

        self.ok_button = QPushButton("Ok")
        self.ok_button.clicked.connect(self.on_button)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.on_button)

        button_group = QHBoxLayout()
        button_group.addWidget(self.ok_button)
        button_group.addWidget(self.cancel_button)

        layout.addLayout(button_group)

    def on_button(self):
        """Accept or reject the dialog based on the clicked button."""
        if self.sender() is self.ok_button:
            self.result = self.object_set_dropdown.currentIndex() + 1
            self.accept()
        elif self.sender() is self.cancel_button:
            self.reject()

    @staticmethod
    def get_object_set(parent=None, alternative_title=""):
        """Run the dialog and return the selected object set.

        This helper is the workflow boundary most callers use. It opens the
        modal selector, optionally replaces the window title for a specific
        level-creation prompt, and translates the dialog result into the
        one-based object-set number expected by level-construction code or
        ``-1`` when the selection is cancelled.

        Parameters
        ----------
        parent : QDialog | None, optional
            Parent Qt widget that owns this object.
        alternative_title : str, optional
            Alternate window title for the prompt.

        Returns
        -------
        int
            Selected one-based object set, or ``-1`` when cancelled.
        """
        dialog = ObjectSetSelector(parent)

        if alternative_title:
            dialog.setWindowTitle(alternative_title)

        if dialog.exec() == QDialog.Accepted:
            return dialog.result
        else:
            return -1
