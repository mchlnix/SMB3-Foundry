"""Edit the encoded SMB3 level header through undo-aware dialog controls.

This module owns the dialog that maps Qt controls onto the level header fields
exposed by ``LevelRef``: gameplay flags, Mario start state, graphics and
palette selections, and the next-area pointers that branch into another level.
It is the dialog-layer bridge between human-readable header controls and the
command objects that preserve undo, replay, and dirty-state behavior.

See Also
--------
foundry.game.level.LevelRef
    Header-backed level view edited by this dialog.
foundry.gui.commands
    Command layer that receives staged header changes from this dialog.
foundry.gui.dialogs.level_selector.LevelSelector
    Source of next-area destination data when the user picks another level.
"""

from PySide6.QtGui import Qt, QUndoStack
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from foundry import make_macro
from foundry.game.gfx.GraphicsSet import GRAPHIC_SET_NAMES
from foundry.game.level.LevelRef import LevelRef
from foundry.gui import OBJECT_SET_ITEMS
from foundry.gui.commands import (
    SetLevelAttribute,
    SetNextAreaEnemyAddress,
    SetNextAreaObjectAddress,
    SetNextAreaObjectSet,
)
from foundry.gui.dialogs.CustomDialog import CustomDialog
from foundry.gui.dialogs.level_selector.LevelSelector import LevelSelector
from foundry.gui.widgets.Spinner import Spinner
from smb3parse.constants import OBJECT_SET_NAMES
from smb3parse.levels import ENEMY_BASE_OFFSET
from smb3parse.levels.level_header import MARIO_X_POSITIONS, MARIO_Y_POSITIONS

LEVEL_LENGTHS = [0x10 * (i + 1) for i in range(0, 2**4)]
STR_LEVEL_LENGTHS = [f"{length - 1:0=#4X} / {length} Blocks".replace("X", "x") for length in LEVEL_LENGTHS]

STR_X_POSITIONS = [f"{position >> 4}. Block ({position:0=#4X})".replace("X", "x") for position in MARIO_X_POSITIONS]

STR_Y_POSITIONS = [f"{position}. Block ({position:0=#4X})".replace("X", "x") for position in MARIO_Y_POSITIONS]

ACTIONS = [
    "None",
    "Sliding",
    "Out of pipe ↑",
    "Out of pipe ↓",
    "Out of pipe →",
    "Out of pipe ←",
    "Running and climbing up ship",
    "Ship auto scrolling",
]

MUSIC_ITEMS = [
    "Plain level",
    "Underground",
    "Water level",
    "Fortress",
    "Boss",
    "Ship",
    "Battle",
    "P-Switch/Mushroom house (1)",
    "Hilly level",
    "Castle room",
    "Clouds/Sky",
    "P-Switch/Mushroom house (2)",
    "No music",
    "P-Switch/Mushroom house (1)",
    "No music",
    "World 7 map",
]

TIMES = ["300s", "400s", "200s", "Unlimited"]

CAMERA_MOVEMENTS = [
    "Locked, unless climbing/flying",
    "Free vertical scrolling",
    "Locked 'by start coordinates'?",
    "Shouldn't appear in game, do not use.",
]


SPINNER_MAX_VALUE = 0x0F_FF_FF


# change of object palette is always triggered for some reason
class LevelHeaderEditor(CustomDialog):
    """Edit the nine-byte SMB3 level header.

    The dialog maps user-facing controls onto the encoded header fields exposed
    by ``Level`` and ``LevelRef``: length, music, timer, scroll behavior, start
    position, palette indexes, graphics set, and next-area pointers. Changes are
    pushed as undo commands so header edits participate in the normal editor
    history.

    Parameters
    ----------
    parent : QWidget | None
        Parent Qt widget that owns this object.
    level_ref : LevelRef
        Reference to the edited level.

    Attributes
    ----------
    _enemy_address_label : QLabel
        Resolved absolute enemy/item address for the next-area pointer.
    _level_address_label : QLabel
        Resolved absolute layout address for the next-area pointer.
    action_dropdown : QComboBox
        Player entry action selector.
    camera_movement_dropdown : QComboBox
        Scroll-type selector.
    enemy_palette_spinner : Spinner
        Enemy palette index editor.
    enemy_pointer_spinner : Spinner
        Next-area enemy offset editor.
    graphic_set_dropdown : QComboBox
        Graphics set selector.
    header_bytes_label : QLabel
        Raw header byte display.
    length_dropdown : QComboBox
        Level length selector.
    level : LevelRef
        Reference to the level being edited.
    level_is_vertical_cb : QCheckBox
        Vertical-level flag editor.
    level_pointer_spinner : Spinner
        Next-area layout offset editor.
    music_dropdown : QComboBox
        Music index selector.
    next_area_object_set_dropdown : QComboBox
        Object set selector for the next area.
    object_palette_spinner : Spinner
        Object palette index editor.
    pipe_ends_level_cb : QCheckBox
        Pipe-ends-level flag editor.
    tab_widget : QTabWidget
        Tab container for grouped header controls.
    time_dropdown : QComboBox
        Timer index selector.
    x_position_dropdown : QComboBox
        Player start x selector.
    y_position_dropdown : QComboBox
        Player start y selector.

    Notes
    -----
    The dialog does not write header bytes directly on every widget change.
    Instead it stages field edits through undo commands so header changes stay
    mergeable, replayable, and visible to the rest of the editor through the
    normal undo-stack workflow.

    See Also
    --------
    SetLevelAttribute
        Base command used for most header-field edits.
    SetNextAreaObjectAddress, SetNextAreaEnemyAddress, SetNextAreaObjectSet
        Commands used for next-area pointer updates.
    """

    def __init__(self, parent: QWidget | None, level_ref: LevelRef):
        """Create controls for editing a level header.

        Widgets are grouped by gameplay concern: level behavior, player start,
        graphics/palettes, and next-area destination. Signal handlers route
        edits into undo commands rather than mutating header bytes directly from
        the form widgets, so the dialog stays aligned with the editor's merge,
        replay, and dirty-state workflow.

        Parameters
        ----------
        parent : QWidget | None
            Parent Qt widget that owns this object.
        level_ref : LevelRef
            Reference to the edited level.
        """
        super(LevelHeaderEditor, self).__init__(parent, "Level Header Editor")

        self.level = level_ref

        main_layout = QVBoxLayout(self)

        self.tab_widget = QTabWidget(self)
        main_layout.addWidget(self.tab_widget)

        # level settings
        self.length_dropdown = QComboBox()
        self.length_dropdown.addItems(STR_LEVEL_LENGTHS)
        self.length_dropdown.activated.connect(self.on_combo)

        self.music_dropdown = QComboBox()
        self.music_dropdown.addItems(MUSIC_ITEMS)
        self.music_dropdown.activated.connect(self.on_combo)

        self.time_dropdown = QComboBox()
        self.time_dropdown.addItems(TIMES)
        self.time_dropdown.activated.connect(self.on_combo)

        self.camera_movement_dropdown = QComboBox()
        self.camera_movement_dropdown.addItems(CAMERA_MOVEMENTS)
        self.camera_movement_dropdown.activated.connect(self.on_combo)

        self.level_is_vertical_cb = QCheckBox("Level is Vertical")
        self.level_is_vertical_cb.clicked.connect(self.on_check_box)

        self.pipe_ends_level_cb = QCheckBox("Pipe ends Level")
        self.pipe_ends_level_cb.clicked.connect(self.on_check_box)

        check_box_layout = QHBoxLayout()
        check_box_layout.setContentsMargins(0, 0, 0, 0)
        check_box_layout.addWidget(self.level_is_vertical_cb)
        check_box_layout.addWidget(self.pipe_ends_level_cb)

        check_box_widget = QWidget()
        check_box_widget.setLayout(check_box_layout)

        form = QFormLayout()
        form.setFormAlignment(Qt.AlignmentFlag.AlignCenter)

        form.addRow("Level Length: ", self.length_dropdown)
        form.addRow("Music: ", self.music_dropdown)
        form.addRow("Time: ", self.time_dropdown)
        form.addRow("Vertical Camera Movement: ", self.camera_movement_dropdown)

        form.addWidget(check_box_widget)

        widget = QWidget()
        widget.setLayout(form)

        self.tab_widget.addTab(widget, "Level")

        # player settings

        self.x_position_dropdown = QComboBox()
        self.x_position_dropdown.addItems(STR_X_POSITIONS)
        self.x_position_dropdown.activated.connect(self.on_combo)

        self.y_position_dropdown = QComboBox()
        self.y_position_dropdown.addItems(STR_Y_POSITIONS)
        self.y_position_dropdown.activated.connect(self.on_combo)

        self.action_dropdown = QComboBox()
        self.action_dropdown.addItems(ACTIONS)
        self.action_dropdown.activated.connect(self.on_combo)

        form = QFormLayout()
        form.setFormAlignment(Qt.AlignmentFlag.AlignCenter)

        form.addRow("Starting X: ", self.x_position_dropdown)
        form.addRow("Starting Y: ", self.y_position_dropdown)
        form.addRow("Action: ", self.action_dropdown)

        widget = QWidget()
        widget.setLayout(form)

        self.tab_widget.addTab(widget, "Mario")

        # graphic settings

        self.object_palette_spinner = Spinner(self, maximum=7)
        self.object_palette_spinner.valueChanged.connect(self.on_spin)

        self.enemy_palette_spinner = Spinner(self, maximum=3)
        self.enemy_palette_spinner.valueChanged.connect(self.on_spin)

        self.graphic_set_dropdown = QComboBox()
        self.graphic_set_dropdown.addItems(GRAPHIC_SET_NAMES)
        self.graphic_set_dropdown.activated.connect(self.on_combo)

        form = QFormLayout()
        form.setFormAlignment(Qt.AlignmentFlag.AlignCenter)

        form.addRow("Object Palette: ", self.object_palette_spinner)
        form.addRow("Enemy Palette: ", self.enemy_palette_spinner)
        form.addRow("Graphic Set: ", self.graphic_set_dropdown)

        widget = QWidget()
        widget.setLayout(form)

        self.tab_widget.addTab(widget, "Graphics")

        # next area settings
        self.level_pointer_spinner = Spinner(self)
        self.level_pointer_spinner.valueChanged.connect(self.on_spin)
        self.level_pointer_spinner.setMinimum(0)
        self.level_pointer_spinner.setMaximum(0xFFFF)

        self._level_address_label = QLabel()
        self._level_address_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.enemy_pointer_spinner = Spinner(self)
        self.enemy_pointer_spinner.valueChanged.connect(self.on_spin)
        self.enemy_pointer_spinner.setMinimum(0)
        self.enemy_pointer_spinner.setMaximum(0xFFFF)

        self._enemy_address_label = QLabel()
        self._enemy_address_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.next_area_object_set_dropdown = QComboBox()
        self.next_area_object_set_dropdown.addItems(OBJECT_SET_ITEMS)
        self.next_area_object_set_dropdown.activated.connect(self.on_combo)

        level_select_button = QPushButton("Set from Level Selector")
        level_select_button.clicked.connect(self._set_jump_destination)

        current_level_select_button = QPushButton("Use current Level")
        current_level_select_button.clicked.connect(self._set_from_current_level)

        form = QFormLayout()
        form.setFormAlignment(Qt.AlignmentFlag.AlignCenter)

        form.addRow("Offset of Level Objects: ", self.level_pointer_spinner)
        form.addRow("Address of Level Objects: ", self._level_address_label)
        form.addRow("Offset of Enemies: ", self.enemy_pointer_spinner)
        form.addRow("Address of Enemies: ", self._enemy_address_label)
        form.addRow("Object Set: ", self.next_area_object_set_dropdown)

        form.addRow(QLabel(""))
        form.addRow(level_select_button)
        form.addRow(current_level_select_button)

        widget = QWidget()
        widget.setLayout(form)

        self.tab_widget.addTab(widget, "Jump Destination")

        self.header_bytes_label = QLabel()

        main_layout.addWidget(self.header_bytes_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.update()

    @property
    def undo_stack(self) -> QUndoStack:
        """Expose the shared undo stack used for header-field commands.

        Header changes are pushed here as command objects rather than mutating
        the level directly from callbacks, which keeps dialog edits merged into
        the same history and dirty-state lifecycle as viewport commands.

        Returns
        -------
        QUndoStack
            Undo stack named ``undo_stack`` in the owning window.
        """
        return self.parent().window().findChild(QUndoStack, "undo_stack")

    def update(self):
        """Synchronize controls from the loaded level header.

        The refresh happens in four phases. First the dialog mirrors the basic
        header fields such as length, music, timer, start state, and graphics
        directly from ``LevelRef``. Next it blocks signals while it converts
        the ROM-backed next-area addresses back into the offset-based values
        shown in the pointer controls, so programmatic synchronization does not
        emit new undo commands. Finally it rebuilds the raw-byte preview and
        emits palette and data-changed signals so dependent editor surfaces
        repaint from the newly synchronized header state. This makes
        ``update`` the central redraw path after header commands, destination
        changes, and level reloads.
        """
        length_index = LEVEL_LENGTHS.index(self.level.length)

        self.length_dropdown.setCurrentIndex(length_index)
        self.music_dropdown.setCurrentIndex(self.level.music_index)
        self.time_dropdown.setCurrentIndex(self.level.time_index)
        self.camera_movement_dropdown.setCurrentIndex(self.level.scroll_type)
        self.level_is_vertical_cb.setChecked(self.level.is_vertical)
        self.pipe_ends_level_cb.setChecked(self.level.pipe_ends_level)

        self.x_position_dropdown.setCurrentIndex(self.level.start_x_index)
        self.y_position_dropdown.setCurrentIndex(self.level.start_y_index)
        self.action_dropdown.setCurrentIndex(self.level.start_action)

        self.object_palette_spinner.setValue(self.level.object_palette_index)
        self.enemy_palette_spinner.setValue(self.level.enemy_palette_index)
        self.graphic_set_dropdown.setCurrentIndex(self.level.graphic_set)

        self.blockSignals(True)

        self.level_pointer_spinner.setValue(self.level.header.jump_level_offset)
        self._level_address_label.setText(
            hex(self.level.header.jump_object_set.level_offset + self.level_pointer_spinner.value())
        )
        self.enemy_pointer_spinner.setValue(self.level.header.jump_enemy_offset)
        self._enemy_address_label.setText(hex(ENEMY_BASE_OFFSET + self.enemy_pointer_spinner.value()))
        self.next_area_object_set_dropdown.setCurrentIndex(self.level.next_area_object_set_no)

        self.blockSignals(False)

        self.header_bytes_label.setText(" ".join(f"{number:0=#4X}"[2:] for number in self.level.header_bytes))

        self.level.palette_changed.emit()
        self.level.data_changed.emit()

    def _set_level_attr(self, name: str, value, display_name="", display_value=""):
        """Push a command that changes one level header attribute.

        ``display_name`` and ``display_value`` let the command present more
        readable undo text than the raw property name or integer value. The
        helper is the dialog's main bridge from form widgets to undoable header
        mutations, including repeated combo-box cycling that can later merge on
        the undo stack. Combo boxes, check boxes, and spinners all converge on
        this helper so header edits share one command-construction path instead
        of each widget deciding independently how to mutate ``LevelRef``. That
        keeps undo text, command coalescing, and replay behavior aligned across
        the whole dialog.

        Parameters
        ----------
        name : str
            ``LevelRef`` attribute to update.
        value : object
            New value for the attribute.
        display_name : str, optional
            Human-readable field name for undo text.
        display_value : str, optional
            Display text shown in the UI.
        """
        self.undo_stack.push(SetLevelAttribute(self.level, name, value, display_name, display_value))

    def _set_jump_destination(self):
        """Open the level selector and use its choice as next-area data.

        The selected layout address, enemy address, and object set are committed
        as one undo macro.
        """
        level_selector = LevelSelector(self)

        if self.level:
            level_selector.goto_world(self.level.world)

        level_was_selected = level_selector.exec() == QDialog.DialogCode.Accepted

        if not level_was_selected:
            return

        level_address = level_selector.object_data_offset
        enemy_address = level_selector.enemy_data_offset
        object_set_number = level_selector.object_set

        self._set_jump_destination_values(enemy_address, level_address, object_set_number)

        self.update()

    def _set_from_current_level(self):
        """Use the loaded ROM-backed level as the next area.

        Imported or detached levels do not have ROM addresses, so they cannot be
        used as jump destinations.
        """
        if not self.level.level.attached_to_rom:
            QMessageBox.warning(
                self,
                "Warning",
                "The current level is not attached to the ROM and does not have a level or enemy address yet.\n\n"
                "That's why you can't set it as a Jump Destination yet.",
            )

        level_address = self.level.level.header_offset
        enemy_address = self.level.level.enemy_offset
        object_set_number = self.level.level.object_set.number

        self._set_jump_destination_values(enemy_address, level_address, object_set_number)

        self.update()

    def _set_jump_destination_values(self, enemy_offset: int, level_offset: int, object_set_number: int):
        """Commit next-area destination values as one undo macro.

        The three encoded fields are coupled: object set affects how the layout
        pointer is resolved, while the enemy pointer uses a separate base.

        Parameters
        ----------
        enemy_offset : int
            ROM enemy offset.
        level_offset : int
            ROM level offset.
        object_set_number : int
            Object set number that selects graphics and object definitions.
        """
        self.blockSignals(True)

        self.next_area_object_set_dropdown.setCurrentIndex(object_set_number)
        self.level_pointer_spinner.setValue(level_offset)
        self.enemy_pointer_spinner.setValue(enemy_offset)

        self.blockSignals(False)

        make_macro(
            self.undo_stack,
            f"Set Next Area to {level_offset:#x}/{enemy_offset:#x}, {OBJECT_SET_NAMES[object_set_number]}",
            SetNextAreaObjectSet(self.level, object_set_number),
            SetNextAreaObjectAddress(self.level, level_offset),
            SetNextAreaEnemyAddress(self.level, enemy_offset),
        )

    def on_spin(self, new_value):
        """Respond to spinner changes for palette and pointer fields.

        Palette spinners map to ordinary header attributes. Pointer spinners are
        stored as offsets in the UI and converted back to absolute addresses for
        commands.

        Parameters
        ----------
        new_value : int
            Replacement setting value.
        """
        if not self.level or self.signalsBlocked():
            return

        spinner = self.sender()

        if spinner == self.object_palette_spinner:
            self._set_level_attr("object_palette_index", new_value)

        elif spinner == self.enemy_palette_spinner:
            self._set_level_attr("enemy_palette_index", new_value)

        elif spinner == self.level_pointer_spinner and new_value != self.level.header.jump_level_offset:
            self.undo_stack.push(
                SetNextAreaObjectAddress(self.level, self.level.header.jump_object_set.level_offset + new_value)
            )

        elif spinner == self.enemy_pointer_spinner and new_value != self.level.header.jump_enemy_offset:
            self.undo_stack.push(SetNextAreaEnemyAddress(self.level, ENEMY_BASE_OFFSET + new_value))

        self.update()

    def on_combo(self, new_index):
        """Respond to dropdown changes for encoded header fields.

        Each dropdown maps its selected index to the corresponding ``LevelRef``
        property and pushes an undo command when the value actually changes.

        Parameters
        ----------
        new_index : int
            Selected dropdown index.
        """
        if not self.level or self.signalsBlocked():
            return

        dropdown = self.sender()
        assert isinstance(dropdown, QComboBox)

        text = dropdown.currentText()

        # TODO do this via properties and get rid of the ifs?
        if dropdown == self.length_dropdown and (new_length := LEVEL_LENGTHS[new_index]) != self.level.length:
            self._set_level_attr("length", new_length, display_value=text)

        elif dropdown == self.music_dropdown and new_index != self.level.music_index:
            self._set_level_attr("music_index", new_index, display_value=text)

        elif dropdown == self.time_dropdown:
            self._set_level_attr("time_index", new_index, display_value=text)

        elif dropdown == self.camera_movement_dropdown:
            self._set_level_attr(
                "scroll_type",
                new_index,
                display_name="Camera Movement",
                display_value=text,
            )

        elif dropdown == self.x_position_dropdown:
            self._set_level_attr(
                "start_x_index",
                new_index,
                display_name="Mario Start X",
                display_value=text,
            )

        elif dropdown == self.y_position_dropdown:
            self._set_level_attr(
                "start_y_index",
                new_index,
                display_name="Mario Start Y",
                display_value=text,
            )

        elif dropdown == self.action_dropdown:
            self._set_level_attr(
                "start_action",
                new_index,
                display_name="Mario Start Action",
                display_value=text,
            )

        elif dropdown == self.graphic_set_dropdown:
            self._set_level_attr("graphic_set", new_index, display_value=text)

        elif dropdown == self.next_area_object_set_dropdown and new_index != self.level.next_area_object_set_no:
            object_set_cmd = SetNextAreaObjectSet(self.level, new_index)

            # in case the level address changes based on the new object set, don't list that command separately
            make_macro(self.undo_stack, object_set_cmd.text(), object_set_cmd)

        self.update()

    def on_check_box(self, checked):
        """Respond to checkbox changes for boolean header flags.


        Parameters
        ----------
        checked : bool
            New checked state emitted by Qt.
        """
        if not self.level or self.signalsBlocked():
            return

        checkbox = self.sender()
        assert isinstance(checkbox, QCheckBox)
        assert checked == checkbox.isChecked()

        if checkbox == self.pipe_ends_level_cb:
            self._set_level_attr("pipe_ends_level", checked)
        elif checkbox == self.level_is_vertical_cb:
            self._set_level_attr("is_vertical", checked, "Level is Vertical")

        self.update()
