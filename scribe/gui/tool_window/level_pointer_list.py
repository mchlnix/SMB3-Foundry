import typing

from PySide6.QtGui import QDropEvent, QPainter, QPixmap
from PySide6.QtWidgets import QComboBox, QTableWidgetItem

from foundry.game.ObjectSet import OBJECT_SET_NAMES
from foundry.game.gfx.drawable.Block import get_worldmap_tile
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.Spinner import Spinner
from scribe.gui.commands import ChangeLevelPointerIndex, SetEnemyAddress, SetLevelAddress, SetObjectSet
from scribe.gui.tool_window.table_widget import DialogDelegate, DropdownDelegate, SpinBoxDelegate, TableWidget
from smb3parse.levels import FIRST_VALID_ROW


class LevelPointerList(TableWidget):
    def __init__(self, parent, level_ref: LevelRef):
        super(LevelPointerList, self).__init__(parent, level_ref)

        self.level_ref.level_changed.connect(self.update_content)
        self.level_ref.data_changed.connect(self.update_content)

        self.cellChanged.connect(self._save_level_pointer)

        self.set_headers(["Object Set", "Level Offset", "Enemy/Item Offset", "Map Position"])

        self.setItemDelegateForColumn(0, DropdownDelegate(self, OBJECT_SET_NAMES))
        self.setItemDelegateForColumn(1, SpinBoxDelegate(self))
        self.setItemDelegateForColumn(2, SpinBoxDelegate(self))
        self.setItemDelegateForColumn(
            3,
            DialogDelegate(
                self,
                "No can do",
                "You can move level pointers by dragging them around in the WorldView. "
                "Make sure they are shown in the View Menu.",
            ),
        )

        self.update_content()

    def dropEvent(self, event: QDropEvent) -> None:
        source_index = self.selectedIndexes()[0].row()
        target_index = self.indexAt(event.pos()).row()

        self.undo_stack.push(ChangeLevelPointerIndex(self.world, source_index, target_index))

        self.update_content()

    def _save_level_pointer(self, row: int, column: int):
        if column == 3 or self.cellWidget(row, column) is None:
            return

        level_pointer = self.world.level_pointers[row]

        if column == 0:
            widget = typing.cast(QComboBox, self.cellWidget(row, column))
            data = widget.currentText()
        elif column in [1, 2]:
            widget = typing.cast(Spinner, self.cellWidget(row, column))
            data = widget.value()
        else:
            return

        if level_pointer.data.y < FIRST_VALID_ROW:
            level_pointer.data.y = FIRST_VALID_ROW

        if column == 0:
            self.undo_stack.push(SetObjectSet(level_pointer.data, OBJECT_SET_NAMES.index(data)))
        elif column == 1:
            self.undo_stack.push(SetLevelAddress(level_pointer.data, data))
        elif column == 2:
            self.undo_stack.push(SetEnemyAddress(level_pointer.data, data))
        else:
            return

        self.world.data_changed.emit()

    def update_content(self):
        self.setRowCount(self.world.internal_world_map.level_count)

        self.blockSignals(True)

        for row, lp in enumerate(self.world.level_pointers):
            object_set_name = QTableWidgetItem(OBJECT_SET_NAMES[lp.data.object_set])

            block_icon = QPixmap(self.iconSize())
            painter = QPainter(block_icon)
            get_worldmap_tile(self.world.tile_at(*lp.get_position())).draw(painter, 0, 0, self.iconSize().width())
            painter.end()

            object_set_name.setIcon(block_icon)

            hex_level_address = QTableWidgetItem(hex(lp.data.level_address))
            hex_enemy_address = QTableWidgetItem(hex(lp.data.enemy_address))
            pos = QTableWidgetItem(f"Screen {lp.data.screen}: x={lp.data.x}, y={lp.data.y}")
            # TODO Maybe set the tile of the pointer as an icon next to the pos?

            self.setItem(row, 0, object_set_name)
            self.setItem(row, 1, hex_level_address)
            self.setItem(row, 2, hex_enemy_address)
            self.setItem(row, 3, pos)

        self.blockSignals(False)
