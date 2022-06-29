from PySide6.QtCore import QModelIndex
from PySide6.QtWidgets import QComboBox, QMessageBox, QStyledItemDelegate, QTableWidgetItem, QWidget

from foundry.game.level.LevelRef import LevelRef
from scribe.gui.tool_window.table_widget import TableWidget
from smb3parse.constants import MAPITEM_NAMES, MAPOBJ_NAMES
from smb3parse.levels import FIRST_VALID_ROW


class SpriteList(TableWidget):
    def __init__(self, level_ref: LevelRef):
        super(SpriteList, self).__init__(level_ref)

        self.level_ref.level_changed.connect(self.update_content)
        self.level_ref.data_changed.connect(self.update_content)

        self.itemSelectionChanged.connect(lambda: self.level_ref.select_sprites(self.selected_rows))
        self.cellChanged.connect(self._save_sprite)

        self.set_headers(["Sprite Type", "Item Type", "Map Position"])

        self.setItemDelegateForColumn(0, DropdownDelegate(self, MAPOBJ_NAMES.values()))
        self.setItemDelegateForColumn(1, DropdownDelegate(self, MAPITEM_NAMES.values()))
        self.setItemDelegateForColumn(2, DialogDelegate(self))

        self.update_content()

    def _save_sprite(self, row: int, column: int):
        if column == 2:
            return

        sprite = list(self.world.internal_world_map.gen_sprites())[row]

        widget: QComboBox = self.cellWidget(row, column)
        data = widget.currentText()

        if sprite.y < FIRST_VALID_ROW:
            sprite.y = FIRST_VALID_ROW

        if column == 0:
            sprite.type = list(MAPOBJ_NAMES.values()).index(data)
        elif column == 1:
            sprite.item = list(MAPITEM_NAMES.values()).index(data)
        else:
            return

        sprite.write_back()

        self.world.data_changed.emit()

    def update_content(self):
        self.clear()

        self.setRowCount(len(list(self.world.internal_world_map.gen_sprites())))

        self.blockSignals(True)

        for index, position in enumerate(self.world.internal_world_map.gen_sprites()):
            sprite_type = QTableWidgetItem(MAPOBJ_NAMES[position.type])
            item_type = QTableWidgetItem(MAPITEM_NAMES[position.item])
            pos = QTableWidgetItem(f"Screen {position.screen}: x={position.x}, y={position.y}")

            self.setItem(index, 0, sprite_type)
            self.setItem(index, 1, item_type)
            self.setItem(index, 2, pos)

        self.blockSignals(False)


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


class DialogDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        super(DialogDelegate, self).__init__(parent)

    def createEditor(self, parent: QWidget, option, index: QModelIndex) -> QWidget:
        dialog = QMessageBox(
            QMessageBox.Information,
            "No can do",
            "You can move sprites by dragging them around in the WorldView. Make sure they are shown in the View Menu.",
            parent=parent,
        )

        return dialog

    def setModelData(self, editor: QWidget, model, index: QModelIndex) -> None:
        return model.data(index)
