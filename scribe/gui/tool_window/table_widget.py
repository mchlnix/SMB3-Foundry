from typing import cast

from PySide6.QtCore import QAbstractItemModel, QSize, Signal, SignalInstance
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
from foundry.gui.widgets.Spinner import SPINNER_MAX_VALUE, Spinner


class TableWidget(QTableWidget):
    selection_changed: SignalInstance = Signal(int)

    def __init__(self, parent, level_ref: LevelRef):
        super(TableWidget, self).__init__(parent)

        self.setDragDropMode(self.DragDropMode.InternalMove)
        self.setIconSize(QSize(32, 32))
        self.setAlternatingRowColors(True)

        self.level_ref = level_ref

        self.level_ref.level_changed.connect(self.update_content)
        self.level_ref.palette_changed.connect(self.update_content)
        self.level_ref.data_changed.connect(self.update_content)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.setSelectionBehavior(self.SelectionBehavior.SelectRows)
        self.setSelectionMode(self.SelectionMode.SingleSelection)

        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setStretchLastSection(True)

        self.itemSelectionChanged.connect(lambda: self.selection_changed.emit(self.selected_row))

        self.undo_stack.indexChanged.connect(self.update_content)

    def set_headers(self, headers: list[str]):
        self.setColumnCount(len(headers))

        # TODO doesn't do anything?
        self.setHorizontalHeaderLabels(headers)

    @property
    def world(self) -> WorldMap:
        return self.level_ref.level

    @property
    def undo_stack(self) -> QUndoStack:
        return cast(QUndoStack, self.window().parent().findChild(QUndoStack, "undo_stack"))

    @property
    def selected_row(self):
        if self.selectedIndexes():
            return self.selectedIndexes()[0].row()
        else:
            return -1

    def update_content(self):
        pass

    def _set_map_tile_as_icon(self, item: QTableWidgetItem, pos: tuple[int, int]):
        if not self.world.point_in(*pos):
            return

        block_icon = QPixmap(self.iconSize())

        painter = QPainter(block_icon)
        get_worldmap_tile(self.world.tile_at(*pos), self.world.data.palette_index).draw(
            painter, 0, 0, self.iconSize().width()
        )
        painter.end()

        item.setIcon(block_icon)


class DropdownDelegate(QStyledItemDelegate):
    def __init__(self, parent, items: list[str], icons: list[QImage] | None = None):
        super(DropdownDelegate, self).__init__(parent)

        self._items = items

        if icons is None:
            self._icons = []
        else:
            self._icons = icons

    def createEditor(self, parent: QWidget, option, index) -> QWidget:
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

    def setEditorData(self, editor, index):
        assert isinstance(editor, QComboBox)

        editor.setCurrentText(index.data())

        editor.showPopup()


class SpinBoxDelegate(QStyledItemDelegate):
    def __init__(self, parent, minimum=0, maximum=SPINNER_MAX_VALUE, base=16):
        super(SpinBoxDelegate, self).__init__(parent)

        self.minimum = minimum
        self.maximum = maximum
        self.base = base

    def createEditor(self, parent: QWidget, option, index) -> QWidget:
        return Spinner(parent, self.maximum, self.base)

    def setEditorData(self, editor: QWidget, index):
        if isinstance(value := index.data(), str):
            value = int(value, self.base)

        assert isinstance(editor, Spinner)
        editor.setValue(value)

    def setModelData(self, editor: QWidget, model: QAbstractItemModel, index) -> None:
        assert isinstance(editor, Spinner)

        if self.base == 16:
            model.setData(index, hex(editor.value()))
        else:
            model.setData(index, editor.value())


class DialogDelegate(QStyledItemDelegate):
    def __init__(self, parent, title: str, text: str):
        super(DialogDelegate, self).__init__(parent)

        self.title = title
        self.text = text

    def createEditor(self, parent: QWidget, option, index) -> QWidget:
        dialog = QMessageBox(
            QMessageBox.Information,
            self.title,
            self.text,
            parent=parent,
        )

        return dialog

    def setModelData(self, editor: QWidget, model, index) -> None:
        return model.data(index)
