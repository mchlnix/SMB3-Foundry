from typing import Optional

from PySide6.QtCore import QObject, Signal, SignalInstance

from foundry.game.level.Level import Level


class LevelRef(QObject):
    data_changed: SignalInstance = Signal()
    jumps_changed: SignalInstance = Signal()

    def __init__(self):
        super(LevelRef, self).__init__()
        self._internal_level: Optional[Level] = Level()

    def load_level(self, level_name: str, object_data_offset: int, enemy_data_offset: int, object_set_number: int):
        self.level = Level(level_name, object_data_offset, enemy_data_offset, object_set_number)

        # actively emit, because we weren't connected yet, when the level sent it out
        self.data_changed.emit()

    @property
    def level(self):
        return self._internal_level

    @level.setter
    def level(self, level):
        self._internal_level = level

        self._internal_level.data_changed.connect(self.data_changed.emit)
        self._internal_level.jumps_changed.connect(self.jumps_changed.emit)

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

    def undo(self):
        if not self.undo_stack.undo_available:
            return

        self.set_level_state(*self.undo_stack.undo())

    def redo(self):
        if not self.undo_stack.redo_available:
            return

        self.set_level_state(*self.undo_stack.redo())

    def set_level_state(self, object_data, enemy_data):
        self.level.from_bytes(object_data, enemy_data, new_level=False)
        self.level.changed = True

        self.data_changed.emit()

    def import_undo_stack_data(self, undo_index, byte_data):
        self.level.undo_stack.import_data(undo_index, byte_data)

        if byte_data:
            self.set_level_state(*byte_data[undo_index])

    def save_level_state(self):
        self.undo_stack.save_level_state(self._internal_level.to_bytes())
        self.level.changed = True

        self.data_changed.emit()

    def __bool__(self):
        return self._internal_level.fully_loaded
