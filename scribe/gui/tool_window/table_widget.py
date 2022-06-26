from PySide6.QtWidgets import QHeaderView, QSizePolicy, QTableWidget

from foundry.game.level.LevelRef import LevelRef
from foundry.game.level.WorldMap import WorldMap


class TableWidget(QTableWidget):
    def __init__(self, level_ref: LevelRef):
        super(TableWidget, self).__init__()

        self.level_ref = level_ref

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.setSelectionBehavior(self.SelectRows)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def set_headers(self, headers: list[str]):
        self.setColumnCount(len(headers))

        self.setHorizontalHeaderLabels(headers)

    @property
    def world(self) -> WorldMap:
        return self.level_ref.level

    @property
    def selected_rows(self):
        return [index.row() for index in self.selectedIndexes()]
