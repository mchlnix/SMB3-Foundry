from PySide6.QtGui import QUndoStack
from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from foundry.game.Data import LEVEL_POINTER_COUNT
from foundry.game.level.WorldMap import WorldMap
from foundry.gui.CustomDialog import CustomDialog
from foundry.gui.Spinner import Spinner
from scribe.gui.commands import AddLevelPointer, RemoveLevelPointer, SetScreenCount, SetWorldIndex
from smb3parse.levels import MAX_SCREEN_COUNT, WORLD_COUNT


class EditWorldInfo(CustomDialog):
    def __init__(self, parent: QWidget, world_map: WorldMap):
        super(EditWorldInfo, self).__init__(parent, "Edit World Info")

        self.world_map = world_map

        self.setLayout(QVBoxLayout())

        layout = QVBoxLayout()

        screen_amount_layout = QHBoxLayout()
        screen_amount_layout.addWidget(QLabel("Screen Count"))
        screen_amount_layout.addStretch(1)

        screen_spin_box = Spinner(self, maximum=MAX_SCREEN_COUNT, base=10)
        screen_spin_box.setMinimum(1)
        screen_spin_box.setValue(self.world_map.data.screen_count)
        screen_spin_box.valueChanged.connect(self._change_screen_count)

        screen_amount_layout.addWidget(screen_spin_box)
        layout.addLayout(screen_amount_layout)

        level_count_layout = QHBoxLayout()
        level_count_layout.addWidget(QLabel("Level Count"))
        level_count_layout.addStretch(1)

        level_count_spin_box = Spinner(self, maximum=LEVEL_POINTER_COUNT, base=10)
        level_count_spin_box.setMinimum(0)
        level_count_spin_box.setValue(self.world_map.data.level_count)
        level_count_spin_box.valueChanged.connect(self._change_level_pointer_count)

        level_count_layout.addWidget(level_count_spin_box)
        layout.addLayout(level_count_layout)

        world_size_group = QGroupBox("World Size")
        world_size_group.setLayout(layout)

        self.layout().addWidget(world_size_group)

        layout = QVBoxLayout()

        world_index_layout = QHBoxLayout()
        world_index_layout.addWidget(QLabel("World Number"))
        world_index_layout.addStretch(1)

        index_spin_box = Spinner(self, maximum=WORLD_COUNT, base=10)
        index_spin_box.setMinimum(1)
        index_spin_box.setValue(self.world_map.data.index + 1)
        index_spin_box.valueChanged.connect(self._change_index)

        world_index_layout.addWidget(index_spin_box)

        layout.addLayout(world_index_layout)

        world_data_group = QGroupBox("World Data")
        world_data_group.setLayout(layout)

        self.layout().addWidget(world_data_group)

        self.ok_button = QPushButton("OK")
        self.ok_button.pressed.connect(self.close)

        self.layout().addWidget(self.ok_button)

    @property
    def undo_stack(self) -> QUndoStack:
        return self.window().parent().findChild(QUndoStack, "undo_stack")

    def _change_screen_count(self, new_amount):
        if self.world_map.data.screen_count == new_amount:
            return

        self.undo_stack.push(SetScreenCount(self.world_map, new_amount))

    def _change_index(self, new_index):
        new_index -= 1

        if self.world_map.data.index == new_index:
            return

        self.undo_stack.push(SetWorldIndex(self.world_map, new_index))

    def _change_level_pointer_count(self, new_count):
        current_count = self.world_map.data.level_count

        diff = new_count - current_count

        if diff == 0:
            return

        if diff < 0:
            self._remove_level_pointers(abs(diff))
        else:
            self._add_level_pointers(diff)

    def _remove_level_pointers(self, count):
        if count == 1:
            self.undo_stack.push(RemoveLevelPointer(self.world_map))

        else:
            self.undo_stack.beginMacro(f"Removing {count} Level Pointers")
            for _ in range(count):
                self.undo_stack.push(RemoveLevelPointer(self.world_map))
            self.undo_stack.endMacro()

    def _add_level_pointers(self, count):
        if count == 1:
            self.undo_stack.push(AddLevelPointer(self.world_map))

        else:
            self.undo_stack.beginMacro(f"Adding {count} Level Pointers")
            for _ in range(count):
                self.undo_stack.push(AddLevelPointer(self.world_map))
            self.undo_stack.endMacro()
