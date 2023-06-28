import typing

from PySide6.QtGui import QDropEvent
from PySide6.QtWidgets import QComboBox, QTableWidgetItem

from foundry.game.level.LevelRef import LevelRef
from foundry.gui.Spinner import Spinner
from scribe.gui.commands import (
    ChangeLevelPointerIndex,
    SetEnemyAddress,
    SetLevelAddress,
    SetObjectSet,
)
from scribe.gui.tool_window.table_widget import (
    DialogDelegate,
    DropdownDelegate,
    SpinBoxDelegate,
    TableWidget,
)
from smb3parse.levels import FIRST_VALID_ROW
from smb3parse.objects.object_set import OBJECT_SET_NAMES


class LevelPointerList(TableWidget):
    def __init__(self, parent, level_ref: LevelRef):
        super(LevelPointerList, self).__init__(parent, level_ref)

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
        target_index = self.indexAt(event.position().toPoint()).row()

        self.undo_stack.push(ChangeLevelPointerIndex(self.world, source_index, target_index))

        self.update_content()

    def _save_level_pointer(self, row: int, column: int):
        if column == 3 or self.cellWidget(row, column) is None:
            return

        str_data = ""
        int_data = 0

        level_pointer = self.world.level_pointers[row]

        if column == 0:
            combo_box = typing.cast(QComboBox, self.cellWidget(row, column))
            str_data = combo_box.currentText()
        elif column in [1, 2]:
            spinner = typing.cast(Spinner, self.cellWidget(row, column))
            int_data = spinner.value()
        else:
            return

        if level_pointer.data.y < FIRST_VALID_ROW:
            level_pointer.data.y = FIRST_VALID_ROW

        if column == 0:
            self.undo_stack.push(SetObjectSet(level_pointer.data, OBJECT_SET_NAMES.index(str_data)))
        elif column == 1:
            self.undo_stack.push(SetLevelAddress(level_pointer.data, int_data))
        elif column == 2:
            self.undo_stack.push(SetEnemyAddress(level_pointer.data, int_data))
        else:
            return

        self.world.data_changed.emit()

    def update_content(self):
        self.setRowCount(self.world.internal_world_map.level_count)

        self.blockSignals(True)

        for row, lp in enumerate(self.world.level_pointers):
            object_set_name = QTableWidgetItem(OBJECT_SET_NAMES[lp.data.object_set])

            hex_level_address = QTableWidgetItem(hex(lp.data.level_address))
            hex_enemy_address = QTableWidgetItem(hex(lp.data.enemy_address))
            pos = QTableWidgetItem(f"Screen {lp.data.screen}: x={lp.data.x}, y={lp.data.y}")

            self._set_map_tile_as_icon(pos, lp.get_position())

            self.setItem(row, 0, object_set_name)
            self.setItem(row, 1, hex_level_address)
            self.setItem(row, 2, hex_enemy_address)
            self.setItem(row, 3, pos)

        self.blockSignals(False)
