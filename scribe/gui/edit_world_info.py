from PySide6.QtGui import QUndoStack
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from foundry.game.level.WorldMap import WorldMap
from foundry.gui.CustomDialog import CustomDialog
from foundry.gui.Spinner import Spinner
from scribe.gui.commands import SetScreenCount
from smb3parse.levels import MAX_SCREEN_COUNT, WORLD_COUNT


class EditWorldInfo(CustomDialog):
    def __init__(self, parent: QWidget, world_map: WorldMap):
        super(EditWorldInfo, self).__init__(parent, "Edit World Info")

        self.world_map = world_map

        layout = QVBoxLayout()

        screen_amount_layout = QHBoxLayout()
        screen_amount_layout.addWidget(QLabel("# of screens"))
        screen_amount_layout.addStretch(1)

        self.screen_spin_box = Spinner(self, maximum=MAX_SCREEN_COUNT, base=10)
        self.screen_spin_box.setMinimum(1)
        self.screen_spin_box.setValue(self.world_map.internal_world_map.screen_count)
        self.screen_spin_box.valueChanged.connect(self._change_screen_count)

        screen_amount_layout.addWidget(self.screen_spin_box)

        layout.addLayout(screen_amount_layout)

        world_index_layout = QHBoxLayout()
        world_index_layout.addWidget(QLabel("World Index"))
        world_index_layout.addStretch(1)

        self.index_spin_box = Spinner(self, maximum=WORLD_COUNT, base=10)
        self.index_spin_box.setMinimum(1)
        self.index_spin_box.setValue(self.world_map.internal_world_map.data.index + 1)
        self.index_spin_box.valueChanged.connect(self._change_index)

        world_index_layout.addWidget(self.index_spin_box)

        layout.addLayout(world_index_layout)

        self.setLayout(layout)

    @property
    def undo_stack(self) -> QUndoStack:
        return self.window().parent().findChild(QUndoStack, "undo_stack")

    def _change_screen_count(self, new_amount):
        if self.world_map.internal_world_map.screen_count == new_amount:
            return

        self.undo_stack.push(SetScreenCount(self.world_map, new_amount))

    def _change_index(self, new_index):
        new_index -= 1
        world_data = self.world_map.internal_world_map.data

        if world_data.index == new_index:
            return

        world_data.change_index(new_index)
        self.world_map.reread_tiles()
