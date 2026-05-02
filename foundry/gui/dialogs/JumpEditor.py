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

from enum import IntEnum

from PySide6.QtWidgets import (
    QComboBox,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from foundry.game.gfx.objects.in_level.jump import Jump
from foundry.gui.dialogs.CustomDialog import CustomDialog
from foundry.gui.localization import tr
from foundry.gui.widgets.Spinner import Spinner

TR_KEY_CONTEXT = "foundry.jump_editor"


class JumpAction(IntEnum):
    """Map jump-action dropdown choices to encoded SMB3 nibble values.

    ``Jump.exit_action`` owns these values when jump-pointer data is decoded or
    rebuilt. The dialog stores each enum member as combo user data, refreshes
    only the translated label from ``JUMP_ACTION_LABELS``, and passes the
    stable integer back to ``Jump.from_properties`` on commit. Keep values
    stable and in encoded order; ``UNKNOWN_*`` members are retained for
    compatibility and round-trip safety, not as removable placeholders.

    Attributes
    ----------
    DOWNWARD_PIPE_1 : JumpAction
        First encoded downward-pipe action.
    UPWARD_PIPE : JumpAction
        Upward-pipe action.
    DOWNWARD_PIPE_2 : JumpAction
        Second encoded downward-pipe action.
    RIGHT_PIPE : JumpAction
        Right-facing pipe action.
    LEFT_PIPE : JumpAction
        Left-facing pipe action.
    UNKNOWN_5, UNKNOWN_6 : JumpAction
        Unknown encoded actions preserved for round-trip compatibility.
    NOTE_BLOCK : JumpAction
        Note-block jump action.
    DOOR : JumpAction
        Door jump action.
    UNKNOWN_9, UNKNOWN_A, UNKNOWN_B, UNKNOWN_C : JumpAction
        Unknown encoded actions preserved for round-trip compatibility.
    UNKNOWN_D, UNKNOWN_E, UNKNOWN_F : JumpAction
        Unknown encoded actions preserved for round-trip compatibility.
    """

    DOWNWARD_PIPE_1 = 0x0
    UPWARD_PIPE = 0x1
    DOWNWARD_PIPE_2 = 0x2
    RIGHT_PIPE = 0x3
    LEFT_PIPE = 0x4
    UNKNOWN_5 = 0x5
    UNKNOWN_6 = 0x6
    NOTE_BLOCK = 0x7
    DOOR = 0x8
    UNKNOWN_9 = 0x9
    UNKNOWN_A = 0xA
    UNKNOWN_B = 0xB
    UNKNOWN_C = 0xC
    UNKNOWN_D = 0xD
    UNKNOWN_E = 0xE
    UNKNOWN_F = 0xF


class JumpVerticalPosition(IntEnum):
    """Map jump vertical-position choices to encoded SMB3 nibble values.

    ``Jump.exit_vertical`` owns these values when a jump destination is decoded
    or rebuilt. The normal and vertical groups intentionally repeat visible
    numeric labels, but each enum member remains a distinct stored nibble.
    Combo boxes keep the integer payload stable while ``JUMP_VERTICAL_POSITION_LABELS``
    and ``tr`` provide user-visible text. The enum is the commit boundary
    between Qt selection state and jump-pointer data, so live translation
    refreshes can change labels without changing the encoded destination.
    """

    POSITION_00 = 0x0
    POSITION_05 = 0x1
    POSITION_08 = 0x2
    POSITION_12 = 0x3
    POSITION_16 = 0x4
    POSITION_20 = 0x5
    POSITION_23 = 0x6
    POSITION_24 = 0x7
    VERTICAL_00 = 0x8
    VERTICAL_05 = 0x9
    VERTICAL_08 = 0xA
    VERTICAL_12 = 0xB
    VERTICAL_16 = 0xC
    VERTICAL_20 = 0xD
    VERTICAL_23 = 0xE
    VERTICAL_24 = 0xF


JUMP_ACTION_LABELS = {
    JumpAction.DOWNWARD_PIPE_1: "Downward Pipe 1",
    JumpAction.UPWARD_PIPE: "Upward Pipe",
    JumpAction.DOWNWARD_PIPE_2: "Downward Pipe 2",
    JumpAction.RIGHT_PIPE: "Right Pipe",
    JumpAction.LEFT_PIPE: "Left Pipe",
    JumpAction.UNKNOWN_5: "0x5: ?",
    JumpAction.UNKNOWN_6: "0x6: ?",
    JumpAction.NOTE_BLOCK: "Jump on Noteblock",
    JumpAction.DOOR: "Door",
    JumpAction.UNKNOWN_9: "0x9: ?",
    JumpAction.UNKNOWN_A: "0xA: ?",
    JumpAction.UNKNOWN_B: "0xB: ?",
    JumpAction.UNKNOWN_C: "0xC: ?",
    JumpAction.UNKNOWN_D: "0xD: ?",
    JumpAction.UNKNOWN_E: "0xE: ?",
    JumpAction.UNKNOWN_F: "0xF: ?",
}

JUMP_VERTICAL_POSITION_LABELS = {
    JumpVerticalPosition.POSITION_00: "00",
    JumpVerticalPosition.POSITION_05: "05",
    JumpVerticalPosition.POSITION_08: "08",
    JumpVerticalPosition.POSITION_12: "12",
    JumpVerticalPosition.POSITION_16: "16",
    JumpVerticalPosition.POSITION_20: "20",
    JumpVerticalPosition.POSITION_23: "23",
    JumpVerticalPosition.POSITION_24: "24",
    JumpVerticalPosition.VERTICAL_00: "00 (Vertical)",
    JumpVerticalPosition.VERTICAL_05: "05 (Vertical)",
    JumpVerticalPosition.VERTICAL_08: "08 (Vertical)",
    JumpVerticalPosition.VERTICAL_12: "12 (Vertical)",
    JumpVerticalPosition.VERTICAL_16: "16 (Vertical)",
    JumpVerticalPosition.VERTICAL_20: "20 (Vertical)",
    JumpVerticalPosition.VERTICAL_23: "23 (Vertical)",
    JumpVerticalPosition.VERTICAL_24: "24 (Vertical)",
}

MAX_SCREEN_INDEX = 0x0F
MAX_HORIZ_POSITION = 0xFF


def _add_enum_options(dropdown: QComboBox, labels: dict[IntEnum, str]) -> None:
    """Populate a combo box with translated labels and stable enum payloads.

    Parameters
    ----------
    dropdown : QComboBox
        Combo box receiving the options.
    labels : dict[IntEnum, str]
        Mapping from encoded enum values to English fallback labels.

    Notes
    -----
    The visible text is catalog-backed, while ``Qt.UserRole`` stores the
    encoded integer used by ``Jump`` reconstruction. That split lets language
    refreshes change labels without changing jump-pointer data.
    """
    for option in sorted(labels, key=int):
        dropdown.addItem(
            tr(TR_KEY_CONTEXT, f"{option.__class__.__name__}.{option.name}".casefold(), labels[option]), int(option)
        )


def _retranslate_enum_options(dropdown: QComboBox, labels: dict[IntEnum, str]) -> None:
    """Refresh combo labels while preserving encoded option values.

    Parameters
    ----------
    dropdown : QComboBox
        Existing combo box whose rows already carry enum integer data.
    labels : dict[IntEnum, str]
        Mapping from encoded enum values to English fallback labels.

    Notes
    -----
    The lookup is by stored user data rather than row order so translated text
    can be replaced during live language switching without disturbing the
    currently staged jump action or destination value.
    """
    for option in sorted(labels, key=int):
        index = dropdown.findData(int(option))
        if index >= 0:
            dropdown.setItemText(
                index,
                tr(TR_KEY_CONTEXT, f"{option.__class__.__name__}.{option.name}".casefold(), labels[option]),
            )


def _set_current_data(dropdown: QComboBox, value: int) -> None:
    """Select the combo row whose user data stores an encoded value.

    Jump fields are edited through translated combo text, but the saved SMB3
    value is still the integer stored in ``Qt.UserRole``. Falling back to the
    numeric row preserves round-tripping for older or unknown jump encodings.

    Parameters
    ----------
    dropdown : QComboBox
        Combo box containing encoded integer user data.
    value : int
        Encoded jump field value to select.

    Notes
    -----
    Unknown or legacy values fall back to their numeric row so the editor can
    still round-trip jump data that predates the known enum labels.
    """
    index = dropdown.findData(value)
    dropdown.setCurrentIndex(index if index >= 0 else value)


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
    exit_horizontal_label : QLabel
        Form label for the destination x control.
    exit_vertical : QComboBox
        Dropdown for the encoded destination y coordinate.
    exit_vertical_label : QLabel
        Form label for the destination y control.
    exit_action_label : QLabel
        Form label for the encoded exit-action dropdown.
    exit_group_box : QGroupBox
        Group box that owns exit-action and destination controls.
    jump : Jump
        Current jump value represented by the dialog.
    level_group_box : QGroupBox
        Group box that owns the trigger-screen controls.
    ok_button : object
        Dialog button that accepts the edited jump.
    screen_label : QLabel
        Form label for the trigger-screen spinner.
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
        super(JumpEditor, self).__init__(parent, tr(TR_KEY_CONTEXT, "title", "Jump Editor"))

        self.jump = jump

        self.screen_spinner = Spinner(parent=self, maximum=MAX_SCREEN_INDEX, base=10)

        self.screen_label = QLabel(self)
        position_layout = QFormLayout()
        position_layout.addRow(self.screen_label, self.screen_spinner)

        self.level_group_box = QGroupBox(self)
        self.level_group_box.setLayout(position_layout)

        self.exit_action = QComboBox(self)
        _add_enum_options(self.exit_action, JUMP_ACTION_LABELS)

        self.exit_horizontal = Spinner(parent=self, maximum=MAX_HORIZ_POSITION, base=10)

        self.exit_vertical = QComboBox(self)
        _add_enum_options(self.exit_vertical, JUMP_VERTICAL_POSITION_LABELS)

        self.exit_action_label = QLabel(self)
        self.exit_horizontal_label = QLabel(self)
        self.exit_vertical_label = QLabel(self)
        exit_layout = QFormLayout()
        exit_layout.addRow(self.exit_action_label, self.exit_action)
        exit_layout.addRow(self.exit_horizontal_label, self.exit_horizontal)
        exit_layout.addRow(self.exit_vertical_label, self.exit_vertical)

        self.exit_group_box = QGroupBox(self)
        self.exit_group_box.setLayout(exit_layout)

        button_box = QDialogButtonBox()
        self.ok_button = button_box.addButton(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.clicked.connect(self.on_ok)
        button_box.addButton(QDialogButtonBox.StandardButton.Cancel).clicked.connect(self.close)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.level_group_box)
        main_layout.addWidget(self.exit_group_box)
        main_layout.addWidget(button_box)

        self.setLayout(main_layout)

        self.retranslate_ui()
        self._set_widget_values()

    def retranslate_ui(self) -> None:
        """Refresh visible Qt labels without touching encoded jump state.

        Live language switching changes window text, form labels, group titles,
        and combo item labels. It leaves the selected combo user data and
        spinner values intact so the staged ``Jump`` still commits the same
        SMB3 jump-pointer fields after translation refresh.
        """
        self.setWindowTitle(tr(TR_KEY_CONTEXT, "title", "Jump Editor"))
        self.screen_label.setText(tr(TR_KEY_CONTEXT, "label.jump_on_screen", "Jump on screen:"))
        self.level_group_box.setTitle(tr(TR_KEY_CONTEXT, "group.level_position", "Level position"))
        self.exit_action_label.setText(tr(TR_KEY_CONTEXT, "label.exit_action", "Exit action:"))
        self.exit_horizontal_label.setText(tr(TR_KEY_CONTEXT, "label.exit_position_x", "Exit position x:"))
        self.exit_vertical_label.setText(tr(TR_KEY_CONTEXT, "label.exit_position_y", "Exit position y:"))
        self.exit_group_box.setTitle(tr(TR_KEY_CONTEXT, "group.exit_options", "Exit options"))
        _retranslate_enum_options(self.exit_action, JUMP_ACTION_LABELS)
        _retranslate_enum_options(self.exit_vertical, JUMP_VERTICAL_POSITION_LABELS)

    def _set_widget_values(self):
        """Populate widgets from the staged jump value.

        The widgets mirror the four encoded fields carried by ``Jump`` so the
        dialog can round-trip the value without extra translation state.
        """
        self.screen_spinner.setValue(self.jump.screen_index)

        _set_current_data(self.exit_action, self.jump.exit_action)
        self.exit_horizontal.setValue(self.jump.exit_horizontal)
        _set_current_data(self.exit_vertical, self.jump.exit_vertical)

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
            int(self.exit_action.currentData()),
            self.exit_horizontal.value(),
            int(self.exit_vertical.currentData()),
        )

        self.close()
