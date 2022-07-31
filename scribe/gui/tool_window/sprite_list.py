import typing

from PySide6.QtGui import QDropEvent, QPixmap
from PySide6.QtWidgets import QComboBox, QTableWidgetItem

from foundry.game.level.LevelRef import LevelRef
from scribe.gui.commands import ChangeSpriteIndex, SetSpriteItem, SetSpriteType
from scribe.gui.tool_window.table_widget import DialogDelegate, DropdownDelegate, TableWidget
from smb3parse.constants import MAPITEM_NAMES, MAPOBJ_NAMES, MAP_ITEM_SPRITES, MAP_OBJ_SPRITES
from smb3parse.levels import FIRST_VALID_ROW


class SpriteList(TableWidget):
    def __init__(self, parent, level_ref: LevelRef):
        super(SpriteList, self).__init__(parent, level_ref)

        self.level_ref.level_changed.connect(self.update_content)
        self.level_ref.data_changed.connect(self.update_content)

        self.cellChanged.connect(self._save_sprite)

        self.set_headers(["Sprite Type", "Item Type", "Map Position"])

        self.setItemDelegateForColumn(
            0, DropdownDelegate(self, list(MAPOBJ_NAMES.values()), list(MAP_OBJ_SPRITES.values()))
        )
        self.setItemDelegateForColumn(
            1, DropdownDelegate(self, list(MAPITEM_NAMES.values()), list(MAP_ITEM_SPRITES.values()))
        )
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

    def dropEvent(self, event: QDropEvent) -> None:
        source_index = self.selectedIndexes()[0].row()
        target_index = self.indexAt(event.pos()).row()

        self.undo_stack.push(ChangeSpriteIndex(self.world, source_index, target_index))

        self.update_content()

    def _save_sprite(self, row: int, column: int):
        if column == 2:
            return

        sprite = self.world.sprites[row]

        widget = typing.cast(QComboBox, self.cellWidget(row, column))
        data = widget.currentText()

        if sprite.data.y < FIRST_VALID_ROW:
            sprite.data.y = FIRST_VALID_ROW

        if column == 0:
            self.undo_stack.push(SetSpriteType(sprite.data, list(MAPOBJ_NAMES.values()).index(data)))
        elif column == 1:
            self.undo_stack.push(SetSpriteItem(sprite.data, list(MAPITEM_NAMES.values()).index(data)))
        else:
            return

        self.world.data_changed.emit()

    def update_content(self):
        self.setRowCount(len(self.world.sprites))

        self.blockSignals(True)

        for index, sprite in enumerate(self.world.sprites):
            sprite_type = QTableWidgetItem(MAPOBJ_NAMES[sprite.data.type])
            sprite_type.setIcon(QPixmap(MAP_OBJ_SPRITES[sprite.data.type].scaled(self.iconSize())))

            item_type = QTableWidgetItem(MAPITEM_NAMES[sprite.data.item])
            item_type.setIcon(QPixmap(MAP_ITEM_SPRITES[sprite.data.item].scaled(self.iconSize())))
            pos = QTableWidgetItem(f"Screen {sprite.data.screen}: x={sprite.data.x}, y={sprite.data.y}")

            self._set_map_tile_as_icon(pos, sprite.get_position())

            self.setItem(index, 0, sprite_type)
            self.setItem(index, 1, item_type)
            self.setItem(index, 2, pos)

        self.blockSignals(False)
