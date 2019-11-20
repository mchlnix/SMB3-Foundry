from typing import Union

from PySide2.QtWidgets import QStatusBar, QMainWindow

from foundry.game.gfx.objects.EnemyItem import EnemyObject
from foundry.game.gfx.objects.LevelObject import LevelObject
from foundry.gui.LevelView import LevelView


class ObjectStatusBar(QStatusBar):
    def __init__(self, parent: QMainWindow, level_view_ref: LevelView):
        super(ObjectStatusBar, self).__init__(parent=parent)

        self.level_view_ref = level_view_ref

    def clear(self):
        self.clearMessage()

    def update(self):
        selected_objects = self.level_view_ref.level.selected_objects

        if selected_objects:
            self._fill(selected_objects[-1])

    def _fill(self, obj: Union[LevelObject, EnemyObject]):
        info = obj.get_status_info()

        message_parts = []

        for key, value in info:
            message_parts.append(f"{key}: {value}")

        self.showMessage(" | ".join(message_parts))
