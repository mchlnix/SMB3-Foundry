from typing import Optional

from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QCheckBox, QGroupBox, QLabel, QVBoxLayout

from foundry.game.gfx.objects import EnemyItem
from foundry.gui import label_and_widget
from foundry.gui.commands import AddObject, RemoveObjects
from foundry.gui.level_settings.settings_mixin import SettingsMixin
from foundry.gui.widgets.Spinner import Spinner
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


class AutoScrollMixin(SettingsMixin):
    def __init__(self, parent):
        super(AutoScrollMixin, self).__init__(parent)

        self.original_autoscroll_item = _get_autoscroll(self.level_ref.enemies)
        self.original_scroll_type = (
            self.original_autoscroll_item.auto_scroll_type if self.original_autoscroll_item else -1
        )

        # Autoscroll
        auto_scroll_group = QGroupBox("Autoscrolling", self)
        QVBoxLayout(auto_scroll_group)

        self.enabled_checkbox = QCheckBox("Enable Autoscroll in Level", self)
        self.enabled_checkbox.toggled.connect(self._insert_autoscroll_object)

        self.auto_scroll_type_spinner = Spinner(self, maximum=0x60 - 1)
        self.auto_scroll_type_spinner.valueChanged.connect(self._update_auto_scroll_type)

        self.auto_scroll_type_label = QLabel(self)

        auto_scroll_group.layout().addWidget(self.enabled_checkbox)
        auto_scroll_group.layout().addLayout(label_and_widget("Scroll Type: ", self.auto_scroll_type_spinner))
        auto_scroll_group.layout().addWidget(self.auto_scroll_type_label)

        self.layout().addWidget(auto_scroll_group)

    def update(self):
        # auto scroll
        autoscroll_item = _get_autoscroll(self.level_ref.enemies)

        self.enabled_checkbox.setChecked(autoscroll_item is not None)
        self.auto_scroll_type_spinner.setEnabled(autoscroll_item is not None)

        if autoscroll_item is None:
            self.auto_scroll_type_label.setText(AUTOSCROLL_LABELS[-1])
        else:
            self.auto_scroll_type_spinner.setValue(autoscroll_item.auto_scroll_type)
            self.auto_scroll_type_label.setText(AUTOSCROLL_LABELS[autoscroll_item.auto_scroll_type >> 4])

        super(AutoScrollMixin, self).update()

    def _update_auto_scroll_type(self, _):
        autoscroll_item = _get_autoscroll(self.level_ref.enemies)
        assert autoscroll_item is not None

        autoscroll_item.auto_scroll_type = self.auto_scroll_type_spinner.value()

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
            OBJ_AUTOSCROLL, 0, self.auto_scroll_type_spinner.value()
        )

    def closeEvent(self, event: QMouseEvent):
        current_autoscroll_item = _get_autoscroll(self.level_ref.enemies)

        autoscroll_kept_disabled = self.original_autoscroll_item is current_autoscroll_item is None
        autoscroll_was_disabled = self.original_autoscroll_item is not None and current_autoscroll_item is None
        autoscroll_was_enabled = self.original_autoscroll_item is None and current_autoscroll_item is not None

        if autoscroll_kept_disabled:
            # nothing to do
            pass
        elif autoscroll_was_disabled:
            assert self.original_autoscroll_item is not None

            self.level_ref.level.enemies.insert(0, self.original_autoscroll_item)
            self.undo_stack.push(RemoveObjects(self.level_ref.level, [self.original_autoscroll_item]))
        elif autoscroll_was_enabled:
            assert current_autoscroll_item is not None
            self.level_ref.level.remove_object(current_autoscroll_item)
            self.undo_stack.push(AddObject(self.level_ref.level, current_autoscroll_item, 0))
        else:
            # autoscroll object might have been changed, first reset state from the start
            assert self.original_autoscroll_item is not None

            if current_autoscroll_item is self.original_autoscroll_item:
                current_autoscroll_item = self.original_autoscroll_item.copy()
            else:
                self.level_ref.level.remove_object(current_autoscroll_item)
                self.level_ref.level.enemies.insert(0, self.original_autoscroll_item)

            assert current_autoscroll_item is not None

            if self.original_scroll_type != current_autoscroll_item.auto_scroll_type:
                assert self.original_autoscroll_item is not current_autoscroll_item

                self.undo_stack.beginMacro("Change Autoscroll Path")

                self.undo_stack.push(RemoveObjects(self.level_ref.level, [self.original_autoscroll_item]))
                self.undo_stack.push(AddObject(self.level_ref.level, current_autoscroll_item, 0))

                self.undo_stack.endMacro()

        super(AutoScrollMixin, self).closeEvent(event)


def _get_autoscroll(enemy_items: list[EnemyItem]) -> Optional[EnemyItem]:
    for item in enemy_items:
        if item.obj_index == OBJ_AUTOSCROLL:
            return item
    else:
        return None
