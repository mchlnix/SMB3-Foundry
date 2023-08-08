from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QLabel, QListWidget, QVBoxLayout, QWidget

from foundry import get_level_thumbnail
from foundry.game.File import ROM
from smb3parse.objects.object_set import OBJECT_SET_NAMES

LOST_LEVELS_INDEX = 8
OVERWORLD_MAPS_INDEX = 9


class FoundLevelWidget(QWidget):
    def __init__(self):
        super().__init__()

        found_label = QLabel("Found Levels")
        self.level_list = QListWidget()
        self.level_list.setMouseTracking(True)

        description_label = QLabel()

        description_label.setWordWrap(True)
        description_label.setText(
            "If the automatic Level management is active, the ROM is searched for all accessible Levels. Be it through "
            "an overworld, jumped to by another Level, or generic Levels, defined for every World (e.g. Coin Ship "
            "Levels). Inaccessible 'Lost' Levels cannot be found this way and are not listed here/have probably been "
            "overwritten to make space for more Levels."
        )

        found_level_layout = QVBoxLayout(self)
        found_level_layout.addWidget(found_label, 0)
        found_level_layout.addWidget(self.level_list, 1)
        found_level_layout.addWidget(description_label, 0)

        # List of found levels
        self.found_levels = ROM.additional_data.found_levels.copy()
        self.found_levels.sort(key=lambda x: (x.world_number, x.level_offset))

        for found_level in self.found_levels:
            level_descr = f"World {found_level.world_number}\t"

            level_descr += f"Level: 0x{found_level.level_offset:x}\t"
            level_descr += f"Enemy: 0x{found_level.enemy_offset:0>4x}\t"

            level_descr += OBJECT_SET_NAMES[found_level.object_set_number]

            if found_level.found_as_jump and not found_level.found_in_world:
                level_descr += " (Jump Destination)"

            self.level_list.addItem(level_descr)

        self.level_list.mouseMoveEvent = self._set_thumbnail
        self._last_checked_row = -1

    def _set_thumbnail(self, event: QMouseEvent):
        pos = self.level_list.mapFromGlobal(event.globalPosition().toPoint())

        row = self.level_list.row(self.level_list.itemAt(pos))

        if row == self._last_checked_row:
            return

        self._last_checked_row = row

        if row == -1:
            self.level_list.setToolTip(None)
            return

        level = self.found_levels[row]

        image_data = get_level_thumbnail(
            level.object_set_number,
            level.level_offset,
            level.enemy_offset,
        )

        self.level_list.setToolTip(f"<img src='data:image/png;base64,{image_data}'>")

    @property
    def _level_index(self):
        return self.level_list.currentRow()

    @property
    def level_address(self):
        return self.found_levels[self._level_index].level_offset

    @property
    def enemy_address(self):
        return self.found_levels[self._level_index].enemy_offset

    @property
    def object_set_number(self):
        return self.found_levels[self._level_index].object_set_number
