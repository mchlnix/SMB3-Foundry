from typing import Optional

from PySide2.QtCore import Signal, SignalInstance
from PySide2.QtGui import QWindow, Qt
from PySide2.QtWidgets import (
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
from foundry.gui.CustomDialog import CustomDialog
from foundry.gui.LevelSelector import LevelSelector, OBJECT_SET_ITEMS
from foundry.gui.Spinner import Spinner
from smb3parse.levels.level_header import MARIO_X_POSITIONS, MARIO_Y_POSITIONS

LEVEL_LENGTHS = [0x10 * (i + 1) for i in range(0, 2 ** 4)]
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

TIMES = ["300", "400", "200", "Unlimited"]

SCROLL_DIRECTIONS = [
    "Locked, unless climbing/flying",
    "Free vertical scrolling",
    "Locked 'by start coordinates'?",
    "Shouldn't appear in game, do not use.",
]


SPINNER_MAX_VALUE = 0x0F_FF_FF


class HeaderEditor(CustomDialog):
    header_change: SignalInstance = Signal()

    def __init__(self, parent: Optional[QWindow], level_ref: LevelRef):
        super(HeaderEditor, self).__init__(parent, "Level Header Editor")

        self.level: Level = level_ref.level

        # enables undo
        self.header_change.connect(level_ref.save_level_state)

        main_layout = QVBoxLayout(self)

        tab_widget = QTabWidget(self)
        main_layout.addWidget(tab_widget)

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

        self.v_scroll_direction_dropdown = QComboBox()
        self.v_scroll_direction_dropdown.addItems(SCROLL_DIRECTIONS)
        self.v_scroll_direction_dropdown.activated.connect(self.on_combo)

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

        form.addRow("Level length: ", self.length_dropdown)
        form.addRow("Music: ", self.music_dropdown)
        form.addRow("Time: ", self.time_dropdown)
        form.addRow("Scroll direction: ", self.v_scroll_direction_dropdown)

        form.addWidget(check_box_widget)

        widget = QWidget()
        widget.setLayout(form)

        tab_widget.addTab(widget, "Level")

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

        tab_widget.addTab(widget, "Mario")

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

        tab_widget.addTab(widget, "Graphics")

        # next area settings

        self.level_pointer_spinner = Spinner(self, maximum=SPINNER_MAX_VALUE)
        self.level_pointer_spinner.valueChanged.connect(self.on_spin)
        self.enemy_pointer_spinner = Spinner(self, maximum=SPINNER_MAX_VALUE)
        self.enemy_pointer_spinner.valueChanged.connect(self.on_spin)

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

        tab_widget.addTab(widget, "Jump Destination")

        self.header_bytes_label = QLabel()

        main_layout.addWidget(self.header_bytes_label, alignment=Qt.AlignCenter)

        self.update()

    def update(self):
        length_index = LEVEL_LENGTHS.index(self.level.length)

        self.length_dropdown.setCurrentIndex(length_index)
        self.music_dropdown.setCurrentIndex(self.level.music_index)
        self.time_dropdown.setCurrentIndex(self.level.time_index)
        self.v_scroll_direction_dropdown.setCurrentIndex(self.level.scroll_type)
        self.level_is_vertical_cb.setChecked(self.level.is_vertical)
        self.pipe_ends_level_cb.setChecked(self.level.pipe_ends_level)

        self.x_position_dropdown.setCurrentIndex(self.level.start_x_index)
        self.y_position_dropdown.setCurrentIndex(self.level.start_y_index)
        self.action_dropdown.setCurrentIndex(self.level.start_action)

        self.object_palette_spinner.setValue(self.level.object_palette_index)
        self.enemy_palette_spinner.setValue(self.level.enemy_palette_index)
        self.graphic_set_dropdown.setCurrentIndex(self.level.graphic_set)

        self.level_pointer_spinner.setValue(self.level.next_area_objects)
        self.enemy_pointer_spinner.setValue(self.level.next_area_enemies)
        self.next_area_object_set_dropdown.setCurrentIndex(self.level.next_area_object_set)

        self.header_bytes_label.setText(" ".join(f"{number:0=#4X}"[2:] for number in self.level.header_bytes))

    def _set_jump_destination(self):
        level_selector = LevelSelector(self)
        level_was_selected = level_selector.exec_() == QDialog.Accepted

        if not level_was_selected:
            return

        self.next_area_object_set_dropdown.setCurrentIndex(level_selector.object_set)
        self.level.next_area_object_set = level_selector.object_set

        self.level_pointer_spinner.setValue(level_selector.object_data_offset)
        self.level.next_area_objects = level_selector.object_data_offset

        self.enemy_pointer_spinner.setValue(level_selector.enemy_data_offset)
        self.level.next_area_enemies = level_selector.enemy_data_offset - 1

        self.header_change.emit()

    def on_spin(self, _):
        if self.level is None:
            return

        spinner = self.sender()

        self.level.data_changed.connect(self.header_change.emit)

        if spinner == self.object_palette_spinner:
            new_index = self.object_palette_spinner.value()
            self.level.object_palette_index = new_index

        elif spinner == self.enemy_palette_spinner:
            new_index = self.enemy_palette_spinner.value()
            self.level.enemy_palette_index = new_index

        elif spinner == self.level_pointer_spinner:
            new_offset = self.level_pointer_spinner.value()
            self.level.next_area_objects = new_offset

        elif spinner == self.enemy_pointer_spinner:
            new_offset = self.enemy_pointer_spinner.value()
            self.level.next_area_enemies = new_offset

        self.level.data_changed.disconnect(self.header_change.emit)

        self.update()

    def on_combo(self, _):
        dropdown = self.sender()

        self.level.data_changed.connect(self.header_change.emit)

        if dropdown == self.length_dropdown:
            new_length = LEVEL_LENGTHS[self.length_dropdown.currentIndex()]
            self.level.length = new_length

        elif dropdown == self.music_dropdown:
            new_music = self.music_dropdown.currentIndex()
            self.level.music_index = new_music

        elif dropdown == self.time_dropdown:
            new_time = self.time_dropdown.currentIndex()
            self.level.time_index = new_time

        elif dropdown == self.v_scroll_direction_dropdown:
            new_scroll = self.v_scroll_direction_dropdown.currentIndex()
            self.level.scroll_type = new_scroll

        elif dropdown == self.x_position_dropdown:
            new_x = self.x_position_dropdown.currentIndex()
            self.level.start_x_index = new_x

        elif dropdown == self.y_position_dropdown:
            new_y = self.y_position_dropdown.currentIndex()
            self.level.start_y_index = new_y

        elif dropdown == self.action_dropdown:
            new_action = self.action_dropdown.currentIndex()
            self.level.start_action = new_action

        elif dropdown == self.graphic_set_dropdown:
            new_gfx_set = self.graphic_set_dropdown.currentIndex()
            self.level.graphic_set = new_gfx_set

        elif dropdown == self.next_area_object_set_dropdown:
            new_object_set = self.next_area_object_set_dropdown.currentIndex()
            self.level.next_area_object_set = new_object_set

        self.level.data_changed.disconnect(self.header_change.emit)

        self.update()

    def on_check_box(self, _):
        checkbox = self.sender()

        self.level.data_changed.connect(self.header_change.emit)

        if checkbox == self.pipe_ends_level_cb:
            self.level.pipe_ends_level = self.pipe_ends_level_cb.isChecked()
        elif checkbox == self.level_is_vertical_cb:
            self.level.is_vertical = self.level_is_vertical_cb.isChecked()

        self.level.data_changed.disconnect(self.header_change.emit)

        self.update()
