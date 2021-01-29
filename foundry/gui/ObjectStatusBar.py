from typing import Union

from PySide2.QtWidgets import QStatusBar, QMainWindow

from foundry.game.gfx.objects.EnemyItem import EnemyObject
from foundry.game.gfx.objects.LevelObj.ObjectLikeLevelObjectRendererAdapter import (
    ObjectLikeLevelObjectRendererAdapter as LevelObject,
)
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

    def _fill(self, obj: Union[LevelObject, EnemyObject]):
        info = obj.get_status_info()

        message_parts = []

        for key, value in info:
            message_parts.append(f"{key}: {value}")

        self.showMessage(" | ".join(message_parts))
