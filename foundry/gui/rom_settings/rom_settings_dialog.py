from PySide6.QtCore import Signal, SignalInstance
from PySide6.QtGui import QUndoStack

from foundry.game.level.LevelRef import LevelRef
from foundry.gui.CustomDialog import CustomDialog
from foundry.gui.rom_settings.managed_levels_mixin import ManagedLevelsMixin


class RomSettingsDialog(ManagedLevelsMixin, CustomDialog):
    needs_gui_update: SignalInstance = Signal()

    def __init__(self, parent, level_ref: LevelRef):
        self.level_ref = level_ref

        super(RomSettingsDialog, self).__init__(parent)

        self.setWindowTitle("ROM Settings")

        self.update()

    @property
    def undo_stack(self) -> QUndoStack:
        return self.parent().window().findChild(QUndoStack, "undo_stack")

    def update(self):
        super(RomSettingsDialog, self).update()

    def closeEvent(self, event):
        super(RomSettingsDialog, self).closeEvent(event)
