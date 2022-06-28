from PySide6.QtWidgets import QTableWidgetItem

from foundry.game.level.LevelRef import LevelRef
from scribe.gui.tool_window.table_widget import TableWidget
from smb3parse.constants import MAPITEM_NAMES, MAPOBJ_NAMES


class SpriteList(TableWidget):
    def __init__(self, level_ref: LevelRef):
        super(SpriteList, self).__init__(level_ref)

        self.level_ref.level_changed.connect(self.update_content)

        self.itemSelectionChanged.connect(lambda: self.level_ref.select_sprites(self.selected_rows))

        self.set_headers(["Sprite Type", "Item Type", "Map Position"])

        self.update_content()

    def update_content(self):
        self.clear()

        self.setRowCount(len(list(self.world._internal_world_map.gen_sprites())))

        last_item_row = 0

        for position in self.world._internal_world_map.gen_sprites():
            sprite_type = QTableWidgetItem(MAPOBJ_NAMES[position.type])
            item_type = QTableWidgetItem(MAPITEM_NAMES[position.item])
            pos = QTableWidgetItem(f"Screen {position.screen}: x={position.x}, y={position.y}")

            self.setItem(last_item_row, 0, sprite_type)
            self.setItem(last_item_row, 1, item_type)
            self.setItem(last_item_row, 2, pos)

            last_item_row += 1
