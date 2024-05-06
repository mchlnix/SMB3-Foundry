from PySide6.QtCore import QModelIndex, Signal, SignalInstance
from PySide6.QtGui import QMouseEvent, Qt
from PySide6.QtWidgets import QListWidget, QSizePolicy, QWidget

from foundry.game.level.LevelRef import LevelRef
from foundry.gui.ContextMenu import LevelContextMenu


class ObjectList(QListWidget):
    selection_changed: SignalInstance = Signal(list)

    def __init__(self, parent: QWidget, level_ref: LevelRef, context_menu: LevelContextMenu):
        super(ObjectList, self).__init__(parent=parent)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.setSelectionMode(self.SelectionMode.ExtendedSelection)

        self.level_ref: LevelRef = level_ref
        self.level_ref.data_changed.connect(self.update_content)

        self.context_menu = context_menu

        self.itemSelectionChanged.connect(self.on_selection_changed)

        self.setWhatsThis(
            "<b>Object List</b><br/>"
            "This lists all the objects and enemies/items in the level. They appear in the order, "
            "that they are stored in the ROM as, which also decides which objects get drawn "
            "before/behind which.<br/>"
            "Enemies/items are always listed last, since they are also stored separately from the level "
            "objects.<br/><br/>"
            "Note: While Jumps are technically level objects, they are omitted here, since they are "
            "listed in a separate list below."
        )

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.RightButton:
            self.on_right_down(event)
        else:
            return super(ObjectList, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.RightButton:
            self.on_right_up(event)
        else:
            return super(ObjectList, self).mouseReleaseEvent(event)

    def on_right_down(self, event: QMouseEvent):
        item_under_mouse = self.itemAt(event.position().toPoint())

        if item_under_mouse is None:
            event.ignore()
            return

        if not item_under_mouse.isSelected():
            self.clearSelection()

            index = self.indexFromItem(item_under_mouse)

            selected_object = self.level_ref.level.get_all_objects()[index.row()]

            self.level_ref.selected_objects = [selected_object]

    def on_right_up(self, event):
        item_under_mouse = self.itemAt(event.position().toPoint())

        if item_under_mouse is None:
            event.ignore()
            return

        index: QModelIndex = self.indexFromItem(item_under_mouse)

        level_object = self.level_ref.level.objects[index.row()]

        self.context_menu.as_list_menu(level_object).popup(event.globalPos())

    def update_content(self):
        level_objects = self.level_ref.get_all_objects()

        self.blockSignals(True)

        for index, level_object in enumerate(level_objects):
            # insert potentially new items
            if (item := self.item(index)) is None:
                self.insertItem(index, level_object.name)
                item = self.item(index)

            # update level objects name and associated data, if it has changed (moved, deleted, added)
            if level_object != item.data(Qt.ItemDataRole.UserRole):
                item.setText(level_object.name)
                item.setData(Qt.ItemDataRole.UserRole, level_object)

            item.setSelected(level_object.selected)

        # in case of object deletion, remove all unnecessary objects
        while self.count() > len(level_objects):
            self.takeItem(self.count() - 1)

        self.blockSignals(False)

        if self.selectedIndexes():
            self.scrollTo(self.selectedIndexes()[-1])

    def selected_objects(self):
        return [self.item(index.row()).data(Qt.ItemDataRole.UserRole) for index in self.selectedIndexes()]

    def on_selection_changed(self):
        # only called by ourselves
        selected_objects = self.selected_objects()

        selection_not_changed = selected_objects == self.level_ref.selected_objects

        if selection_not_changed:
            return
        else:
            self.level_ref.selected_objects = selected_objects
            self.selection_changed.emit(selected_objects)
