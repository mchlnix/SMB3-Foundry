from typing import Optional

from PySide6.QtGui import QMouseEvent, QPixmap
from PySide6.QtWidgets import QCheckBox, QComboBox, QGroupBox, QVBoxLayout

from foundry.game.gfx.objects import EnemyItem
from foundry.game.level.Level import Level
from foundry.gui import label_and_widget
from foundry.gui.commands import AddObject, MoveObjects, RemoveObjects
from foundry.gui.level_settings.settings_mixin import SettingsMixin
from smb3parse.constants import (
    MAPITEM_MUSHROOM,
    MAPITEM_MUSICBOX,
    MAPITEM_NAMES,
    MAP_ITEM_SPRITES,
    OBJ_CHEST_EXIT,
    OBJ_CHEST_ITEM_SETTER,
)


class _ChestState:
    def __init__(self, level: Level):
        self.level = level

        self.chest_exit = self._get_chest_exit()
        self.chest_item = self._get_chest_item()

    @property
    def item_index(self):
        if self.chest_item:
            return self.chest_item.y_position - 1
        else:
            return -2

    @property
    def had_exit(self):
        return self.chest_exit is not None

    @property
    def had_item(self):
        return self.chest_item is not None

    def _get_chest_exit(self) -> Optional[EnemyItem]:
        for item in self.level.enemies:
            if item.obj_index == OBJ_CHEST_EXIT:
                return item
        else:
            return None

    def _get_chest_item(self) -> Optional[EnemyItem]:
        for item in self.level.enemies:
            if item.obj_index == OBJ_CHEST_ITEM_SETTER:
                return item
        else:
            return None


class ChestExitMixin(SettingsMixin):
    def __init__(self, parent):
        super(ChestExitMixin, self).__init__(parent)

        self.before = _ChestState(self.level_ref.level)

        chest_group = QGroupBox("Treasure Chest", self)
        QVBoxLayout(chest_group)

        self.chest_end_checkbox = QCheckBox("Getting Chest ends Level", self)
        self.chest_end_checkbox.setChecked(self.before.had_exit)
        self.chest_end_checkbox.toggled.connect(self._update_chest_dropdown)

        self.chest_item_dropdown = QComboBox()

        # y-position of 0 is invalid, so start at 1 and adapt the dropdown index accordingly
        for item_id in range(MAPITEM_MUSHROOM, MAPITEM_MUSICBOX + 1):
            self.chest_item_dropdown.addItem(QPixmap(MAP_ITEM_SPRITES[item_id]), MAPITEM_NAMES[item_id])

        self.chest_item_dropdown.setCurrentIndex(self.before.item_index)

        chest_group.layout().addWidget(self.chest_end_checkbox)
        chest_group.layout().addLayout(label_and_widget("Item in Chest: ", self.chest_item_dropdown))

        self._update_chest_dropdown()

        self.layout().addWidget(chest_group)

    def _update_chest_dropdown(self):
        self.chest_item_dropdown.setEnabled(self.chest_end_checkbox.isChecked())

    def closeEvent(self, event: QMouseEvent):
        chest_item_name = MAPITEM_NAMES[self.chest_item_dropdown.currentIndex() + 1]

        # stayed disabled
        if not self.chest_end_checkbox.isChecked() and not self.before.had_exit:
            pass

        # was disabled
        elif not self.chest_end_checkbox.isChecked() and self.before.had_exit:
            self.undo_stack.beginMacro("Disabling Chest Exit")
            self.undo_stack.push(RemoveObjects(self.level_ref.level, [self.before.chest_exit]))

            if self.before.had_item:
                self.undo_stack.push(RemoveObjects(self.level_ref.level, [self.before.chest_item]))

            self.undo_stack.endMacro()

        # was enabled
        elif self.chest_end_checkbox.isChecked() and not self.before.chest_exit:
            self.undo_stack.beginMacro(f"Enable Chest Exit with '{chest_item_name}'")
            self.undo_stack.push(
                AddObject(
                    self.level_ref.level,
                    self.level_ref.level.enemy_item_factory.from_properties(OBJ_CHEST_EXIT, 0, 0),
                )
            )

            self.undo_stack.push(
                AddObject(
                    self.level_ref.level,
                    self.level_ref.level.enemy_item_factory.from_properties(
                        OBJ_CHEST_ITEM_SETTER, 0, self.chest_item_dropdown.currentIndex() + 1
                    ),
                )
            )

            self.undo_stack.endMacro()

        # just changed item
        elif self.before.item_index != self.chest_item_dropdown.currentIndex():
            self.undo_stack.beginMacro(f"Set Chest Item to '{chest_item_name}'")

            if self.before.had_item:
                before_move = self.before.chest_item.copy()
                self.before.chest_item.y_position = self.chest_item_dropdown.currentIndex() + 1

                self.undo_stack.push(MoveObjects(self.level_ref.level, [before_move], [self.before.chest_item]))
            else:
                self.undo_stack.push(
                    AddObject(
                        self.level_ref.level,
                        self.level_ref.level.enemy_item_factory.from_properties(
                            OBJ_CHEST_ITEM_SETTER, 0, self.chest_item_dropdown.currentIndex() + 1
                        ),
                    )
                )

            self.undo_stack.endMacro()

        self.level_ref.level.data_changed.emit()

        super(ChestExitMixin, self).closeEvent(event)
