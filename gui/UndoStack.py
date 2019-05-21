import wx

from Events import (
    UndoCompleteEvent,
    UndoStackClearedEvent,
    UndoStateSavedEvent,
    RedoCompleteEvent,
)

UNDO_STACK_ID = wx.NewId()


class UndoStack(wx.Window):
    def __init__(self, parent):
        super(UndoStack, self).__init__(parent)
        self.id = UNDO_STACK_ID

        self.undo_stack = []
        self.undo_index = -1

    def clear(self, new_initial_state):
        self.undo_stack = [new_initial_state]
        self.undo_index = 0

        wx.PostEvent(self, UndoStackClearedEvent(self.id))

    def save_state(self, data):
        self.undo_index += 1

        self.undo_stack = self.undo_stack[: self.undo_index]

        self.undo_stack.append(data)

        wx.PostEvent(self, UndoStateSavedEvent(self.id))

    def undo(self):
        if not self.undo_stack:
            return

        self.undo_index -= 1

        data = self.undo_stack[self.undo_index]

        evt = UndoCompleteEvent(id=self.id, undos_left=self.undo_index > -1)

        wx.PostEvent(self, evt)

        return data

    def redo(self):
        if self.undo_index + 1 == len(self.undo_stack):
            return

        self.undo_index += 1

        data = self.undo_stack[self.undo_index]

        evt = RedoCompleteEvent(
            id=self.id, redos_left=self.undo_index + 1 < len(self.undo_stack)
        )

        wx.PostEvent(self, evt)

        return data
