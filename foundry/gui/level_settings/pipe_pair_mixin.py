from typing import Optional

from PySide6.QtWidgets import QCheckBox, QDialog, QGroupBox, QLabel, QMessageBox, QPushButton, QTabWidget, QVBoxLayout

from foundry import icon
from foundry.game.File import ROM
from foundry.game.gfx.objects import EnemyItem
from foundry.gui import label_and_widget
from foundry.gui.LevelSelector import WorldMapLevelSelect
from foundry.gui.Spinner import Spinner
from foundry.gui.commands import AddObject, RemoveObjects, UpdatePipeData
from foundry.gui.level_settings.settings_mixin import SettingsMixin
from smb3parse.constants import OBJ_PIPE_EXITS, PIPE_PAIR_COUNT
from smb3parse.data_points import Position
from smb3parse.data_points.pipe_data import PipeData
from smb3parse.levels import WORLD_COUNT


class PipePairMixin(SettingsMixin):
    def __init__(self, parent):
        super(PipePairMixin, self).__init__(parent)

        pipe_pair_group = QGroupBox("Pipe Pair Exits")
        QVBoxLayout(pipe_pair_group)

        self.pipe_datas = [PipeData(ROM(), index) for index in range(PIPE_PAIR_COUNT)]
        self.pipe_data_changed = False

        self.original_pipe_item = _get_pipe_item(self.level_ref.enemies)
        if self.original_pipe_item is None:
            self.original_pipe_y_value = -1
        else:
            self.original_pipe_y_value = self.original_pipe_item.y_position

        self.pipe_pair_check_box = QCheckBox("Enable exiting somewhere else on WorldMap")
        self.pipe_pair_check_box.setChecked(self.original_pipe_item is not None)
        self.pipe_pair_check_box.clicked.connect(self._on_pipe_check_box)
        pipe_pair_group.layout().addWidget(self.pipe_pair_check_box)

        self.sky_tower_check_box = QCheckBox("Like Sky Tower (Top and Bottom, instead of Left and Right)")
        self.sky_tower_check_box.clicked.connect(self._on_update_y_position)
        pipe_pair_group.layout().addWidget(self.sky_tower_check_box)

        self.pipe_pair_spinner = Spinner(self, maximum=PIPE_PAIR_COUNT - 1)
        self.pipe_pair_spinner.valueChanged.connect(self._on_update_y_position)
        pipe_pair_group.layout().addLayout(label_and_widget("Pipe Pair Index", self.pipe_pair_spinner))

        self.left_pos_label = QLabel("-")
        pipe_pair_group.layout().addLayout(label_and_widget("Left Exit", self.left_pos_label))

        self.right_pos_label = QLabel("-")
        pipe_pair_group.layout().addLayout(label_and_widget("Right Exit", self.right_pos_label))

        self.set_new_button = QPushButton("Change Exit Locations")
        self.set_new_button.clicked.connect(self._on_set_pipe_exits)
        pipe_pair_group.layout().addWidget(self.set_new_button)

        self._update_position_labels()

        self.layout().addWidget(pipe_pair_group)

    def _on_pipe_check_box(self, checked):
        if checked:
            self.level_ref.level.add_enemy(OBJ_PIPE_EXITS, Position.from_xy(0, 0))
        else:
            self.level_ref.level.remove_object(_get_pipe_item(self.level_ref.enemies))

        self._update_position_labels()

    def _on_set_pipe_exits(self):
        QMessageBox.information(
            self, "Select Pipe Pair Exit", "On the next screen, choose where the Left/Top Exit should lead to."
        )
        left_pair_screen = PipeExitSetScreen(self)
        left_pair_screen.current_world = self.level_ref.level.world
        left_pair_screen.exec()

        QMessageBox.information(
            self, "Select Pipe Pair Exit", "On the next screen, choose where the Right/Bottom Exit should lead to."
        )
        right_pair_screen = PipeExitSetScreen(self)
        right_pair_screen.current_world = left_pair_screen.current_world
        right_pair_screen.exec()

        pipe_item = _get_pipe_item(self.level_ref.enemies)
        assert pipe_item is not None

        pipe_data = self.pipe_datas[pipe_item.y_position]

        pipe_data.left_pos = left_pair_screen.selected_position
        pipe_data.right_pos = right_pair_screen.selected_position
        self.pipe_data_changed = True

        self._update_position_labels()

    def _on_update_y_position(self):
        pipe_item = _get_pipe_item(self.level_ref.enemies)

        if pipe_item is not None:
            new_value = self.pipe_pair_spinner.value()

            if self.sky_tower_check_box.isChecked():
                new_value += 0x80

            pipe_item.y_position = new_value

        self._update_position_labels()

    def _update_position_labels(self):
        pipe_item = _get_pipe_item(self.level_ref.enemies)

        self.sky_tower_check_box.setEnabled(pipe_item is not None)
        self.sky_tower_check_box.setChecked(pipe_item is not None and pipe_item.y_position & 0x80 == 0x80)
        self.pipe_pair_spinner.setEnabled(pipe_item is not None)
        self.set_new_button.setEnabled(pipe_item is not None)

        if pipe_item is None:
            self.left_pos_label.setText("-")
            self.right_pos_label.setText("-")

            self.pipe_pair_spinner.setValue(0)
        else:
            self.pipe_pair_spinner.setValue(pipe_item.y_position % 0x80)

            pipe_data = self.pipe_datas[pipe_item.y_position]

            self.left_pos_label.setText(
                f"Screen: {pipe_data.screen_left}, x: {pipe_data.x_left}, y: {pipe_data.y_left}"
            )
            self.right_pos_label.setText(
                f"Screen: {pipe_data.screen_right}, x: {pipe_data.x_right}, y: {pipe_data.y_right}"
            )

        self.level_ref.data_changed.emit()

    def closeEvent(self, event):
        super(PipePairMixin, self).closeEvent(event)

        current_pipe_item = _get_pipe_item(self.level_ref.enemies)

        pipe_kept_disabled = self.original_pipe_item is current_pipe_item is None
        pipe_was_disabled = self.original_pipe_item is not None and current_pipe_item is None
        pipe_was_enabled = self.original_pipe_item is None and current_pipe_item is not None

        if pipe_kept_disabled:
            pass
        elif pipe_was_disabled:
            assert self.original_pipe_item

            self.level_ref.level.enemies.insert(0, self.original_pipe_item)

            self.undo_stack.beginMacro("Disable Pipe Pair Exits")
            self.undo_stack.push(RemoveObjects(self.level_ref.level, [self.original_pipe_item]))
            self.undo_stack.endMacro()

        elif pipe_was_enabled:
            assert current_pipe_item is not None

            self.level_ref.level.remove_object(current_pipe_item)

            self.undo_stack.beginMacro("Enable Pipe Pair Exits")
            self.undo_stack.push(AddObject(self.level_ref.level, current_pipe_item, 0))
            self.undo_stack.endMacro()

        else:
            assert self.original_pipe_item is not None

            if current_pipe_item is self.original_pipe_item:
                current_pipe_item = self.original_pipe_item.copy()
            else:
                self.level_ref.level.remove_object(current_pipe_item)
                self.level_ref.level.enemies.append(self.original_pipe_item)

            assert current_pipe_item is not None

            if self.original_pipe_y_value != current_pipe_item.y_position:
                assert self.original_pipe_item is not current_pipe_item

                self.original_pipe_item.y_position = self.original_pipe_y_value
                self.undo_stack.beginMacro(f"Pipe Pair Exits Index to {current_pipe_item.y_position:#x}")

                self.undo_stack.push(RemoveObjects(self.level_ref.level, [self.original_pipe_item]))
                self.undo_stack.push(AddObject(self.level_ref.level, current_pipe_item))

                self.undo_stack.endMacro()

        if self.pipe_data_changed:
            self.undo_stack.push(UpdatePipeData(self.pipe_datas))


class PipeExitSetScreen(QDialog):
    def __init__(self, parent):
        super(PipeExitSetScreen, self).__init__(parent)

        self.selected_position = Position.from_xy(0, 0)

        self.world_tabs = QTabWidget()

        for world_number in range(WORLD_COUNT - 1):
            world_number += 1

            world_map_select = WorldMapLevelSelect(world_number)
            world_map_select.ignore_levels = True
            world_map_select.map_position_clicked.connect(self._set_position)
            world_map_select.map_position_clicked.connect(self.accept)

            self.world_tabs.addTab(world_map_select, f"World {world_number}")
            self.world_tabs.setTabIcon(world_number, icon("globe.svg"))

        self.setLayout(QVBoxLayout())

        self.layout().addWidget(self.world_tabs)

    @property
    def current_world(self):
        return self.world_tabs.currentIndex() + 1

    @current_world.setter
    def current_world(self, value):
        if value not in range(1, WORLD_COUNT + 1):
            return

        self.world_tabs.setCurrentIndex(value - 1)

    def _set_position(self, pos: Position):
        self.selected_position = pos.copy()


def _get_pipe_item(enemy_items: list[EnemyItem]) -> Optional[EnemyItem]:
    for item in enemy_items:
        if item.obj_index == OBJ_PIPE_EXITS:
            return item
    else:
        return None
