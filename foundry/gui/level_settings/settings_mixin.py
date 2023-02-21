from typing import Callable

from PySide6.QtGui import QMouseEvent, QUndoStack
from PySide6.QtWidgets import QLayout, QVBoxLayout

from foundry.game.level.LevelRef import LevelRef


class SettingsMixin:
    layout: Callable[[], QLayout]
    update: Callable[[], None]
    closeEvent: Callable[[QMouseEvent], None]

    level_ref: LevelRef
    undo_stack: QUndoStack

    def __init__(self, *args, **kwargs):
        super(SettingsMixin, self).__init__(*args, **kwargs)

        if self.layout() is None:
            QVBoxLayout(self)
