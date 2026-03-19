from PySide6.QtWidgets import QMenu


class DebugMenu(QMenu):
    def __init__(self, title="&Debug"):
        super(DebugMenu, self).__init__(title)

        self.setTitle("Debug")
        self.export_stack_action = self.addAction("Export UndoStack")
        self.replay_stack_action = self.addAction("Replay UndoStack")
