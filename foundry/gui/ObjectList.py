from PySide2.QtGui import QWindow, QMouseEvent, Qt
from PySide2.QtWidgets import QListWidget, QAbstractItemView, QSizePolicy

from foundry.game.level.LevelRef import LevelRef
from foundry.gui.ContextMenu import ContextMenu


class ObjectList(QListWidget):
    def __init__(self, parent: QWindow, level_ref: LevelRef, context_menu: ContextMenu):
        super(ObjectList, self).__init__(parent=parent)

        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.level_ref: LevelRef = level_ref
        self.level_ref.data_changed.connect(self.update)

        self.context_menu = context_menu

        self.itemSelectionChanged.connect(self.on_selection_changed)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.RightButton:
            self.on_right_down(event)
        else:
            return super(ObjectList, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.RightButton:
            self.on_right_up(event)
        else:
            return super(ObjectList, self).mouseReleaseEvent(event)

    def on_right_down(self, event: QMouseEvent):
        item_under_mouse = self.itemAt(event.pos())

        if item_under_mouse is None:
            event.ignore()
            return

        if not item_under_mouse.isSelected():
            self.clearSelection()

            index = self.indexFromItem(item_under_mouse)

            selected_object = self.level_ref.level.get_all_objects()[index.row()]

            self.level_ref.selected_objects = [selected_object]

            self.selection_changed.emit()

    def on_right_up(self, event):
        item_under_mouse = self.itemAt(event.pos())

        if item_under_mouse is None:
            event.ignore()
            return

        self.context_menu.as_list_menu().popup(event.globalPos())

    def update(self):
        level_objects = self.level_ref.get_all_objects()

        labels = [obj.description for obj in level_objects]

        self.blockSignals(True)

        self.clear()

        self.addItems(labels)

        for index, level_object in enumerate(level_objects):
            item = self.item(index)

            item.setData(Qt.UserRole, level_object)
            item.setSelected(level_object.selected)

        self.blockSignals(False)

        if self.selectedIndexes():
            self.scrollTo(self.selectedIndexes()[-1])

    def selected_objects(self):
        return [self.item(index.row()).data(Qt.UserRole) for index in self.selectedIndexes()]

    def on_selection_changed(self):
        selected_objects = self.selected_objects()

        selection_not_changed = selected_objects == self.level_ref.selected_objects

        if selection_not_changed:
            return
        else:
            self.level_ref.selected_objects = selected_objects
