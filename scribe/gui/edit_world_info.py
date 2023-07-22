from typing import cast

from PySide6.QtCore import QSize
from PySide6.QtGui import QCloseEvent, QPainter, QPixmap, QUndoStack, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from foundry.game.File import ROM
from foundry.game.gfx.drawable.Block import get_worldmap_tile
from foundry.game.level.LevelRef import LevelRef
from foundry.game.level.WorldMap import WorldMap
from foundry.gui import label_and_widget
from foundry.gui.windows.BlockViewer import BlockBank
from foundry.gui.dialogs.CustomDialog import CustomDialog
from foundry.gui.widgets.Spinner import Spinner
from scribe.gui.commands import (
    SetWorldScroll,
    WorldBottomTile,
    WorldMusicIndex,
    WorldPaletteIndex,
    WorldTickPerFrame,
)
from scribe.gui.world_overview import WorldOverview
from smb3parse.constants import MUSIC_THEMES
from smb3parse.levels import NO_MAP_SCROLLING, WORLD_MAP_PALETTE_COUNT


class EditWorldInfo(CustomDialog):
    def __init__(self, parent: QWidget, world_map: WorldMap):
        super(EditWorldInfo, self).__init__(parent, "Edit World Info")

        self.world_map = world_map

        self.setLayout(QVBoxLayout())

        # world data
        layout = QVBoxLayout()

        self.scrolls_check_box = QCheckBox("Scrolls to next screen, when at the edge")
        self.scrolls_check_box.setChecked(self.world_map.data.map_scroll not in [0, NO_MAP_SCROLLING])

        layout.addWidget(self.scrolls_check_box)

        palette_spin_box = Spinner(self, maximum=WORLD_MAP_PALETTE_COUNT - 1)
        palette_spin_box.setValue(self.world_map.data.palette_index)
        palette_spin_box.valueChanged.connect(self._change_palette_index)

        layout.addLayout(label_and_widget("Color Palette Index", palette_spin_box))

        music_dropdown = QComboBox(self)
        music_dropdown.addItems([f"{name} ({value:#X})" for value, name in MUSIC_THEMES.items()])
        music_dropdown.currentIndexChanged.connect(self._change_music_index)
        music_dropdown.setCurrentIndex(list(MUSIC_THEMES.keys()).index(world_map.data.music_index))

        layout.addLayout(label_and_widget("Music Theme", music_dropdown))

        self.icon_button = QPushButton("")
        self.icon_button.clicked.connect(self._on_button_press)
        self._update_button_icon()

        layout.addLayout(label_and_widget("Bottom Border Tile", self.icon_button))

        world_data_group = QGroupBox("World Data")
        world_data_group.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
        world_data_group.setLayout(layout)

        self.orig_tick_per_frame = self.world_map.data.frame_tick_count

        ticks_per_frame_spin_box = Spinner(self, maximum=0xFF, base=10)
        ticks_per_frame_spin_box.setValue(self.world_map.data.frame_tick_count)
        ticks_per_frame_spin_box.valueChanged.connect(self._change_anim_frame)

        layout.addLayout(label_and_widget("Ticks between Animation Frames", ticks_per_frame_spin_box))

        self.animation_hint_label = QLabel()
        layout.addWidget(self.animation_hint_label)

        self.layout().addWidget(world_data_group)

        level_ref = LevelRef()
        level_ref.level = self.world_map

        self.world_overview = WorldOverview(self, level_ref, ROM())
        self.world_overview.data_changed.connect(self._update_hint_labels)
        self.world_overview.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        self.layout().addWidget(self.world_overview)

        self.error_label = QLabel(self.world_overview.status_msg)
        self.layout().addWidget(self.error_label)

        # ok button
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.close)

        self.layout().addWidget(self.ok_button)

        self._update_hint_labels()

    @property
    def undo_stack(self) -> QUndoStack:
        return cast(QUndoStack, self.window().parent().findChild(QUndoStack, "undo_stack"))

    def _update_button_icon(self):
        block = get_worldmap_tile(self.world_map.data.bottom_border_tile, self.world_map.data.palette_index)

        block_icon = QPixmap(QSize(32, 32))

        painter = QPainter(block_icon)
        block.draw(painter, 0, 0, 32)
        painter.end()

        self.icon_button.setIcon(block_icon)

    def _update_hint_labels(self):
        world_number = self.world_map.data.index

        if world_number == 4:
            self.animation_hint_label.setText("Note: World 5 cannot scroll and isn't animated")
        elif world_number == 7:
            self.animation_hint_label.setText("Note: World 8 cannot scroll and the last screen isn't animated")
        else:
            self.animation_hint_label.setText("")

        self.error_label.setText(self.world_overview.status_msg)

        if self.world_overview.valid():
            self.error_label.setStyleSheet("QLabel { }")
        else:
            self.error_label.setStyleSheet("QLabel { color : red; }")

        self.ok_button.setEnabled(self.world_overview.valid())

    def _on_button_press(self):
        block_bank = BlockBank(None, palette_group_index=self.world_map.data.palette_index)
        block_bank.setWindowModality(Qt.WindowModal)

        block_bank.last_clicked_index = self.world_map.data.bottom_border_tile

        def _callback():
            block_bank.hide()

            self.undo_stack.push(WorldBottomTile(self.world_map, block_bank.last_clicked_index))

            self._update_button_icon()

        block_bank.clicked.connect(_callback)

        block_bank.showNormal()

    def _change_anim_frame(self, new_count):
        self.world_map.data.frame_tick_count = new_count

        self.world_map.palette_changed.emit()

    def _change_palette_index(self, new_index):
        self.undo_stack.push(WorldPaletteIndex(self.world_map, new_index))

        self._update_button_icon()

        self.world_map.palette_changed.emit()

    def _change_music_index(self, new_index: int):
        music_index = list(MUSIC_THEMES.keys())[new_index]

        self.undo_stack.push(WorldMusicIndex(self.world_map, music_index))

    def closeEvent(self, event: QCloseEvent):
        if not self.world_overview.valid():
            event.ignore()

            return

        should_scroll = self.scrolls_check_box.isChecked()

        if should_scroll != (self.world_map.data.map_scroll not in [0x00, NO_MAP_SCROLLING]):
            self.undo_stack.push(SetWorldScroll(self.world_map.data, should_scroll))

        self.world_overview.finalize(self.undo_stack)

        curr_tick_per_frame = self.world_map.data.frame_tick_count
        self.world_map.data.frame_tick_count = self.orig_tick_per_frame

        if self.orig_tick_per_frame != curr_tick_per_frame:
            self.undo_stack.push(WorldTickPerFrame(self.world_map, curr_tick_per_frame))
