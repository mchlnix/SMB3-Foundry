from typing import Optional

from PySide6.QtGui import QUndoStack, Qt
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

from foundry.game.gfx.GraphicsSet import GRAPHIC_SET_NAMES
from foundry.game.level.Level import Level
from foundry.game.level.LevelRef import LevelRef
from foundry.gui import OBJECT_SET_ITEMS
from foundry.gui.CustomDialog import CustomDialog
from foundry.gui.LevelSelector import LevelSelector
from foundry.gui.Spinner import Spinner
from foundry.gui.commands import (
    SetLevelAttribute,
    SetNextAreaEnemyAddress,
    SetNextAreaObjectAddress,
    SetNextAreaObjectSet,
)
from smb3parse.levels.level_header import MARIO_X_POSITIONS, MARIO_Y_POSITIONS
from smb3parse.objects.object_set import OBJECT_SET_NAMES

LEVEL_LENGTHS = [0x10 * (i + 1) for i in range(0, 2**4)]
STR_LEVEL_LENGTHS = [f"{length - 1:0=#4X} / {length} Blocks".replace("X", "x") for length in LEVEL_LENGTHS]

STR_X_POSITIONS = [f"{position >> 4}. Block ({position:0=#4X})".replace("X", "x") for position in MARIO_X_POSITIONS]

STR_Y_POSITIONS = [f"{position}. Block ({position:0=#4X})".replace("X", "x") for position in MARIO_Y_POSITIONS]

ACTIONS = [
    "None",
    "Sliding",
    "Out of pipe ↑",
    "Out of pipe ↓",
    "Out of pipe ←",
    "Out of pipe →",
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


class HeaderEditor(CustomDialog):
    def __init__(self, parent: Optional[QWidget], level_ref: LevelRef):
        super(HeaderEditor, self).__init__(parent, "Level Header Editor")

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
        form.setFormAlignment(Qt.AlignCenter)

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
        form.setFormAlignment(Qt.AlignCenter)

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
        form.setFormAlignment(Qt.AlignCenter)

        form.addRow("Object Palette: ", self.object_palette_spinner)
        form.addRow("Enemy Palette: ", self.enemy_palette_spinner)
        form.addRow("Graphic Set: ", self.graphic_set_dropdown)

        widget = QWidget()
        widget.setLayout(form)

        self.tab_widget.addTab(widget, "Graphics")

        # next area settings
        self.level_pointer_spinner = Spinner(self)
        self.level_pointer_spinner.valueChanged.connect(self.on_spin)

        self.enemy_pointer_spinner = Spinner(self)
        self.enemy_pointer_spinner.valueChanged.connect(self.on_spin)
        self.enemy_pointer_spinner.setMinimum(0)
        self.enemy_pointer_spinner.setMaximum(0xFFFF)

        self.next_area_object_set_dropdown = QComboBox()
        self.next_area_object_set_dropdown.addItems(OBJECT_SET_ITEMS)
        self.next_area_object_set_dropdown.activated.connect(self.on_combo)

        level_select_button = QPushButton("Set from Level")
        level_select_button.pressed.connect(self._set_jump_destination)

        form = QFormLayout()
        form.setFormAlignment(Qt.AlignCenter)

        form.addRow("Address of Objects: ", self.level_pointer_spinner)
        form.addRow("Address of Enemies: ", self.enemy_pointer_spinner)
        form.addRow("Object Set: ", self.next_area_object_set_dropdown)

        form.addRow(QLabel(""))
        form.addRow(level_select_button)

        widget = QWidget()
        widget.setLayout(form)

        self.tab_widget.addTab(widget, "Jump Destination")

        self.header_bytes_label = QLabel()

        main_layout.addWidget(self.header_bytes_label, alignment=Qt.AlignCenter)

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

        self.level_pointer_spinner.setValue(self.level.next_area_objects)
        self.enemy_pointer_spinner.setValue(self.level.next_area_enemies)
        self.next_area_object_set_dropdown.setCurrentIndex(self.level.next_area_object_set)

        self.blockSignals(False)

        self.header_bytes_label.setText(" ".join(f"{number:0=#4X}"[2:] for number in self.level.header_bytes))

        self.level.data_changed.emit()

    def _set_level_attr(self, name: str, value, display_name="", display_value=""):
        self.undo_stack.push(SetLevelAttribute(self.level, name, value, display_name, display_value))

    def _set_jump_destination(self):
        level_selector = LevelSelector(self)

        if self.level:
            level_selector.goto_world(self.level.world)

        level_was_selected = level_selector.exec() == QDialog.Accepted

        if not level_was_selected:
            return

        self.blockSignals(True)

        self.next_area_object_set_dropdown.setCurrentIndex(level_selector.object_set)
        self.level_pointer_spinner.setValue(level_selector.object_data_offset)
        self.enemy_pointer_spinner.setValue(level_selector.enemy_data_offset)

        self.blockSignals(False)

        level_address = level_selector.object_data_offset
        enemy_address = level_selector.enemy_data_offset - 1
        object_set_number = level_selector.object_set

        self.undo_stack.beginMacro(
            f"Set Next Area to {hex(level_address)}/{hex(enemy_address)}, {OBJECT_SET_NAMES[object_set_number]}"
        )

        self.undo_stack.push(SetNextAreaObjectSet(self.level, object_set_number))
        self.undo_stack.push(SetNextAreaObjectAddress(self.level, level_address))
        self.undo_stack.push(SetNextAreaEnemyAddress(self.level, enemy_address))

        self.undo_stack.endMacro()

        self.update()

    def on_spin(self, new_value):
        if self.level is None or self.signalsBlocked():
            return

        spinner = self.sender()

        if spinner == self.object_palette_spinner:
            self._set_level_attr("object_palette_index", new_value)

        elif spinner == self.enemy_palette_spinner:
            self._set_level_attr("enemy_palette_index", new_value)

        elif spinner == self.level_pointer_spinner and new_value != self.level.next_area_objects:
            self.undo_stack.push(SetNextAreaObjectAddress(self.level, new_value))

        elif spinner == self.enemy_pointer_spinner and new_value != self.level.next_area_enemies:
            self.undo_stack.push(SetNextAreaEnemyAddress(self.level, new_value))

        self.update()

    def on_combo(self, new_index):
        if self.level is None or self.signalsBlocked():
            return

        dropdown = self.sender()
        text = dropdown.currentText()

        # TODO do this via properties and get rid of the ifs?
        if dropdown == self.length_dropdown and (new_length := LEVEL_LENGTHS[new_index]) != self.level.length:
            self._set_level_attr("length", new_length, display_value=text)

        elif dropdown == self.music_dropdown and new_index != self.level.music_index:
            self._set_level_attr("music_index", new_index, display_value=text)

        elif dropdown == self.time_dropdown:
            self._set_level_attr("time_index", new_index, display_value=text)

        elif dropdown == self.camera_movement_dropdown:
            self._set_level_attr("scroll_type", new_index, display_name="Camera Movement", display_value=text)

        elif dropdown == self.x_position_dropdown:
            self._set_level_attr("start_x_index", new_index, display_name="Mario Start X", display_value=text)

        elif dropdown == self.y_position_dropdown:
            self._set_level_attr("start_y_index", new_index, display_name="Mario Start Y", display_value=text)

        elif dropdown == self.action_dropdown:
            self._set_level_attr("start_action", new_index, display_name="Mario Start Action", display_value=text)

        elif dropdown == self.graphic_set_dropdown:
            self._set_level_attr("graphic_set", new_index, display_value=text)

        elif dropdown == self.next_area_object_set_dropdown and new_index != self.level.next_area_object_set:
            object_set_cmd = SetNextAreaObjectSet(self.level, new_index)

            # in case the level address changes based on the new object set, don't list that command separately
            self.undo_stack.beginMacro(object_set_cmd.text())
            self.undo_stack.push(object_set_cmd)

            # update min and max, based on new object set
            min_level_address = self.level.header.jump_object_set.level_offset
            self.level_pointer_spinner.setMinimum(min_level_address)
            self.level_pointer_spinner.setMaximum(min_level_address + 0xFFFF)

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
            self._set_level_attr("is_vertical", checked, "Level is Vertical")

        self.update()
