from PySide6.QtWidgets import QMainWindow, QStatusBar

from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from foundry.game.level.LevelRef import LevelRef


class ObjectStatusBar(QStatusBar):
    def __init__(self, parent: QMainWindow, level_ref: LevelRef):
        super(ObjectStatusBar, self).__init__(parent=parent)

        self.level_ref = level_ref
        self.level_ref.data_changed.connect(self.update)

    def clear(self):
        self.clearMessage()

    def update(self):
        selected_objects = self.level_ref.selected_objects

        if selected_objects:
            self._fill(selected_objects[-1])

    def _fill(self, obj: InLevelObject):
        info = obj.get_status_info()

        message_parts = [f"{key}: {value}" for key, value in info]

        self.showMessage(" | ".join(message_parts))
