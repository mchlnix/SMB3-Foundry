"""Edit SMB3 jump-pointer values through a focused modal dialog.

This module owns the small dialog that stages one ``Jump`` object's encoded
screen, action, and destination fields before rebuilding the value on accept.
It sits on the narrow workflow boundary between jump selection in the editor
and the immutable-style ``Jump`` value that commands, lists, and save paths
continue to use afterward.

See Also
--------
foundry.game.gfx.objects.in_level.jump
    Value object edited and rebuilt by this dialog.
foundry.gui.dialogs.LevelHeaderEditor
    Broader header-editing dialog that also manipulates jump destinations.
"""

from PySide6.QtWidgets import (
    QComboBox,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QVBoxLayout,
    QWidget,
)

from foundry.game.gfx.objects.in_level.jump import Jump
from foundry.gui.dialogs.CustomDialog import CustomDialog
from foundry.gui.widgets.Spinner import Spinner

JUMP_ACTIONS = [
    "Downward Pipe 1",
    "Upward Pipe",
    "Downward Pipe 2",
    "Right Pipe",
    "Left Pipe",
    "0x5: ?",
    "0x6: ?",
    "Jump on Noteblock",
    "Door",
    "0x9: ?",
    "0xA: ?",
    "0xB: ?",
    "0xC: ?",
    "0xD: ?",
    "0xE: ?",
    "0xF: ?",
]

VERT_POSITIONS = [
    "00",
    "05",
    "08",
    "12",
    "16",
    "20",
    "23",
    "24",
    "00 (Vertical)",
    "05 (Vertical)",
    "08 (Vertical)",
    "12 (Vertical)",
    "16 (Vertical)",
    "20 (Vertical)",
    "23 (Vertical)",
    "24 (Vertical)",
]

MAX_SCREEN_INDEX = 0x0F
MAX_HORIZ_POSITION = 0xFF


class JumpEditor(CustomDialog):
    """Edit one SMB3 jump pointer object.

    Jump objects describe transitions such as pipes, doors, and note blocks.
    The dialog exposes the encoded screen index, exit action, and destination
    coordinates, then rebuilds the immutable-style ``Jump`` value when accepted.

    Parameters
    ----------
    parent : QWidget | None
        Parent Qt widget that owns this object.
    jump : Jump
        Jump pointer being edited.

    Attributes
    ----------
    exit_action : QComboBox
        Dropdown for the encoded jump action.
    exit_horizontal : Spinner
        Spinner for the destination x coordinate.
    exit_vertical : QComboBox
        Dropdown for the encoded destination y coordinate.
    jump : Jump
        Current jump value represented by the dialog.
    ok_button : object
        Dialog button that accepts the edited jump.
    screen_spinner : Spinner
        Spinner for the screen index where the jump trigger appears.
    """

    def __init__(self, parent: QWidget | None, jump: Jump):
        """Create widgets for editing one jump pointer.

        Construction follows the same three stages the edit workflow uses at
        runtime: build the level-position controls, build the exit-field
        controls, wire the accept and cancel buttons, then hydrate every widget
        from the staged ``Jump`` value. The dialog therefore stays as a modal
        staging surface that collects encoded-field edits first and only
        rebuilds the immutable-style jump object once acceptance commits the
        form state.

        Parameters
        ----------
        parent : QWidget | None
            Parent Qt widget that owns this object.
        jump : Jump
            Jump pointer being edited.
        """
        super(JumpEditor, self).__init__(parent, "Jump Editor")

        self.jump = jump

        self.screen_spinner = Spinner(parent=self, maximum=MAX_SCREEN_INDEX, base=10)

        position_layout = QFormLayout()
        position_layout.addRow("Jump on screen:", self.screen_spinner)

        level_group_box = QGroupBox("Level position")
        level_group_box.setLayout(position_layout)

        self.exit_action = QComboBox(self)
        self.exit_action.addItems(JUMP_ACTIONS)

        self.exit_horizontal = Spinner(parent=self, maximum=MAX_HORIZ_POSITION, base=10)

        self.exit_vertical = QComboBox(self)
        self.exit_vertical.addItems(VERT_POSITIONS)

        exit_layout = QFormLayout()
        exit_layout.addRow("Exit action:", self.exit_action)
        exit_layout.addRow("Exit position x:", self.exit_horizontal)
        exit_layout.addRow("Exit position y:", self.exit_vertical)

        exit_group_box = QGroupBox("Exit options")
        exit_group_box.setLayout(exit_layout)

        button_box = QDialogButtonBox()
        self.ok_button = button_box.addButton(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.clicked.connect(self.on_ok)
        button_box.addButton(QDialogButtonBox.StandardButton.Cancel).clicked.connect(self.close)

        main_layout = QVBoxLayout()
        main_layout.addWidget(level_group_box)
        main_layout.addWidget(exit_group_box)
        main_layout.addWidget(button_box)

        self.setLayout(main_layout)

        self._set_widget_values()

    def _set_widget_values(self):
        """Populate widgets from the staged jump value.

        The widgets mirror the four encoded fields carried by ``Jump`` so the
        dialog can round-trip the value without extra translation state.
        """
        self.screen_spinner.setValue(self.jump.screen_index)

        self.exit_action.setCurrentIndex(self.jump.exit_action)
        self.exit_horizontal.setValue(self.jump.exit_horizontal)
        self.exit_vertical.setCurrentIndex(self.jump.exit_vertical)

    @staticmethod
    def edit_jump(parent: QWidget | None, jump: Jump):
        """Open a modal editor and return the resulting jump value.

        This helper is the dialog's value-object boundary: callers provide the
        existing ``Jump``, the dialog mutates its local copy, and the updated
        value is returned after the modal session ends.


        Parameters
        ----------
        parent : QWidget | None
            Parent Qt widget that owns this object.
        jump : Jump
            Jump pointer being edited.

        Returns
        -------
        Jump
            Updated jump pointer after the dialog closes.
        """
        jump_editor = JumpEditor(parent, jump)

        jump_editor.exec()

        return jump_editor.jump

    def on_ok(self):
        """Accept the staged widget values as a new jump pointer.

        The dialog stores the rebuilt ``Jump`` and closes; callers read it from
        ``edit_jump``.
        """
        self.jump = Jump.from_properties(
            self.screen_spinner.value(),
            self.exit_action.currentIndex(),
            self.exit_horizontal.value(),
            self.exit_vertical.currentIndex(),
        )

        self.close()
