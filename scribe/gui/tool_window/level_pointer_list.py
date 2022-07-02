import typing

from PySide6.QtWidgets import QComboBox, QTableWidgetItem

from foundry.game.ObjectSet import OBJECT_SET_NAMES
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.Spinner import Spinner
from scribe.gui.tool_window.table_widget import DialogDelegate, DropdownDelegate, SpinBoxDelegate, TableWidget
from smb3parse.levels import FIRST_VALID_ROW


class LevelPointerList(TableWidget):
    def __init__(self, level_ref: LevelRef):
        super(LevelPointerList, self).__init__(level_ref)

        self.level_ref.level_changed.connect(self.update_content)
        self.level_ref.data_changed.connect(self.update_content)

        self.itemSelectionChanged.connect(lambda: self.level_ref.select_level_pointers(self.selected_rows))
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

    def _save_level_pointer(self, row: int, column: int):
        if column == 3 or self.cellWidget(row, column) is None:
            return

        level_pointer = list(self.world.internal_world_map.gen_level_pointers())[row]

        if column == 0:
            widget = typing.cast(QComboBox, self.cellWidget(row, column))
            data = widget.currentText()
        elif column in [1, 2]:
            widget = typing.cast(Spinner, self.cellWidget(row, column))
            data = widget.value()
        else:
            return

        if level_pointer.y < FIRST_VALID_ROW:
            level_pointer.y = FIRST_VALID_ROW

        if column == 0:
            level_pointer.object_set = OBJECT_SET_NAMES.index(data)
        elif column == 1:
            level_pointer.level_address = data
        elif column == 2:
            level_pointer.enemy_address = data
        else:
            return

        level_pointer.write_back()

        self.world.data_changed.emit()

    def update_content(self):
        self.clear()

        self.setRowCount(self.world.internal_world_map.level_count)

        last_item_row = 0

        for level_pointer in self.world.internal_world_map.gen_level_pointers():
            object_set_name = QTableWidgetItem(OBJECT_SET_NAMES[level_pointer.object_set])
            hex_level_address = QTableWidgetItem(hex(level_pointer.level_address))
            hex_enemy_address = QTableWidgetItem(hex(level_pointer.enemy_address))
            pos = QTableWidgetItem(f"Screen {level_pointer.screen}: x={level_pointer.x}, y={level_pointer.y}")

            self.setItem(last_item_row, 0, object_set_name)
            self.setItem(last_item_row, 1, hex_level_address)
            self.setItem(last_item_row, 2, hex_enemy_address)
            self.setItem(last_item_row, 3, pos)

            last_item_row += 1
