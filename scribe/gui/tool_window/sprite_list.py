import typing

from PySide6.QtWidgets import QComboBox, QTableWidgetItem

from foundry.game.level.LevelRef import LevelRef
from scribe.gui.tool_window.table_widget import DialogDelegate, DropdownDelegate, TableWidget
from smb3parse.constants import MAPITEM_NAMES, MAPOBJ_NAMES
from smb3parse.levels import FIRST_VALID_ROW


class SpriteList(TableWidget):
    def __init__(self, level_ref: LevelRef):
        super(SpriteList, self).__init__(level_ref)

        self.level_ref.level_changed.connect(self.update_content)
        self.level_ref.data_changed.connect(self.update_content)

        self.itemSelectionChanged.connect(lambda: self.level_ref.select_sprites(self.selected_rows))
        self.cellChanged.connect(self._save_sprite)

        self.set_headers(["Sprite Type", "Item Type", "Map Position"])

        self.setItemDelegateForColumn(0, DropdownDelegate(self, MAPOBJ_NAMES.values()))
        self.setItemDelegateForColumn(1, DropdownDelegate(self, MAPITEM_NAMES.values()))
        self.setItemDelegateForColumn(
            2,
            DialogDelegate(
                self,
                "No can do",
                "You can move sprites by dragging them around in the WorldView. "
                "Make sure they are shown in the View Menu.",
            ),
        )

        self.update_content()

    def _save_sprite(self, row: int, column: int):
        if column == 2:
            return

        sprite = list(self.world.internal_world_map.gen_sprites())[row]

        widget = typing.cast(QComboBox, self.cellWidget(row, column))
        data = widget.currentText()

        if sprite.y < FIRST_VALID_ROW:
            sprite.y = FIRST_VALID_ROW

        if column == 0:
            sprite.type = list(MAPOBJ_NAMES.values()).index(data)
        elif column == 1:
            sprite.item = list(MAPITEM_NAMES.values()).index(data)
        else:
            return

        sprite.write_back()

        self.world.data_changed.emit()

    def update_content(self):
        self.clear()

        self.setRowCount(len(list(self.world.internal_world_map.gen_sprites())))

        self.blockSignals(True)

        for index, sprite in enumerate(self.world.internal_world_map.gen_sprites()):
            sprite_type = QTableWidgetItem(MAPOBJ_NAMES[sprite.type])
            item_type = QTableWidgetItem(MAPITEM_NAMES[sprite.item])
            pos = QTableWidgetItem(f"Screen {sprite.screen}: x={sprite.x}, y={sprite.y}")

            self.setItem(index, 0, sprite_type)
            self.setItem(index, 1, item_type)
            self.setItem(index, 2, pos)

        self.blockSignals(False)
