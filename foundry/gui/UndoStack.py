from typing import List, Optional

import wx
from PySide2.QtCore import Signal
from PySide2.QtWidgets import QWidget

from foundry.game.level.Level import LevelByteData

UNDO_STACK_ID = wx.NewId()


class UndoStack(QWidget):
    undo_stack_cleared = Signal()
    undo_stack_saved = Signal()
    undo_complete = Signal()

    # bool - redos left
    redo_complete = Signal(bool)

    def __init__(self, parent: QWidget):
        super(UndoStack, self).__init__(parent)

        self.undo_stack: List[LevelByteData] = []
        self.undo_index = -1

    def clear(self, new_initial_state: LevelByteData):
        self.undo_stack = [new_initial_state]
        self.undo_index = 0

        self.undo_stack_cleared.emit()

    def save_state(self, data: LevelByteData):
        self.undo_index += 1

        self.undo_stack = self.undo_stack[: self.undo_index]

        self.undo_stack.append(data)

        self.undo_stack_saved.emit()

    def undo(self) -> Optional[LevelByteData]:
        if not self.undo_stack:
            return None

        self.undo_index -= 1

        data = self.undo_stack[self.undo_index]

        self.undo_complete.emit()

        return data

    def redo(self) -> Optional[LevelByteData]:
        if self.undo_index + 1 == len(self.undo_stack):
            return None

        self.undo_index += 1

        data = self.undo_stack[self.undo_index]

        self.redo_complete.emit(self.undo_index + 1 < len(self.undo_stack))

        return data
