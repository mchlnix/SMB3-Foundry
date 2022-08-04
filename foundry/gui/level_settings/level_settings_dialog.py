from PySide6.QtGui import QUndoStack

from foundry.game.level.LevelRef import LevelRef
from foundry.gui.CustomDialog import CustomDialog
from foundry.gui.level_settings.auto_scroll_mixin import AutoScrollMixin
from foundry.gui.level_settings.boom_boom_mixin import BoomBoomMixin
from foundry.gui.level_settings.pipe_pair_mixin import PipePairMixin


class LevelSettingsDialog(PipePairMixin, BoomBoomMixin, AutoScrollMixin, CustomDialog):
    def __init__(self, parent, level_ref: LevelRef):
        self.level_ref = level_ref

        super(LevelSettingsDialog, self).__init__(parent)

        self.setWindowTitle("Other Level Settings")

        self.update()

    @property
    def undo_stack(self) -> QUndoStack:
        return self.parent().window().findChild(QUndoStack, "undo_stack")

    def update(self):
        super(LevelSettingsDialog, self).update()

    def closeEvent(self, event):
        super(LevelSettingsDialog, self).closeEvent(event)
