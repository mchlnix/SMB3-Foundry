from PySide6.QtCore import Signal, SignalInstance
from PySide6.QtWidgets import QHeaderView, QSizePolicy, QTableWidget


class TableWidget(QTableWidget):
    selection_changed: SignalInstance = Signal(int)

    def __init__(self, parent):
        super(TableWidget, self).__init__(parent)

        self.setAlternatingRowColors(True)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.setSelectionBehavior(self.SelectionBehavior.SelectRows)
        self.setSelectionMode(self.SelectionMode.SingleSelection)

        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setStretchLastSection(True)

        self.itemSelectionChanged.connect(lambda: self.selection_changed.emit(self.selected_row))

    def set_headers(self, headers: list[str]):
        self.setColumnCount(len(headers))

        # TODO doesn't do anything?
        self.setHorizontalHeaderLabels(headers)
        self.resizeColumnsToContents()

    @property
    def selected_row(self):
        if self.selectedIndexes():
            return self.selectedIndexes()[0].row()
        else:
            return -1
