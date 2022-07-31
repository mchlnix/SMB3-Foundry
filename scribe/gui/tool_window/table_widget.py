from typing import List, Tuple

from PySide6.QtCore import QAbstractItemModel, QModelIndex, QSize, Signal, SignalInstance
from PySide6.QtGui import QImage, QPainter, QPixmap, QUndoStack
from PySide6.QtWidgets import (
    QComboBox,
    QHeaderView,
    QMessageBox,
    QSizePolicy,
    QStyledItemDelegate,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

from foundry.game.gfx.drawable.Block import get_worldmap_tile
from foundry.game.level.LevelRef import LevelRef
from foundry.game.level.WorldMap import WorldMap
from foundry.gui.Spinner import Spinner


class TableWidget(QTableWidget):
    selection_changed: SignalInstance = Signal(int)

    def __init__(self, parent, level_ref: LevelRef):
        super(TableWidget, self).__init__(parent)

        self.setDragDropMode(self.InternalMove)
        self.setIconSize(QSize(32, 32))
        self.setAlternatingRowColors(True)

        self.level_ref = level_ref

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.setSelectionBehavior(self.SelectRows)
        self.setSelectionMode(self.SingleSelection)

        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setStretchLastSection(True)

        self.itemSelectionChanged.connect(lambda: self.selection_changed.emit(self.selected_row))

        self.undo_stack.indexChanged.connect(self.update_content)

    def set_headers(self, headers: List[str]):
        self.setColumnCount(len(headers))

        # TODO doesn't do anything?
        self.setHorizontalHeaderLabels(headers)

    @property
    def world(self) -> WorldMap:
        return self.level_ref.level

    @property
    def undo_stack(self) -> QUndoStack:
        return self.window().parent().findChild(QUndoStack, "undo_stack")

    @property
    def selected_row(self):
        if self.selectedIndexes():
            return self.selectedIndexes()[0].row()
        else:
            return -1

    def update_content(self):
        pass

    def _set_map_tile_as_icon(self, item: QTableWidgetItem, pos: Tuple[int, int]):
        if not self.world.point_in(*pos):
            return

        block_icon = QPixmap(self.iconSize())

        painter = QPainter(block_icon)
        get_worldmap_tile(self.world.tile_at(*pos)).draw(painter, 0, 0, self.iconSize().width())
        painter.end()

        item.setIcon(block_icon)


class DropdownDelegate(QStyledItemDelegate):
    def __init__(self, parent, items: List[str], icons: List[QImage] = None):
        super(DropdownDelegate, self).__init__(parent)

        self._items = items

        if icons is None:
            self._icons = []
        else:
            self._icons = icons

    def createEditor(self, parent: QWidget, option, index: QModelIndex) -> QWidget:
        combobox = QComboBox(parent)
        combobox.currentTextChanged.connect(lambda _: combobox.clearFocus())

        if not self._icons:
            for name in self._items:
                combobox.addItem(name)
        else:
            for icon, name in zip(self._icons, self._items):
                combobox.addItem(QPixmap(icon.scaled(32, 32)), name)

        combobox.setIconSize(QSize(32, 32))

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
