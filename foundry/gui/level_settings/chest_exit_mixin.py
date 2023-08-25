from typing import Optional

from PySide6.QtGui import QMouseEvent, QPixmap
from PySide6.QtWidgets import QCheckBox, QComboBox, QGroupBox, QVBoxLayout

from foundry.game.gfx.objects import EnemyItem
from foundry.game.gfx.objects.world_map.sprite import MAP_ITEM_SPRITES
from foundry.game.level.Level import Level
from foundry.gui import label_and_widget
from foundry.gui.commands import AddObject, MoveObject, RemoveObject
from foundry.gui.level_settings.settings_mixin import SettingsMixin
from smb3parse.constants import (
    MAPITEM_MUSHROOM,
    MAPITEM_MUSICBOX,
    MAPITEM_NAMES,
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
            return self.chest_item.y_position
        else:
            return -2

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
        self.chest_end_checkbox.setChecked(self.before.chest_exit is not None)

        self.chest_item_dropdown = QComboBox()
        self.chest_item_dropdown.addItem("No Item (Hammer Bros Levels)")

        for item_id in range(MAPITEM_MUSHROOM, MAPITEM_MUSICBOX + 1):
            self.chest_item_dropdown.addItem(QPixmap(MAP_ITEM_SPRITES[item_id]), MAPITEM_NAMES[item_id])

        if self.before.chest_item is not None:
            self.chest_item_dropdown.setCurrentIndex(self.before.item_index)
        else:
            self.chest_item_dropdown.setCurrentIndex(0)

        chest_group.layout().addWidget(self.chest_end_checkbox)
        chest_group.layout().addLayout(label_and_widget("Item in Chest: ", self.chest_item_dropdown))

        self.layout().addWidget(chest_group)

    @property
    def level(self):
        return self.level_ref.level

    def closeEvent(self, event: QMouseEvent):
        item_index = self.chest_item_dropdown.currentIndex()
        chest_item_name = MAPITEM_NAMES[item_index]

        # was enabled
        if self.chest_end_checkbox.isChecked() and self.before.chest_exit is None:
            self.undo_stack.beginMacro(f"Enable Chest Exit with '{chest_item_name}'")

            chest_exit_item = self.level.enemy_item_factory.from_properties(OBJ_CHEST_EXIT, 0, 0)
            self.undo_stack.push(AddObject(self.level, chest_exit_item))
            self.undo_stack.endMacro()

        # was disabled
        elif self.before.chest_exit is not None and not self.chest_end_checkbox.isChecked():
            assert self.before.chest_exit is not None

            self.undo_stack.beginMacro("Disabling Chest Exit")
            self.undo_stack.push(RemoveObject(self.level, self.before.chest_exit))

            self.undo_stack.endMacro()

        # not item set
        elif item_index == 0:
            if self.before.chest_item is not None:
                self.undo_stack.push(RemoveObject(self.level, self.before.chest_item))

        # item was changed/set
        elif self.before.item_index != item_index:
            self.undo_stack.beginMacro(f"Set Chest Item to '{chest_item_name}'")

            if self.before.chest_item is not None:
                before_move = self.before.chest_item.copy()
                self.before.chest_item.y_position = item_index

                self.undo_stack.push(MoveObject(self.level, before_move, self.before.chest_item))

            else:
                item_set_obj = self.level.enemy_item_factory.from_properties(OBJ_CHEST_ITEM_SETTER, 0, item_index)

                self.undo_stack.push(AddObject(self.level, item_set_obj))

            self.undo_stack.endMacro()

        self.level.data_changed.emit()

        super(ChestExitMixin, self).closeEvent(event)
