from typing import List, Optional

from PySide2.QtWidgets import QCheckBox, QLabel, QVBoxLayout

from foundry.game.gfx.objects.EnemyItem import EnemyObject
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.CustomDialog import CustomDialog
from foundry.gui.Spinner import Spinner
from smb3parse.constants import OBJ_AUTOSCROLL

AUTOSCROLL_LABELS = {
    -1: "No Autoscroll in Level.",
    0: "Horizontal Autoscroll",
    1: "Horizontal Autoscroll",
    2: "Moves Level up and right; screen wraps, vertically",
    3: "Moves ceiling down and up (Fortress Spike Levels)",
    4: "Moves ground up, until a door hits the ground",
    5: "Moves ground up and down, used for changes in over-water Levels",
}


class AutoScrollEditor(CustomDialog):
    def __init__(self, parent, level_ref: LevelRef):
        super(AutoScrollEditor, self).__init__(parent, title="Autoscroll Editor")
        self.level_ref = level_ref

        self.original_autoscroll_item = _get_autoscroll(self.level_ref.enemies)

        QVBoxLayout(self)

        self.enabled_checkbox = QCheckBox("Enable Autoscroll in level", self)
        self.enabled_checkbox.toggled.connect(self._insert_autoscroll_object)

        self.y_position_spinner = Spinner(self, maximum=0x60 - 1)
        self.y_position_spinner.valueChanged.connect(self._update_y_position)

        self.auto_scroll_type_label = QLabel(self)

        self.layout().addWidget(self.enabled_checkbox)
        self.layout().addWidget(self.y_position_spinner)
        self.layout().addWidget(self.auto_scroll_type_label)

        self.update()

    def update(self):
        autoscroll_item = _get_autoscroll(self.level_ref.enemies)

        self.enabled_checkbox.setChecked(autoscroll_item is not None)
        self.y_position_spinner.setEnabled(autoscroll_item is not None)

        if autoscroll_item is None:
            self.auto_scroll_type_label.setText(AUTOSCROLL_LABELS[-1])
        else:
            self.y_position_spinner.setValue(autoscroll_item.y_position)
            self.auto_scroll_type_label.setText(AUTOSCROLL_LABELS[autoscroll_item.y_position >> 4])

    def _update_y_position(self, _):
        autoscroll_item = _get_autoscroll(self.level_ref.enemies)

        autoscroll_item.y_position = self.y_position_spinner.value()

        self.level_ref.data_changed.emit()

        self.update()

    def _insert_autoscroll_object(self, should_insert: bool):
        autoscroll_item = _get_autoscroll(self.level_ref.enemies)

        if autoscroll_item is not None:
            self.level_ref.enemies.remove(autoscroll_item)

        if should_insert:
            self.level_ref.enemies.insert(0, self._create_autoscroll_object())

        self.level_ref.data_changed.emit()

        self.update()

    def _create_autoscroll_object(self):
        return self.level_ref.level.enemy_item_factory.from_properties(
            OBJ_AUTOSCROLL, 0, self.y_position_spinner.value()
        )

    def closeEvent(self, event):
        current_autoscroll_item = _get_autoscroll(self.level_ref.enemies)

        if not (self.original_autoscroll_item is None and current_autoscroll_item is None):
            added_or_removed_autoscroll = self.original_autoscroll_item is None or current_autoscroll_item is None

            if (
                added_or_removed_autoscroll
                or self.original_autoscroll_item.y_position != current_autoscroll_item.y_position
            ):
                self.level_ref.save_level_state()

        super(AutoScrollEditor, self).closeEvent(event)


def _get_autoscroll(enemy_items: List[EnemyObject]) -> Optional[EnemyObject]:
    for item in enemy_items:
        if item.obj_index == OBJ_AUTOSCROLL:
            return item
    else:
        return None
