from typing import Optional

from PySide6.QtCore import QObject, Signal, SignalInstance

from foundry.game.level.Level import Level
from foundry.game.level.WorldMap import WorldMap
from smb3parse.objects.object_set import WORLD_MAP_OBJECT_SET


class LevelRef(QObject):
    needs_redraw: SignalInstance = Signal()
    level_changed: SignalInstance = Signal()
    data_changed: SignalInstance = Signal()
    jumps_changed: SignalInstance = Signal()
    palette_changed: SignalInstance = Signal()

    def __init__(self):
        super(LevelRef, self).__init__()
        self._internal_level: Optional[Level] = None

    def load_level(self, level_name: str, object_data_offset: int, enemy_data_offset: int, object_set_number: int):
        if object_set_number == WORLD_MAP_OBJECT_SET:
            self.level = WorldMap(object_data_offset)
        else:
            self.level = Level(level_name, object_data_offset, enemy_data_offset, object_set_number)

        # actively emit, because we weren't connected yet, when the level sent it out
        self.level_changed.emit()
        self.data_changed.emit()

    @property
    def level(self):
        return self._internal_level

    @level.setter
    def level(self, level):
        self._internal_level = level

        level.needs_redraw.connect(self.needs_redraw.emit)
        level.data_changed.connect(self.data_changed.emit)
        level.jumps_changed.connect(self.jumps_changed.emit)
        level.level_changed.connect(self.level_changed.emit)

        if hasattr(level, "palette_changed"):
            level.palette_changed.connect(self.palette_changed.emit)

    @property
    def selected_objects(self):
        return [obj for obj in self._internal_level.get_all_objects() if obj.selected]

    @selected_objects.setter
    def selected_objects(self, selected_objects):
        if selected_objects == self.selected_objects:
            return

        for obj in self._internal_level.get_all_objects():
            obj.selected = obj in selected_objects

        self.data_changed.emit()

    def __getattr__(self, item: str):
        if self._internal_level is None:
            return None
        else:
            return getattr(self._internal_level, item)

    @property
    def fully_loaded(self):
        return bool(self)

    def __bool__(self):
        return self._internal_level is not None and self._internal_level.fully_loaded
