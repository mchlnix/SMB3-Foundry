from PySide6.QtGui import QAction, Qt
from PySide6.QtWidgets import QMenu

from scribe.gui.edit_world_info import EditWorldInfo


class EditMenu(QMenu):
    def __init__(self, parent):
        super(EditMenu, self).__init__("&Edit", parent)

        self.triggered.connect(self.on_menu)

        self.undo_action = self.undo_stack.createUndoAction(self)
        self.undo_action.setShortcut(Qt.CTRL + Qt.Key_Z)

        self.redo_action = self.undo_stack.createRedoAction(self)
        self.redo_action.setShortcut(Qt.CTRL + Qt.SHIFT + Qt.Key_Z)

        self.addAction(self.undo_action)
        self.addAction(self.redo_action)

        self.addSeparator()

        self.clear_tiles_action = self.addAction("Clear &Tiles")
        self.clear_level_pointers_action = self.addAction("Clear All &Level Pointers")
        self.clear_sprites_action = self.addAction("Clear All &Sprites")

        self.addSeparator()

        self.edit_world_info = self.addAction("Edit World Info")

    def on_menu(self, action: QAction):
        if action is self.clear_tiles_action:
            self.world_view.clear_tiles()
        elif action is self.clear_sprites_action:
            self.world_view.clear_sprites()
        elif action is self.clear_level_pointers_action:
            self.world_view.clear_level_pointers()
        elif action is self.edit_world_info:
            EditWorldInfo(self.parent(), self.world_view.level_ref.level).exec()

    @property
    def undo_stack(self):
        return self.parent().undo_stack

    @property
    def world_view(self):
        return self.parent().world_view
