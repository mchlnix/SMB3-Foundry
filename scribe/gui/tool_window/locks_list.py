import typing

from PySide6.QtCore import QSize
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QComboBox, QTableWidgetItem

from foundry.game.gfx.drawable.Block import get_worldmap_tile
from foundry.game.level.LevelRef import LevelRef
from scribe.gui.commands import SetSpriteItem, SetSpriteType
from scribe.gui.tool_window.table_widget import DialogDelegate, DropdownDelegate, TableWidget
from smb3parse.constants import MAPITEM_NAMES, MAPOBJ_NAMES
from smb3parse.levels import FIRST_VALID_ROW


class LocksList(TableWidget):
    def __init__(self, parent, level_ref: LevelRef):
        super(LocksList, self).__init__(parent, level_ref)

        self.setDragDropMode(self.NoDragDrop)

        self.level_ref.level_changed.connect(self.update_content)
        self.level_ref.data_changed.connect(self.update_content)

        self.cellChanged.connect(self._save_fortress_fx)
        self.setIconSize(QSize(32, 32))

        self.set_headers(["Replacement Tile", "Linked Fortress", "Map Position", "Boom Boom Positions"])

        self.setItemDelegateForColumn(0, DropdownDelegate(self, list(MAPOBJ_NAMES.values())))
        self.setItemDelegateForColumn(1, DropdownDelegate(self, list(MAPITEM_NAMES.values())))
        self.setItemDelegateForColumn(
            2,
            DialogDelegate(
                self,
                "No can do",
                "You can move Fortress FX by dragging them around in the WorldView. "
                "Make sure they are shown in the View Menu.",
            ),
        )

        self.update_content()

    def _save_fortress_fx(self, row: int, column: int):
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
        self.clear()

        self.setRowCount(len(self.world.locks_and_bridges))

        self.blockSignals(True)

        for index, fortress_fx in enumerate(self.world.locks_and_bridges):
            replacement_tile = QTableWidgetItem(hex(fortress_fx.data.replacement_tile_index))

            block_icon = QPixmap(self.iconSize())
            painter = QPainter(block_icon)
            get_worldmap_tile(fortress_fx.data.replacement_tile_index).draw(painter, 0, 0, self.iconSize().width())
            painter.end()

            replacement_tile.setIcon(block_icon)

            fortress_index = QTableWidgetItem(hex(fortress_fx.data.index))
            boomboom_pos = QTableWidgetItem(f"{hex(0x10 + 0x10 * index)} - {hex(0x20 + 0x10 * index - 1)}")
            pos = QTableWidgetItem(f"Screen {fortress_fx.data.screen}: x={fortress_fx.data.x}, y={fortress_fx.data.y}")

            self.setItem(index, 0, replacement_tile)
            self.setItem(index, 1, fortress_index)
            self.setItem(index, 2, boomboom_pos)
            self.setItem(index, 3, pos)

        self.blockSignals(False)
