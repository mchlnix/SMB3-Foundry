from PySide6.QtWidgets import QTableWidgetItem

from foundry.game.ObjectSet import OBJECT_SET_NAMES
from foundry.game.level.LevelRef import LevelRef
from scribe.gui.tool_window.table_widget import TableWidget


class LevelPointerList(TableWidget):
    def __init__(self, level_ref: LevelRef):
        super(LevelPointerList, self).__init__(level_ref)

        self.level_ref.level_changed.connect(self.update_content)

        self.itemSelectionChanged.connect(lambda: self.level_ref.select_level_pointers(self.selected_rows))

        self.set_headers(["Object Set", "Level Offset", "Enemy/Item Offset", "Map Position"])

        self.update_content()

    def update_content(self):
        self.clear()

        self.setRowCount(len(list(self.world._internal_world_map.gen_levels())))

        last_item_row = 0

        for position in self.world._internal_world_map.gen_positions():
            if position.level_info is None:
                continue

            object_set_number, level_address, enemy_address = position.level_info

            object_set_name = QTableWidgetItem(OBJECT_SET_NAMES[object_set_number])
            hex_level_address = QTableWidgetItem(hex(level_address))
            hex_enemy_address = QTableWidgetItem(hex(enemy_address))
            pos = QTableWidgetItem(f"Screen {position.screen}: x={position.column}, y={position.row}")

            self.setItem(last_item_row, 0, object_set_name)
            self.setItem(last_item_row, 1, hex_level_address)
            self.setItem(last_item_row, 2, hex_enemy_address)
            self.setItem(last_item_row, 3, pos)

            last_item_row += 1
