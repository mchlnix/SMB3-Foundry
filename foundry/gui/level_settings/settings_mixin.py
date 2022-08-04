from typing import Callable, Optional

from PySide6.QtGui import QMouseEvent, QUndoStack
from PySide6.QtWidgets import QLayout, QVBoxLayout

from foundry.game.level.LevelRef import LevelRef


class SettingsMixin:
    layout: Callable[[], Optional[QLayout]]
    update: Callable[[], None]
    closeEvent: Callable[[QMouseEvent], None]

    level_ref: LevelRef
    undo_stack: QUndoStack

    def __init__(self, parent):
        super(SettingsMixin, self).__init__(parent)

        if self.layout() is None:
            QVBoxLayout(self)
