from PySide6.QtCore import QAbstractItemModel, QModelIndex
from PySide6.QtWidgets import (
    QComboBox,
    QHeaderView,
    QMessageBox,
    QSizePolicy,
    QStyledItemDelegate,
    QTableWidget,
    QWidget,
)

from foundry.game.level.LevelRef import LevelRef
from foundry.game.level.WorldMap import WorldMap
from foundry.gui.Spinner import Spinner


class TableWidget(QTableWidget):
    def __init__(self, level_ref: LevelRef):
        super(TableWidget, self).__init__()

        self.level_ref = level_ref

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.setSelectionBehavior(self.SelectRows)
        self.setSelectionMode(self.SingleSelection)
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


class DropdownDelegate(QStyledItemDelegate):
    def __init__(self, parent, items: list[str]):
        super(DropdownDelegate, self).__init__(parent)

        self._items = items

    def createEditor(self, parent: QWidget, option, index: QModelIndex) -> QWidget:
        combobox = QComboBox(parent)
        combobox.currentTextChanged.connect(lambda _: combobox.clearFocus())

        for index, name in enumerate(self._items):
            combobox.addItem(name, index)

        return combobox

    def setEditorData(self, editor: QComboBox, index: QModelIndex):
        editor.setCurrentText(index.data())

        editor.showPopup()


class SpinBoxDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        super(SpinBoxDelegate, self).__init__(parent)

    def createEditor(self, parent: QWidget, option, index: QModelIndex) -> QWidget:
        return Spinner(parent)

    def setEditorData(self, editor: Spinner, index: QModelIndex):
        if isinstance(value := index.data(), str):
            value = int(value, 16)

        editor.setValue(value)

    def setModelData(self, editor: Spinner, model: QAbstractItemModel, index: QModelIndex) -> None:
        model.setData(index, hex(editor.value()))


class DialogDelegate(QStyledItemDelegate):
    def __init__(self, parent, title: str, text: str):
        super(DialogDelegate, self).__init__(parent)

        self.title = title
        self.text = text

    def createEditor(self, parent: QWidget, option, index: QModelIndex) -> QWidget:
        dialog = QMessageBox(
            QMessageBox.Information,
            self.title,
            self.text,
            parent=parent,
        )

        return dialog

    def setModelData(self, editor: QWidget, model, index: QModelIndex) -> None:
        return model.data(index)
