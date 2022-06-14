from PySide6.QtWidgets import QHeaderView, QSizePolicy, QTableWidget, QTableWidgetItem

from foundry.game.level.LevelRef import LevelRef
from foundry.game.level.WorldMap import WorldMap
from smb3parse.constants import MAPITEM_NAMES, MAPOBJ_NAMES


class SpriteList(QTableWidget):
    def __init__(self, level_ref: LevelRef):
        super(SpriteList, self).__init__()

        self.level_ref = level_ref
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.setColumnCount(3)
        self.setRowCount(len(list(self.world._internal_world_map.gen_sprites())))

        self.setHorizontalHeaderLabels(["Sprite Type", "Item Type", "Map Position"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        last_item_row = 0

        for position in self.world._internal_world_map.gen_sprites():
            sprite_type = QTableWidgetItem(MAPOBJ_NAMES[position.sprite()])
            item_type = QTableWidgetItem(MAPITEM_NAMES[position.item()])
            pos = QTableWidgetItem(f"Screen {position.screen}: x={position.column}, y={position.row}")

            self.setItem(last_item_row, 0, sprite_type)
            self.setItem(last_item_row, 1, item_type)
            self.setItem(last_item_row, 2, pos)

            last_item_row += 1

    @property
    def world(self) -> WorldMap:
        return self.level_ref.level
