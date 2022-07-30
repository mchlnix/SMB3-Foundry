import typing

from PySide6.QtCore import QModelIndex, QSize
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QStyledItemDelegate, QTableWidgetItem, QWidget

from foundry.game.gfx.drawable.Block import get_worldmap_tile
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.BlockViewer import BlockBank
from foundry.gui.Spinner import Spinner
from scribe.gui.commands import ChangeLockIndex, ChangeReplacementTile
from scribe.gui.tool_window.table_widget import DialogDelegate, SpinBoxDelegate, TableWidget


class LocksList(TableWidget):
    def __init__(self, parent, level_ref: LevelRef):
        super(LocksList, self).__init__(parent, level_ref)

        self.setDragDropMode(self.NoDragDrop)

        self.level_ref.level_changed.connect(self.update_content)
        self.level_ref.data_changed.connect(self.update_content)

        self.cellChanged.connect(self._save_fortress_fx)
        self.setIconSize(QSize(32, 32))

        self.set_headers(["Replacement Tile", "Linked Fortress", "Boom Boom Positions", "Map Position"])

        self.setItemDelegateForColumn(0, BlockBankDelegate(self))
        self.setItemDelegateForColumn(1, SpinBoxDelegate(self))
        self.setItemDelegateForColumn(2, NoneDelegate(self))
        self.setItemDelegateForColumn(
            3,
            DialogDelegate(
                self,
                "No can do",
                "You can move Fortress FX by dragging them around in the WorldView. "
                "Make sure they are shown in the View Menu.",
            ),
        )

        self.update_content()

    def _save_fortress_fx(self, row: int, column: int):
        if column in [2, 3]:
            return

        lock = self.world.locks_and_bridges[row]

        if column == 0:
            widget = typing.cast(BlockBank, self.cellWidget(row, column))
            data = widget.last_clicked_index

            self.undo_stack.push(ChangeReplacementTile(self.world, lock.data.index, data))

        elif column == 1:
            widget = typing.cast(Spinner, self.cellWidget(row, column))
            data = widget.value()

            self.undo_stack.push(ChangeLockIndex(self.world, lock, data))

        else:
            return

        self.world.data_changed.emit()

    def update_content(self):
        self.setRowCount(len(self.world.locks_and_bridges))

        self.blockSignals(True)

        for index, fortress_fx in enumerate(self.world.locks_and_bridges):
            replacement_tile = QTableWidgetItem(hex(fortress_fx.data.replacement_tile_index))

            block_icon = QPixmap(self.iconSize())
            painter = QPainter(block_icon)
            get_worldmap_tile(fortress_fx.data.replacement_tile_index).draw(painter, 0, 0, self.iconSize().width())
            painter.end()

            replacement_tile.setIcon(block_icon)

            fortress_index = QTableWidgetItem(hex(fortress_fx.data.index))
            boomboom_pos = QTableWidgetItem(
                f"{hex(0x10 + 0x10 * fortress_fx.data.index)} - {hex(0x20 + 0x10 * fortress_fx.data.index - 1)}"
            )
            pos = QTableWidgetItem(f"Screen {fortress_fx.data.screen}: x={fortress_fx.data.x}, y={fortress_fx.data.y}")

            self.setItem(index, 0, replacement_tile)
            self.setItem(index, 1, fortress_index)
            self.setItem(index, 2, boomboom_pos)
            self.setItem(index, 3, pos)

        self.blockSignals(False)


class BlockBankDelegate(QStyledItemDelegate):
    def createEditor(self, parent: QWidget, option, index: QModelIndex) -> QWidget:
        block_bank = BlockBank(parent)
        block_bank.clicked.connect(block_bank.hide)

        return block_bank

    def setEditorData(self, editor: BlockBank, index: QModelIndex):
        editor.show()


class NoneDelegate(QStyledItemDelegate):
    def createEditor(self, parent: QWidget, option, index: QModelIndex) -> QWidget:
        return None

    def setEditorData(self, editor, index: QModelIndex):
        pass
