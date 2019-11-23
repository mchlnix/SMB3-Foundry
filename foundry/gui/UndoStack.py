from typing import List, Optional

from PySide2.QtCore import Signal, SignalInstance
from PySide2.QtWidgets import QWidget

from foundry.game.level.Level import LevelByteData


class UndoStack(QWidget):
    undo_stack_cleared: SignalInstance = Signal()
    undo_stack_saved: SignalInstance = Signal()
    undo_complete: SignalInstance = Signal()

    # bool - redos left
    redo_complete: SignalInstance = Signal(bool)

    def __init__(self):
        super(UndoStack, self).__init__()

        self.undo_stack: List[LevelByteData] = []
        self.undo_index = -1

    def clear(self, new_initial_state: LevelByteData):
        self.undo_stack = [new_initial_state]
        self.undo_index = 0

        self.undo_stack_cleared.emit()

    def save_level_state(self, data: LevelByteData):
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

    @property
    def undo_available(self):
        return self.undo_index > 0

    @property
    def redo_available(self):
        return self.undo_index < len(self.undo_stack) - 1

    def __len__(self):
        return len(self.undo_stack)
