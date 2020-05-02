from PySide2.QtCore import QMimeData, QTimer
from PySide2.QtGui import QMouseEvent, QWindow, Qt
from PySide2.QtWidgets import QListWidget, QSizePolicy

from foundry.game.level.LevelRef import LevelRef
from foundry.gui.ContextMenu import ContextMenu

LEVEL_OBJECT_LIST_MIME_TYPE = "application/foundry"


class ObjectList(QListWidget):
    def __init__(self, parent: QWindow, level_ref: LevelRef, context_menu: ContextMenu):
        super(ObjectList, self).__init__(parent=parent)

        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.setDragDropMode(self.InternalMove)
        self.setSelectionMode(self.ExtendedSelection)

        self.level_ref: LevelRef = level_ref
        self.level_ref.data_changed.connect(self.update_content)

        self.context_menu = context_menu

        self.itemSelectionChanged.connect(self.on_selection_changed)
        self.model().rowsMoved.connect(self.on_objects_moved)

        self.redraw_timer = QTimer(self)
        self.redraw_timer.setSingleShot(True)

        self.redraw_timer.timeout.connect(self.level_ref.data_changed.emit)

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

    def update_content(self):
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

    def mimeData(self, items):
        """
        Since we have user data on the items, we need to implement this method, otherwise moving the items is
        deactivated automatically. The actual data doesn't matter in our case, however.
        """
        mime_data = QMimeData()

        mime_data.setData(LEVEL_OBJECT_LIST_MIME_TYPE, bytes())

        return mime_data

    def mimeTypes(self):
        return super(ObjectList, self).mimeTypes() + [LEVEL_OBJECT_LIST_MIME_TYPE]

    def on_objects_moved(self, _, start: int, end: int, __, target: int):
        for index in range(end, start - 1, -1):
            self.level_ref.level.objects.insert(target, self.level_ref.level.objects.pop(index))

        self.redraw_timer.start(10)

    def selected_objects(self):
        return [self.item(index.row()).data(Qt.UserRole) for index in self.selectedIndexes()]

    def on_selection_changed(self):
        selected_objects = self.selected_objects()

        selection_not_changed = selected_objects == self.level_ref.selected_objects

        if selection_not_changed:
            return
        else:
            self.level_ref.selected_objects = selected_objects
