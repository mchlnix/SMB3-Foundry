from typing import Optional

from PySide6.QtGui import Qt, QUndoStack
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from foundry import make_macro
from foundry.game.gfx.GraphicsSet import GRAPHIC_SET_NAMES
from foundry.game.level.Level import Level
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
from smb3parse.levels import ENEMY_BASE_OFFSET
from smb3parse.levels.level_header import MARIO_X_POSITIONS, MARIO_Y_POSITIONS
from smb3parse.objects.object_set import OBJECT_SET_NAMES

LEVEL_LENGTHS = [0x10 * (i + 1) for i in range(0, 2**4)]

STR_LEVEL_LENGTHS = [
    _("%(hex)s / %(length)d Blocks") % {"hex": f"0x{length - 1:0=4X}", "length": length}
    for length in LEVEL_LENGTHS
]

STR_X_POSITIONS = [
    _("%(number)d. Block (%(hex)s)")
    % {"number": position >> 4, "hex": f"0x{position:0=2X}"}
    for position in MARIO_X_POSITIONS
]

STR_Y_POSITIONS = [
    _("%(number)d. Block (%(hex)s)") % {"number": position, "hex": f"0x{position:0=2X}"}
    for position in MARIO_Y_POSITIONS
]

ACTIONS = [
    _("None"),
    _("Sliding"),
    _("Out of pipe ↑"),
    _("Out of pipe ↓"),
    _("Out of pipe →"),
    _("Out of pipe ←"),
    _("Running and climbing up ship"),
    _("Ship auto scrolling"),
]

MUSIC_ITEMS = [
    _("Plain level"),
    _("Underground"),
    _("Water level"),
    _("Fortress"),
    _("Boss"),
    _("Ship"),
    _("Battle"),
    _("P-Switch/Mushroom house (1)"),
    _("Hilly level"),
    _("Castle room"),
    _("Clouds/Sky"),
    _("P-Switch/Mushroom house (2)"),
    _("No music"),
    _("P-Switch/Mushroom house (1)"),
    _("No music"),
    _("World 7 map"),
]

TIMES = [_("300 seconds"), _("400 seconds"), _("200 seconds"), _("Unlimited")]

CAMERA_MOVEMENTS = [
    _("Locked, unless climbing/flying"),
    _("Free vertical scrolling"),
    _("Locked 'by start coordinates'?"),
    _("Shouldn't appear in game, do not use."),
]


SPINNER_MAX_VALUE = 0x0F_FF_FF


class HeaderEditor(CustomDialog):
    def __init__(self, parent: Optional[QWidget], level_ref: LevelRef):
        super(HeaderEditor, self).__init__(parent, _("Level Header Editor"))

        self.level: Level = level_ref.level

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

        self.level_is_vertical_cb = QCheckBox(_("Level is Vertical"))
        self.level_is_vertical_cb.clicked.connect(self.on_check_box)

        self.pipe_ends_level_cb = QCheckBox(_("Pipe ends Level"))
        self.pipe_ends_level_cb.clicked.connect(self.on_check_box)

        check_box_layout = QHBoxLayout()
        check_box_layout.setContentsMargins(0, 0, 0, 0)
        check_box_layout.addWidget(self.level_is_vertical_cb)
        check_box_layout.addWidget(self.pipe_ends_level_cb)

        check_box_widget = QWidget()
        check_box_widget.setLayout(check_box_layout)

        form = QFormLayout()
        form.setFormAlignment(Qt.AlignmentFlag.AlignCenter)

        form.addRow(_("Level Length: "), self.length_dropdown)
        form.addRow(_("Music: "), self.music_dropdown)
        form.addRow(_("Time: "), self.time_dropdown)
        form.addRow(_("Vertical Camera Movement: "), self.camera_movement_dropdown)

        form.addWidget(check_box_widget)

        widget = QWidget()
        widget.setLayout(form)

        self.tab_widget.addTab(widget, _("Level"))

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

        form.addRow(_("Starting X: "), self.x_position_dropdown)
        form.addRow(_("Starting Y: "), self.y_position_dropdown)
        form.addRow(_("Action: "), self.action_dropdown)

        widget = QWidget()
        widget.setLayout(form)

        self.tab_widget.addTab(widget, _("Mario"))

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

        form.addRow(_("Object Palette: "), self.object_palette_spinner)
        form.addRow(_("Enemy Palette: "), self.enemy_palette_spinner)
        form.addRow(_("Graphic Set: "), self.graphic_set_dropdown)

        widget = QWidget()
        widget.setLayout(form)

        self.tab_widget.addTab(widget, _("Graphics"))

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

        level_select_button = QPushButton(_("Set from Level Selector"))
        level_select_button.clicked.connect(self._set_jump_destination)

        form = QFormLayout()
        form.setFormAlignment(Qt.AlignmentFlag.AlignCenter)

        form.addRow(_("Offset of Level Objects: "), self.level_pointer_spinner)
        form.addRow(_("Address of Level Objects: "), self._level_address_label)
        form.addRow(_("Offset of Enemies: "), self.enemy_pointer_spinner)
        form.addRow(_("Address of Enemies: "), self._enemy_address_label)
        form.addRow(_("Object Set: "), self.next_area_object_set_dropdown)

        form.addRow(QLabel(""))
        form.addRow(level_select_button)

        widget = QWidget()
        widget.setLayout(form)

        self.tab_widget.addTab(widget, _("Jump Destination"))

        self.header_bytes_label = QLabel()

        main_layout.addWidget(
            self.header_bytes_label, alignment=Qt.AlignmentFlag.AlignCenter
        )

        self.update()

    @property
    def undo_stack(self) -> QUndoStack:
        return self.parent().window().findChild(QUndoStack, "undo_stack")

    def update(self):
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
            hex(
                self.level.header.jump_object_set.level_offset
                + self.level_pointer_spinner.value()
            )
        )
        self.enemy_pointer_spinner.setValue(self.level.header.jump_enemy_offset)
        self._enemy_address_label.setText(
            hex(ENEMY_BASE_OFFSET + self.enemy_pointer_spinner.value())
        )
        self.next_area_object_set_dropdown.setCurrentIndex(
            self.level.next_area_object_set_no
        )

        self.blockSignals(False)

        self.header_bytes_label.setText(
            " ".join(f"{number:0=#4X}"[2:] for number in self.level.header_bytes)
        )

        self.level.data_changed.emit()

    def _set_level_attr(self, name: str, value, display_name="", display_value=""):
        self.undo_stack.push(
            SetLevelAttribute(self.level, name, value, display_name, display_value)
        )

    def _set_jump_destination(self):
        level_selector = LevelSelector(self)

        if self.level:
            level_selector.goto_world(self.level.world)

        level_was_selected = level_selector.exec() == QDialog.DialogCode.Accepted

        if not level_was_selected:
            return

        self.blockSignals(True)

        self.next_area_object_set_dropdown.setCurrentIndex(level_selector.object_set)
        self.level_pointer_spinner.setValue(level_selector.object_data_offset)
        self.enemy_pointer_spinner.setValue(level_selector.enemy_data_offset)

        self.blockSignals(False)

        level_address = level_selector.object_data_offset
        enemy_address = level_selector.enemy_data_offset
        object_set_number = level_selector.object_set

        make_macro(
            self.undo_stack,
            _("Set Next Area to %(level)s/%(enemy)s, %(object)s")
            % {
                "level": f"{level_address:#x}",
                "enemy": f"{enemy_address:#x}",
                "object": OBJECT_SET_NAMES[object_set_number],
            },
            SetNextAreaObjectSet(self.level, object_set_number),
            SetNextAreaObjectAddress(self.level, level_address),
            SetNextAreaEnemyAddress(self.level, enemy_address),
        )

        self.update()

    def on_spin(self, new_value):
        if self.level is None or self.signalsBlocked():
            return

        spinner = self.sender()

        if spinner == self.object_palette_spinner:
            self._set_level_attr("object_palette_index", new_value)

        elif spinner == self.enemy_palette_spinner:
            self._set_level_attr("enemy_palette_index", new_value)

        elif (
            spinner == self.level_pointer_spinner
            and new_value != self.level.header.jump_level_offset
        ):
            self.undo_stack.push(
                SetNextAreaObjectAddress(
                    self.level,
                    self.level.header.jump_object_set.level_offset + new_value,
                )
            )

        elif (
            spinner == self.enemy_pointer_spinner
            and new_value != self.level.header.jump_enemy_offset
        ):
            self.undo_stack.push(
                SetNextAreaEnemyAddress(self.level, ENEMY_BASE_OFFSET + new_value)
            )

        self.update()

    def on_combo(self, new_index):
        if self.level is None or self.signalsBlocked():
            return

        dropdown = self.sender()
        text = dropdown.currentText()

        # TODO do this via properties and get rid of the ifs?
        if (
            dropdown == self.length_dropdown
            and (new_length := LEVEL_LENGTHS[new_index]) != self.level.length
        ):
            self._set_level_attr("length", new_length, display_value=text)

        elif dropdown == self.music_dropdown and new_index != self.level.music_index:
            self._set_level_attr("music_index", new_index, display_value=text)

        elif dropdown == self.time_dropdown:
            self._set_level_attr("time_index", new_index, display_value=text)

        elif dropdown == self.camera_movement_dropdown:
            self._set_level_attr(
                "scroll_type",
                new_index,
                display_name=_("Camera Movement"),
                display_value=text,
            )

        elif dropdown == self.x_position_dropdown:
            self._set_level_attr(
                "start_x_index",
                new_index,
                display_name=_("Mario Start X"),
                display_value=text,
            )

        elif dropdown == self.y_position_dropdown:
            self._set_level_attr(
                "start_y_index",
                new_index,
                display_name=_("Mario Start Y"),
                display_value=text,
            )

        elif dropdown == self.action_dropdown:
            self._set_level_attr(
                "start_action",
                new_index,
                display_name=_("Mario Start Action"),
                display_value=text,
            )

        elif dropdown == self.graphic_set_dropdown:
            self._set_level_attr("graphic_set", new_index, display_value=text)

        elif (
            dropdown == self.next_area_object_set_dropdown
            and new_index != self.level.next_area_object_set_no
        ):
            object_set_cmd = SetNextAreaObjectSet(self.level, new_index)

            # in case the level address changes based on the new object set, don't list that command separately
            make_macro(self.undo_stack, object_set_cmd.text())
            self.undo_stack.push(object_set_cmd)

            self.undo_stack.endMacro()

        self.update()

    def on_check_box(self, checked):
        if self.level is None or self.signalsBlocked():
            return

        checkbox = self.sender()
        assert checked == checkbox.isChecked()

        if checkbox == self.pipe_ends_level_cb:
            self._set_level_attr("pipe_ends_level", checked)
        elif checkbox == self.level_is_vertical_cb:
            self._set_level_attr("is_vertical", checked, _("Level is Vertical"))

        self.update()
