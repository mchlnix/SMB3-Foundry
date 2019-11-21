from PySide2.QtGui import QCloseEvent, QKeyEvent, Qt
from PySide2.QtWidgets import QDialog, QLabel, QListWidget, QComboBox, QPushButton, QGridLayout

from foundry.game.level.Level import Level
from foundry.gui.Spinner import Spinner

WORLD_ITEMS = [
    "World Maps",
    "World 1",
    "World 2",
    "World 3",
    "World 4",
    "World 5",
    "World 6",
    "World 7",
    "World 8",
    "Lost Levels",
]

OBJECT_SET_ITEMS = [
    "0 Overworld",
    "1 Plains",
    "2 Dungeon",
    "3 Hilly",
    "4 Sky",
    "5 Piranha Plant",
    "6 Water",
    "7 Mushroom",
    "8 Pipe",
    "9 Desert",
    "A Ship",
    "B Giant",
    "C Ice",
    "D Cloudy",
    "E Underground",
    "F Spade Bonus",
]


OVERWORLD_MAPS_INDEX = 0
WORLD_1_INDEX = 1


class LevelSelector(QDialog):
    def __init__(self, parent):
        super(LevelSelector, self).__init__(parent)

        self.setWindowTitle("Level Selector")
        self.setModal(True)

        self.selected_world = 1
        self.selected_level = 1
        self.object_set = 0
        self.object_data_offset = 0x0
        self.enemy_data_offset = 0x0

        self.world_label = QLabel(parent=self, text="World")
        self.world_list = QListWidget(parent=self)
        self.world_list.addItems(WORLD_ITEMS)

        self.world_list.itemDoubleClicked.connect(self.on_ok)
        self.world_list.itemSelectionChanged.connect(self.on_world_click)

        self.level_label = QLabel(parent=self, text="Level")
        self.level_list = QListWidget(parent=self)

        self.level_list.itemDoubleClicked.connect(self.on_ok)
        self.level_list.itemSelectionChanged.connect(self.on_level_click)

        self.enemy_data_label = QLabel(parent=self, text="Enemy Data")
        self.enemy_data_spinner = Spinner(parent=self)

        self.object_data_label = QLabel(parent=self, text="Object Data")
        self.object_data_spinner = Spinner(self)

        self.object_set_label = QLabel(parent=self, text="Object Set")
        self.object_set_dropdown = QComboBox(self)
        self.object_set_dropdown.addItems(OBJECT_SET_ITEMS)

        self.button_ok = QPushButton("Ok", self)
        self.button_ok.clicked.connect(self.on_ok)
        self.button_cancel = QPushButton("Cancel", self)
        self.button_cancel.clicked.connect(self.close)

        self.window_layout = QGridLayout(self)

        self.window_layout.addWidget(self.world_label, 0, 0)
        self.window_layout.addWidget(self.level_label, 0, 1)

        self.window_layout.addWidget(self.world_list, 1, 0)
        self.window_layout.addWidget(self.level_list, 1, 1)

        self.window_layout.addWidget(self.enemy_data_label, 2, 0)
        self.window_layout.addWidget(self.object_data_label, 2, 1)
        self.window_layout.addWidget(self.enemy_data_spinner, 3, 0)
        self.window_layout.addWidget(self.object_data_spinner, 3, 1)

        self.window_layout.addWidget(self.object_set_label, 4, 0)
        self.window_layout.addWidget(self.object_set_dropdown, 4, 1)

        self.window_layout.addWidget(self.button_ok, 5, 0)
        self.window_layout.addWidget(self.button_cancel, 5, 1)

        self.setLayout(self.window_layout)

        self.world_list.setCurrentRow(1)  # select Level 1-1
        self.on_world_click()

    def keyPressEvent(self, key_event: QKeyEvent):
        if key_event.key() == Qt.Key_Escape:
            self.reject()

    def on_world_click(self):
        index = self.world_list.currentRow()

        assert index >= 0

        self.level_list.clear()

        # skip first meaningless item
        for level in Level.offsets[1:]:
            if level.game_world == index:
                if level.name:
                    self.level_list.addItem(level.name)

        if self.level_list.count():
            self.level_list.setCurrentRow(0)

            self.on_level_click()

    def on_level_click(self):
        index = self.level_list.currentRow()

        assert index >= 0

        self.selected_world = self.world_list.currentRow()
        self.selected_level = index + 1

        if self.selected_world == OVERWORLD_MAPS_INDEX:  # over-world maps
            level_array_offset = self.selected_level
        else:
            level_array_offset = Level.world_indexes[self.selected_world] + self.selected_level

        object_data_for_lvl = Level.offsets[level_array_offset].rom_level_offset

        if self.selected_world >= WORLD_1_INDEX:
            object_data_for_lvl -= Level.HEADER_LENGTH

        self.object_data_spinner.setValue(object_data_for_lvl)

        if self.selected_world >= WORLD_1_INDEX:
            enemy_data_for_lvl = Level.offsets[level_array_offset].enemy_offset
        else:
            enemy_data_for_lvl = 0

        if enemy_data_for_lvl > 0:
            enemy_data_for_lvl -= 1

        self.enemy_data_spinner.setValue(enemy_data_for_lvl)

        # if self.selected_world >= WORLD_1_INDEX:
        object_set_index = Level.offsets[level_array_offset].real_obj_set
        self.object_set_dropdown.setCurrentIndex(object_set_index)

        print(
            f"Level {self.selected_world}-{self.selected_level}, lvl_array_offset: {level_array_offset}, "
            f"obj_index: {object_set_index}"
        )

    def on_ok(self, _):
        self.object_set = self.object_set_dropdown.currentIndex()
        self.object_data_offset = self.object_data_spinner.value()
        # skip the first byte, because it seems useless
        self.enemy_data_offset = self.enemy_data_spinner.value() + 1

        self.accept()

    def closeEvent(self, _close_event: QCloseEvent):
        self.reject()
