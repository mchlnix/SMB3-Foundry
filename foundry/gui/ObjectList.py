from PySide2.QtCore import Signal, QItemSelectionModel, QRect
from PySide2.QtGui import QWindow, QMouseEvent, Qt
from PySide2.QtWidgets import QListWidget, QAbstractItemView, QSizePolicy

from foundry.gui.LevelView import LevelView
from foundry.gui.ContextMenu import ContextMenu


class ObjectList(QListWidget):
    selection_changed = Signal()

    def __init__(self, parent: QWindow, level_view_ref: LevelView, context_menu: ContextMenu):
        super(ObjectList, self).__init__(parent=parent)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.level_view_ref: LevelView = level_view_ref

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

            selected_object = self.level_view_ref.level.get_all_objects()[index.row()]

            self.level_view_ref.level.selected_objects = [selected_object]

            self.selection_changed.emit()

    def on_right_up(self, event):
        item_under_mouse = self.itemAt(event.pos())

        if item_under_mouse is None:
            event.ignore()
            return

        self.context_menu.as_list_menu().popup(event.globalPos())

    def update(self):
        level_objects = self.level_view_ref.level.get_all_objects()

        labels = [obj.description for obj in level_objects]

        self.clear()

        self.addItems(labels)

        self.blockSignals(True)

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

        selection_not_changed = selected_objects == self.level_view_ref.level.selected_objects

        if selection_not_changed:
            return

        self.selection_changed.emit()
