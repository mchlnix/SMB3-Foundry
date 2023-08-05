from PySide6.QtWidgets import QGridLayout, QLabel, QListWidget, QWidget

from foundry.game.File import ROM
from foundry.game.level.Level import Level
from foundry.gui import WORLD_ITEMS
from smb3parse.levels import HEADER_LENGTH

LOST_LEVELS_INDEX = 8
OVERWORLD_MAPS_INDEX = 9


class StockLevelWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.world_list = QListWidget(parent=self)
        self.world_list.addItems(WORLD_ITEMS)
        self.world_list.itemClicked.connect(self._on_world_click)

        self.level_list = QListWidget(parent=self)

        stock_level_layout = QGridLayout(self)

        world_label = QLabel("World")
        level_label = QLabel("Level")

        description_label = QLabel()
        description_label.setWordWrap(True)
        description_label.setText(
            "These are the Level and Enemy addresses of the US version of SMB3. If Levels are moved (e.g. by the "
            "automatic Level management) or overwritten by other Levels, then loading these might result in an error "
            "or broken Level."
        )

        if ROM.additional_data.found_levels:
            description_label.setStyleSheet("QLabel { color : red; }")

        stock_level_layout.addWidget(world_label, 0, 0)
        stock_level_layout.addWidget(level_label, 0, 1)

        stock_level_layout.addWidget(self.world_list, 1, 0)
        stock_level_layout.addWidget(self.level_list, 1, 1)

        stock_level_layout.addWidget(description_label, 2, 0, 1, 2)

    def _on_world_click(self):
        index = self.world_list.currentRow()

        assert index >= 0

        if index == OVERWORLD_MAPS_INDEX:
            world_number = 0  # world maps
        else:
            world_number = index + 1

        self.level_list.clear()

        # skip first meaningless item
        for level in Level.offsets[1:]:
            if level.game_world == world_number and level.name:
                self.level_list.addItem(level.name)

        if self.level_list.count():
            self.level_list.setCurrentRow(0)
            self.level_list.itemClicked.emit(self.level_list.currentItem())

    @property
    def _level_index(self):
        level_array_offset = self.level_list.currentRow() + 1

        if not self.level_is_overworld:
            level_array_offset += Level.world_indexes[self.world_number]

        return level_array_offset

    @property
    def _level_def(self):
        return Level.offsets[self._level_index]

    @property
    def level_address(self):
        level_address = self._level_def.rom_level_offset

        if not self.level_is_overworld:
            level_address -= HEADER_LENGTH

        return level_address

    @property
    def enemy_address(self):
        if not self.level_is_overworld:
            enemy_address = self._level_def.enemy_offset
        else:
            enemy_address = 0

        if enemy_address:
            # data in look up table is off by one, since workshop ignores the first byte
            enemy_address -= 1

        return enemy_address

    @property
    def object_set_number(self):
        return self._level_def.real_obj_set

    @property
    def world_number(self):
        if self.level_is_lost:
            world_number = 1
        else:
            world_number = self.world_list.currentRow() + 1

        return world_number

    @property
    def level_name(self):
        if self.level_is_overworld:
            level_name = ""
        elif self.level_is_lost:
            level_name = "Lost World, "
        else:
            level_name = f"World {self.world_number}, "

        level_name += f"{self._level_def.name}"

        return level_name

    @property
    def level_is_overworld(self):
        return self.world_list.currentRow() == OVERWORLD_MAPS_INDEX

    @property
    def level_is_lost(self):
        return self.world_list.currentRow() == LOST_LEVELS_INDEX
