from typing import List, Optional, Tuple

from PySide2.QtWidgets import QWidget

from foundry.game.level import LevelByteData


class UndoStack(QWidget):
    def __init__(self):
        super(UndoStack, self).__init__()

        self.undo_stack: List[LevelByteData] = []
        self.undo_index = -1

    def clear(self, new_initial_state: LevelByteData):
        self.undo_stack = [new_initial_state]
        self.undo_index = 0

    def save_level_state(self, data: LevelByteData):
        self.undo_index += 1

        self.undo_stack = self.undo_stack[: self.undo_index]

        self.undo_stack.append(data)

    def undo(self) -> Optional[LevelByteData]:
        if not self.undo_stack:
            return None

        self.undo_index -= 1

        data = self.undo_stack[self.undo_index]

        return data

    def redo(self) -> Optional[LevelByteData]:
        if self.undo_index + 1 == len(self.undo_stack):
            return None

        self.undo_index += 1

        data = self.undo_stack[self.undo_index]

        return data

    @property
    def undo_available(self):
        return self.undo_index > 0

    @property
    def redo_available(self):
        return self.undo_index < len(self.undo_stack) - 1

    def import_data(self, stack_index: int, stack_bytes: List[LevelByteData]) -> None:
        self.undo_index = stack_index
        self.undo_stack = stack_bytes

    def export_data(self) -> Tuple[int, List[LevelByteData]]:
        return self.undo_index, self.undo_stack

    def __len__(self):
        return len(self.undo_stack)
