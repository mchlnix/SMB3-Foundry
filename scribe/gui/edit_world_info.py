from PySide6.QtCore import QSize
from PySide6.QtGui import QPainter, QPixmap, QUndoStack, Qt
from PySide6.QtWidgets import QGroupBox, QPushButton, QVBoxLayout, QWidget

from foundry.game.Data import LEVEL_POINTER_COUNT
from foundry.game.gfx.drawable.Block import get_worldmap_tile
from foundry.game.level.WorldMap import WorldMap
from foundry.gui import label_and_widget
from foundry.gui.BlockViewer import BlockBank
from foundry.gui.CustomDialog import CustomDialog
from foundry.gui.Spinner import Spinner
from scribe.gui.commands import (
    AddLevelPointer,
    RemoveLevelPointer,
    SetScreenCount,
    SetWorldIndex,
    WorldBottomTile,
    WorldPaletteIndex,
)
from smb3parse.levels import MAX_SCREEN_COUNT, WORLD_COUNT, WORLD_MAP_PALETTE_COUNT


class EditWorldInfo(CustomDialog):
    def __init__(self, parent: QWidget, world_map: WorldMap):
        super(EditWorldInfo, self).__init__(parent, "Edit World Info")

        self.world_map = world_map

        self.setLayout(QVBoxLayout())

        # world size
        layout = QVBoxLayout()

        screen_spin_box = Spinner(self, maximum=MAX_SCREEN_COUNT, base=10)
        screen_spin_box.setMinimum(1)
        screen_spin_box.setValue(self.world_map.data.screen_count)
        screen_spin_box.valueChanged.connect(self._change_screen_count)

        layout.addLayout(label_and_widget("Screen Count", screen_spin_box))

        level_count_spin_box = Spinner(self, maximum=LEVEL_POINTER_COUNT, base=10)
        level_count_spin_box.setMinimum(0)
        level_count_spin_box.setValue(self.world_map.data.level_count)
        level_count_spin_box.valueChanged.connect(self._change_level_pointer_count)

        layout.addLayout(label_and_widget("Level Count", level_count_spin_box))

        world_size_group = QGroupBox("World Size")
        world_size_group.setLayout(layout)

        self.layout().addWidget(world_size_group)

        # world data
        layout = QVBoxLayout()

        index_spin_box = Spinner(self, maximum=WORLD_COUNT, base=10)
        index_spin_box.setMinimum(1)
        index_spin_box.setValue(self.world_map.data.index + 1)
        index_spin_box.valueChanged.connect(self._change_world_index)

        layout.addLayout(label_and_widget("World Number", index_spin_box))

        palette_spin_box = Spinner(self, maximum=WORLD_MAP_PALETTE_COUNT - 1)
        palette_spin_box.setValue(self.world_map.data.palette_index)
        palette_spin_box.valueChanged.connect(self._change_palette_index)

        layout.addLayout(label_and_widget("Color Palette Index", palette_spin_box))

        self.icon_button = QPushButton("")
        self.icon_button.pressed.connect(self._on_button_press)
        self._update_button_icon()

        layout.addLayout(label_and_widget("Bottom Border Tile", self.icon_button))

        world_data_group = QGroupBox("World Data")
        world_data_group.setLayout(layout)

        self.layout().addWidget(world_data_group)

        # ok button
        self.ok_button = QPushButton("OK")
        self.ok_button.pressed.connect(self.close)

        self.layout().addWidget(self.ok_button)

    @property
    def undo_stack(self) -> QUndoStack:
        return self.window().parent().findChild(QUndoStack, "undo_stack")

    def _update_button_icon(self):
        block = get_worldmap_tile(self.world_map.data.bottom_border_tile, self.world_map.data.palette_index)

        block_icon = QPixmap(QSize(32, 32))

        painter = QPainter(block_icon)
        block.draw(painter, 0, 0, 32)
        painter.end()

        self.icon_button.setIcon(block_icon)

    def _on_button_press(self):
        block_bank = BlockBank(None, palette_group=self.world_map.data.palette_index)
        block_bank.setWindowModality(Qt.WindowModal)

        block_bank.last_clicked_index = self.world_map.data.bottom_border_tile

        def _callback():
            block_bank.hide()

            self.undo_stack.push(WorldBottomTile(self.world_map, block_bank.last_clicked_index))

            self._update_button_icon()

        block_bank.clicked.connect(_callback)

        block_bank.showNormal()

    def _change_screen_count(self, new_amount):
        if self.world_map.data.screen_count == new_amount:
            return

        self.undo_stack.push(SetScreenCount(self.world_map, new_amount))

    def _change_world_index(self, new_index):
        new_index -= 1

        if self.world_map.data.index == new_index:
            return

        self.undo_stack.push(SetWorldIndex(self.world_map, new_index))

    def _change_palette_index(self, new_index):
        self.undo_stack.push(WorldPaletteIndex(self.world_map, new_index))

        self._update_button_icon()

        self.world_map.palette_changed.emit()

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
