from typing import List, Optional

import wx

from foundry.game.level.Level import LevelByteData
from foundry.gui.Events import (
    UndoCompleteEvent,
    UndoStackClearedEvent,
    UndoStateSavedEvent,
    RedoCompleteEvent,
)

UNDO_STACK_ID = wx.NewId()


class UndoStack(wx.Window):
    def __init__(self, parent: wx.Window):
        super(UndoStack, self).__init__(parent)
        self.SetId(UNDO_STACK_ID)

        self.undo_stack: List[LevelByteData] = []
        self.undo_index = -1

    def clear(self, new_initial_state: LevelByteData):
        self.undo_stack = [new_initial_state]
        self.undo_index = 0

        wx.PostEvent(self, UndoStackClearedEvent(self.GetId()))

    def save_state(self, data: LevelByteData):
        self.undo_index += 1

        self.undo_stack = self.undo_stack[: self.undo_index]

        self.undo_stack.append(data)

        wx.PostEvent(self, UndoStateSavedEvent(self.GetId()))

    def undo(self) -> Optional[LevelByteData]:
        if not self.undo_stack:
            return None

        self.undo_index -= 1

        data = self.undo_stack[self.undo_index]

        evt = UndoCompleteEvent(id=self.GetId(), undos_left=self.undo_index > -1)

        wx.PostEvent(self, evt)

        return data

    def redo(self) -> Optional[LevelByteData]:
        if self.undo_index + 1 == len(self.undo_stack):
            return None

        self.undo_index += 1

        data = self.undo_stack[self.undo_index]

        evt = RedoCompleteEvent(
            id=self.GetId(), redos_left=self.undo_index + 1 < len(self.undo_stack)
        )

        wx.PostEvent(self, evt)

        return data
