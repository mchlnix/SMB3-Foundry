from PySide6.QtCore import Signal, SignalInstance
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QMainWindow, QTabWidget

from scribe.gui.tool_window.block_picker import BlockPicker
from scribe.gui.tool_window.level_pointer_list import LevelPointerList
from scribe.gui.tool_window.locks_list import LocksList
from scribe.gui.tool_window.sprite_list import SpriteList


class ToolWindow(QMainWindow):
    tile_selected: SignalInstance = Signal(int)
    """Is fired, when a tile has been selected through the tile picker. int-argument is the tile id."""

    sprite_selection_changed: SignalInstance = Signal(int)
    level_pointer_selection_changed: SignalInstance = Signal(int)
    locks_selection_changed: SignalInstance = Signal(int)

    def __init__(self, parent, level_ref):
        super(ToolWindow, self).__init__(parent)

        self.setWindowFlag(Qt.Tool, True)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)

        self.setWindowTitle("Tool Window - SMB3 Scribe")

        self.level_ref = level_ref

        self.tabbed_widget = QTabWidget()

        self.tile_picker = BlockPicker(level_ref)
        self.tile_picker.tile_selected.connect(self.tile_selected.emit)

        self.level_pointer_list = LevelPointerList(self, level_ref)
        self.level_pointer_list.selection_changed.connect(self.level_pointer_selection_changed.emit)

        self.sprite_list = SpriteList(self, level_ref)
        self.sprite_list.selection_changed.connect(self.sprite_selection_changed.emit)

        self.locks_list = LocksList(self, level_ref)
        self.locks_list.selection_changed.connect(self.locks_selection_changed.emit)

        self.tabbed_widget.addTab(self.tile_picker, "Tiles")
        self.tabbed_widget.addTab(self.level_pointer_list, "Level Pointers")
        self.tabbed_widget.addTab(self.sprite_list, "Sprites")
        self.tabbed_widget.addTab(self.locks_list, "Locks and Bridges")

        # clear selection if you change the tab
        self.tabbed_widget.currentChanged.connect(lambda _: self.level_pointer_list.clearSelection())
        self.tabbed_widget.currentChanged.connect(lambda _: self.sprite_list.clearSelection())
        self.tabbed_widget.currentChanged.connect(lambda _: self.locks_list.clearSelection())

        self.setCentralWidget(self.tabbed_widget)

    def set_zoom(self, zoom_level=2):
        self.tile_picker.set_zoom(zoom_level)
