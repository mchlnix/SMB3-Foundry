from PySide6.QtCore import QPoint
from PySide6.QtGui import QMouseEvent, Qt
from PySide6.QtWidgets import QLabel, QTableWidgetItem, QVBoxLayout, QWidget

from foundry import get_level_thumbnail, pixmap_to_base64
from foundry.game.File import ROM
from foundry.gui.widgets.table_widget import TableWidget
from smb3parse.objects.object_set import OBJECT_SET_NAMES
from smb3parse.util.parser import FoundLevel

LOST_LEVELS_INDEX = 8
OVERWORLD_MAPS_INDEX = 9


class FoundLevelWidget(QWidget):
    def __init__(self):
        super().__init__()

        # List of found levels
        self._found_levels = ROM.additional_data.found_levels.copy()
        self._found_levels.sort(key=lambda x: (x.world_number, x.level_offset))

        found_label = QLabel("Found Levels")
        self.level_table = _FoundLevelTable(self, self._found_levels)

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
        found_level_layout.addWidget(self.level_table, 1)
        found_level_layout.addWidget(description_label, 0)

    @property
    def level_address(self):
        return self._found_levels[self.level_table.level_index].level_offset

    @property
    def enemy_address(self):
        return self._found_levels[self.level_table.level_index].enemy_offset

    @property
    def object_set_number(self):
        return self._found_levels[self.level_table.level_index].object_set_number


class _FoundLevelTable(TableWidget):
    def __init__(self, parent, levels: list[FoundLevel]):
        super().__init__(parent)

        self.setSortingEnabled(True)
        self.setMouseTracking(True)

        self.setEditTriggers(self.EditTrigger.NoEditTriggers)

        self._levels = levels
        self._last_checked_level_index = -1
        """The index of the last level we generated a thumbnail for."""

        self.set_headers(["World", "Object Set", "Level Addr.", "Enemy Addr.", "Jump Dest.", "World Specific"])

        self._update_content()

    def _level_index_for_row(self, row):
        return self.item(row, 0).data(Qt.ItemDataRole.UserRole)

    @property
    def level_index(self):
        return self._level_index_for_row(self.currentRow())

    def mouseMoveEvent(self, event: QMouseEvent):
        return self._set_thumbnail(event)

    def _set_thumbnail(self, event: QMouseEvent):
        if not self.isVisible():
            # for some reason, even after the level selector is closed, the thumbnails still appear, but now in the
            # level view. no idea why.
            self.setToolTip("")
            return

        pos_plus_header = event.globalPosition() - QPoint(0, self.horizontalHeader().height() + 1)

        pos = self.mapFromGlobal(pos_plus_header.toPoint())

        # when double-clicking to select a level, this happened, killed the call and somehow made tooltips appear in the
        # level view, even after the level selector was cleaned up, so explicitly check that we still have an item
        if (item := self.itemAt(pos)) is None:
            return

        level_index = self._level_index_for_row(self.row(item))

        if level_index == self._last_checked_level_index:
            return

        self._last_checked_level_index = level_index

        if level_index == -1:
            self.setToolTip(None)
            return

        level = self._levels[level_index]

        image_data = get_level_thumbnail(
            level.object_set_number,
            level.level_offset,
            level.enemy_offset,
        )

        self.setToolTip(f"<img src='data:image/png;base64,{pixmap_to_base64(image_data)}'>")

    def _update_content(self):
        self.setRowCount(len(self._levels))

        self.blockSignals(True)

        for index, found_level in enumerate(self._levels):
            # sorting messes up the indexes, so save the level_index in found level list in the table time for world no
            world_table_item = QTableWidgetItem(f"World {found_level.world_number}")
            world_table_item.setData(Qt.ItemDataRole.UserRole, index)

            self.setItem(index, 0, world_table_item)
            self.setItem(index, 1, QTableWidgetItem(OBJECT_SET_NAMES[found_level.object_set_number]))
            self.setItem(index, 2, QTableWidgetItem(f"0x{found_level.level_offset:x}"))
            self.setItem(index, 3, QTableWidgetItem(f"0x{found_level.enemy_offset:0>4x}"))

            if found_level.found_as_jump and not found_level.found_in_world:
                cross_item = QTableWidgetItem("X")
                cross_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.setItem(index, 4, cross_item)
            else:
                no_cross_item = QTableWidgetItem("")
                no_cross_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.setItem(index, 4, no_cross_item)

            if found_level.is_world_specific:
                cross_item = QTableWidgetItem("X")
                cross_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.setItem(index, 5, cross_item)
            else:
                no_cross_item = QTableWidgetItem("")
                no_cross_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.setItem(index, 5, no_cross_item)

        self.blockSignals(False)
