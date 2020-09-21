from math import ceil

from PySide2.QtCore import QSize, QRect, QPoint
from PySide2.QtGui import QPaintEvent, QPainter, QColor, QBrush, QResizeEvent, QMouseEvent, Qt
from PySide2.QtWidgets import (
    QStyle, QComboBox, QToolBar, QWidget, QLayout, QStatusBar, QVBoxLayout, QGridLayout, QSizePolicy, QHBoxLayout
)

from foundry import icon
from foundry.game.File import ROM
from foundry.game.gfx.PatternTableHandler import PatternTableHandler
from foundry.game.gfx.Palette import bg_color_for_object_set, load_palette
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.drawable.Tile import Tile
from foundry.gui.QMainWindow.ChildWindow import ChildWindow
from foundry.gui.LevelSelector import OBJECT_SET_ITEMS
from foundry.core.Settings.util import get_setting


class BlockViewer(ChildWindow):
    def __init__(self, parent):
        super(BlockViewer, self).__init__(parent, "Block Viewer")
        self.main = parent

        self._object_set = 0
        self.sprite_bank = BlockBank(parent=self, object_set=self.object_set)
        self.add_toolbox("Block Viewer", self.sprite_bank, Qt.LeftToolBarArea)

        self.pattern_table = PatternDisplayer(parent=self, object_set=self.object_set)
        self.add_toolbox("Pattern Viewer", self.pattern_table, Qt.RightToolBarArea)

        self.block_selector = BlockSelector(parent=self, object_set=self.object_set)
        self.block_selector.zoom_in()
        self.add_toolbox("Block Selector", self.block_selector, Qt.LeftToolBarArea)

        self.toolbar = QToolBar(self)

        self.save_action = self.toolbar.addAction("Save")
        self.save_action.triggered.connect(self.save)

        self.bank_dropdown = QComboBox(parent=self.toolbar)
        self.bank_dropdown.addItems(OBJECT_SET_ITEMS)
        self.bank_dropdown.setCurrentIndex(0)

        self.bank_dropdown.currentIndexChanged.connect(self.on_combo)

        self.toolbar.addWidget(self.bank_dropdown)

        self.addToolBar(self.toolbar)

        self.setStatusBar(QStatusBar(self))

    def force_update_level_view(self):
        self.main.force_update_level_view()

    def save(self):
        tsa = self.sprite_bank.tsa
        ROM().bulk_write(tsa, ROM().tsa_offset(self.object_set))
        self.force_update_level_view()

    def pattern_selected(self, selected):
        self.block_selector.pattern_selected(selected)

    def block_selected(self, selected):
        self.block_selector.block_selected(selected)

    def set_object_set(self, obj_set):
        self.object_set = obj_set
        self.block_selector.update_obj_set(obj_set)
        self.pattern_table.update_object_set(obj_set)

    def set_tsa(self, tsa):
        self.sprite_bank.set_tsa(tsa)

    @property
    def object_set(self):
        return self._object_set

    @object_set.setter
    def object_set(self, value):
        self._object_set = value

        self._after_object_set()

    def prev_object_set(self):
        self.object_set = max(self.object_set - 1, 0)

    def next_object_set(self):
        self.object_set = min(self.object_set + 1, 0xE)

    def _after_object_set(self):
        self.sprite_bank.object_set = self.object_set

        self.bank_dropdown.setCurrentIndex(self.object_set)

        self.sprite_bank.update()

    def on_combo(self, _):
        self.object_set = self.bank_dropdown.currentIndex()

        self.sprite_bank.object_set = self.object_set

        self.sprite_bank.update()

    def add_toolbox(self, name, widget, side):
        toolbar = QToolBar(name, self)
        toolbar.setContextMenuPolicy(Qt.PreventContextMenu)
        toolbar.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        toolbar.setOrientation(Qt.Horizontal)
        toolbar.setFloatable(False)
        toolbar.toggleViewAction().setChecked(True)
        if isinstance(widget, list):
            for wig in widget:
                toolbar.addWidget(wig)
        else:
            toolbar.addWidget(widget)
        toolbar.setAllowedAreas(Qt.LeftToolBarArea | Qt.RightToolBarArea | Qt.TopToolBarArea | Qt.BottomToolBarArea)

        self.addToolBar(side, toolbar)
        return toolbar


class BlockSelector(QWidget):
    def __init__(self, parent, object_set=0, zoom=2, tsa_data=None):
        super(BlockSelector, self).__init__(parent)
        self.main = parent
        self.setMouseTracking(True)

        self.zoom_step = 256
        self.object_set = object_set
        self.zoom = zoom

        self.block = 0
        self.selected = 0
        self.tsa_data = ROM().get_tsa_data(self.object_set)

        self._size = QSize(Block.WIDTH * self.zoom, Block.HEIGHT * self.zoom)

        self.setFixedSize(self._size)

    @property
    def block_length(self):
        return Block.WIDTH * self.zoom

    def update_obj_set(self, set):
        self.object_set = set
        self.tsa_data = ROM().get_tsa_data(self.object_set)
        self.update()

    def block_selected(self, block):
        self.block = block
        self.update()

    def pattern_selected(self, block):
        self.tsa_data[self.block + (self.selected * 0x100)] = block
        self.main.set_tsa(self.tsa_data)
        self.update()

    def resizeEvent(self, event: QResizeEvent):
        self.update()

    def zoom_in(self):
        self.zoom += 1
        self._after_zoom()

    def zoom_out(self):
        self.zoom = max(self.zoom - 1, 1)
        self._after_zoom()

    def _after_zoom(self):
        new_size = QSize(Block.WIDTH * self.zoom, Block.HEIGHT * self.zoom)
        self.setFixedSize(new_size)

    def mouseReleaseEvent(self, event: QMouseEvent):
        released_button = event.button()

        if released_button == Qt.LeftButton:
            self.on_left_mouse_button_up(event)
        elif released_button == Qt.RightButton:
            pass #self.on_right_mouse_button_up(event)

    def on_left_mouse_button_up(self, event: QMouseEvent):
        x, y = event.pos().toTuple()

        column = x // (self.block_length // 2)
        row = y // (self.block_length // 2)

        self.selected = (column * 2) + row
        self.update()

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)

        bg_color = bg_color_for_object_set(self.object_set, 0)
        painter.setBrush(QBrush(bg_color))
        painter.drawRect(QRect(QPoint(0, 0), self.size()))

        graphics_set = PatternTableHandler(self.object_set)
        palette = load_palette(self.object_set, 0)

        block_length = Block.WIDTH * self.zoom
        block = Block.from_rom(self.block, palette, graphics_set, self.tsa_data)
        block.draw(painter, 0, 0, block_length)

        tile_len = self.block_length // 2
        painter.setPen(QColor(0xFF, 0xFF, 0xFF))
        painter.setBrush(QColor(0, 0, 0, 0))
        painter.drawRect(QRect((self.selected // 2) * tile_len, (self.selected % 2) * tile_len, tile_len, tile_len))


class BlockBank(QWidget):
    def __init__(self, parent, object_set=0, zoom=2):
        super(BlockBank, self).__init__(parent)
        self.main = parent

        self.sprites = 256
        self.zoom_step = 256
        self.sprites_horiz = 16
        self.sprites_vert = ceil(self.sprites / self.sprites_horiz)

        self.object_set = object_set
        self.zoom = zoom

        self._size = QSize(self.sprites_horiz * Block.WIDTH * self.zoom, self.sprites_vert * Block.HEIGHT * self.zoom)

        self.setFixedSize(self._size)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.toolbar = QToolBar(self)
        self.prev_os_action = self.toolbar.addAction("<")
        self.prev_os_action.triggered.connect(self.prev_object_set)
        self.next_os_action = self.toolbar.addAction(">")
        self.next_os_action.triggered.connect(self.next_object_set)
        self.zoom_out_action = self.toolbar.addAction("-")
        self.zoom_out_action.triggered.connect(self.zoom_out)
        self.zoom_in_action = self.toolbar.addAction("+")
        self.zoom_in_action.triggered.connect(self.zoom_in)

        self.bank_dropdown = QComboBox(parent=self.toolbar)
        self.bank_dropdown.addItems(OBJECT_SET_ITEMS)
        self.bank_dropdown.setCurrentIndex(0)
        self.bank_dropdown.currentIndexChanged.connect(self.on_combo)
        self.toolbar.addWidget(self.bank_dropdown)

        self.block_viewer = BlockBankViewer(self, self.object_set, self.zoom)

        layout.addWidget(self.toolbar)
        self.layout().setSizeConstraint(QLayout.SetFixedSize)

        layout.addWidget(self.block_viewer)

        self.status_bar = QStatusBar(self)
        layout.addWidget(self.status_bar)

    def selected(self, block):
        self.main.block_selected(block)

    def zoom_in(self):
        self.block_viewer.zoom_in()

    def zoom_out(self):
        self.block_viewer.zoom_out()

    @property
    def tsa(self):
        return self.block_viewer.tsa_data

    def set_tsa(self, tsa):
        self.block_viewer.set_tsa(tsa)

    def prev_object_set(self):
        self.object_set = max(self.object_set - 1, 0)
        self._after_object_set()

    def next_object_set(self):
        self.object_set = min(self.object_set + 1, 0xE)
        self._after_object_set()

    def _after_object_set(self):
        self.block_viewer.object_set = self.object_set
        self.main.set_object_set(self.object_set)
        self.bank_dropdown.setCurrentIndex(self.object_set)

    def on_combo(self, _):
        self.object_set = self.bank_dropdown.currentIndex()
        self.block_viewer.object_set = self.object_set
        self.main.set_object_set(self.object_set)


class BlockBankViewer(QWidget):
    def __init__(self, parent: BlockBank, object_set=0, zoom=2):
        super(BlockBankViewer, self).__init__(parent)
        self.block_bank = parent
        self.setMouseTracking(True)
        self._object_set = object_set
        self.tsa_data = ROM().get_tsa_data(self.object_set)
        self.sprites = 256
        self.zoom_step = 256
        self.sprites_horiz = 16
        self.sprites_vert = ceil(self.sprites / self.sprites_horiz)
        self.selected = 0

        self.zoom = zoom

        self._size = QSize(self.sprites_horiz * Block.WIDTH * self.zoom, self.sprites_vert * Block.HEIGHT * self.zoom)

        self.setFixedSize(self._size)
        self.setMinimumSize(self.sizeHint())

    @property
    def object_set(self):
        return self._object_set

    @object_set.setter
    def object_set(self, set: int):
        self._object_set = set
        self.tsa_data = ROM().get_tsa_data(self.object_set)
        self.update()

    @property
    def block_length(self):
        return Block.WIDTH * self.zoom

    def set_tsa(self, tsa):
        self.tsa_data = tsa
        self.update()

    def sizeHint(self):
        return self.current_size

    @property
    def current_size(self):
        return QSize(self.block_length * 16, self.block_length * 16)

    def resizeEvent(self, event: QResizeEvent):
        self.update()

    def zoom_in(self):
        self.zoom += 1
        self._after_zoom()

    def zoom_out(self):
        self.zoom = max(self.zoom - 1, 1)
        self._after_zoom()

    def _after_zoom(self):
        new_size = QSize(self.sprites_horiz * Block.WIDTH * self.zoom, self.sprites_vert * Block.HEIGHT * self.zoom)
        self.setFixedSize(new_size)

    def mouseMoveEvent(self, event: QMouseEvent):
        x, y = event.pos().toTuple()

        block_length = Block.WIDTH * self.zoom

        column = x // block_length
        row = y // block_length

        dec_index = row * self.sprites_horiz + column
        hex_index = hex(dec_index).upper().replace("X", "x")

        status_message = f"Row: {row}, Column: {column}, Index: {dec_index} / {hex_index}"
        self.block_bank.status_bar.showMessage(status_message)

    def mouseReleaseEvent(self, event: QMouseEvent):
        released_button = event.button()

        if released_button == Qt.LeftButton:
            self.on_left_mouse_button_up(event)
        elif released_button == Qt.RightButton:
            pass #self.on_right_mouse_button_up(event)

    def on_left_mouse_button_up(self, event: QMouseEvent):
        x, y = event.pos().toTuple()

        column = x // self.block_length
        row = y // self.block_length

        self.selected = column + (row * 0x10)
        self.block_bank.selected(self.selected)
        self.update()

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)

        graphics_set = PatternTableHandler(self.object_set)
        palette = load_palette(self.object_set, 0)

        transparent = get_setting("block_transparency", True)

        horizontal = self.sprites_horiz

        block_length = Block.WIDTH * self.zoom

        for i in range(self.sprites):
            block = Block.from_rom(i, palette, graphics_set, self.tsa_data)

            x = (i % horizontal) * block_length
            y = (i // horizontal) * block_length
            selected = i == self.selected

            block.draw(painter, x, y, block_length, selected=selected, transparent=transparent)


class PatternDisplayer(QWidget):
    def __init__(self, parent, object_set=0, zoom=2):
        super(PatternDisplayer, self).__init__(parent)
        self.main = parent

        self.sprites = 256
        self.zoom_step = 256
        self.sprites_horiz = 16
        self.sprites_vert = ceil(self.sprites / self.sprites_horiz)

        self.object_set = object_set
        self.zoom = zoom

        self._size = QSize(self.sprites_horiz * Block.WIDTH * self.zoom, self.sprites_vert * Block.HEIGHT * self.zoom)

        self.setFixedSize(self._size)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.toolbar = QToolBar(self)
        self.prev_os_action = self.toolbar.addAction("<")
        self.prev_os_action.triggered.connect(self.prev_object_set)
        self.next_os_action = self.toolbar.addAction(">")
        self.next_os_action.triggered.connect(self.next_object_set)
        self.zoom_out_action = self.toolbar.addAction("-")
        self.zoom_out_action.triggered.connect(self.zoom_out)
        self.zoom_in_action = self.toolbar.addAction("+")
        self.zoom_in_action.triggered.connect(self.zoom_in)

        self.bank_dropdown = QComboBox(parent=self.toolbar)
        self.bank_dropdown.addItems(OBJECT_SET_ITEMS)
        self.bank_dropdown.setCurrentIndex(0)
        self.bank_dropdown.currentIndexChanged.connect(self.on_combo)
        self.toolbar.addWidget(self.bank_dropdown)

        self.pattern_viewer = PatternDisplayerViewer(self, self.object_set, self.zoom)

        layout.addWidget(self.toolbar)
        self.layout().setSizeConstraint(QLayout.SetFixedSize)

        layout.addWidget(self.pattern_viewer)

        self.status_bar = QStatusBar(self)
        layout.addWidget(self.status_bar)
        self.setMinimumSize(self.sizeHint())

    def update_object_set(self, obj_set):
        self.pattern_viewer.update_object_set(obj_set)

    def selected(self, block):
        self.main.pattern_selected(block)

    def zoom_in(self):
        self.pattern_viewer.zoom_in()

    def zoom_out(self):
        self.pattern_viewer.zoom_out()

    def prev_object_set(self):
        self.object_set = max(self.object_set - 1, 0)
        self._after_object_set()

    def next_object_set(self):
        self.object_set = min(self.object_set + 1, 0xE)
        self._after_object_set()

    def _after_object_set(self):
        self.pattern_viewer.object_set = self.object_set
        self.bank_dropdown.setCurrentIndex(self.object_set)

    def on_combo(self, _):
        self.object_set = self.bank_dropdown.currentIndex()
        self.pattern_viewer.object_set = self.object_set


class PatternDisplayerViewer(QWidget):
    def __init__(self, parent: PatternDisplayer, object_set=0, zoom=2):
        super(PatternDisplayerViewer, self).__init__(parent)
        self.pattern_display = parent

        self.setMouseTracking(True)

        self.sprites = 256
        self.zoom_step = 256
        self.sprites_horiz = 16
        self.sprites_vert = ceil(self.sprites / self.sprites_horiz)
        self.selected = 0

        self.object_set = object_set
        self.zoom = zoom

        self._size = QSize(self.sprites_horiz * Block.WIDTH * self.zoom, self.sprites_vert * Block.HEIGHT * self.zoom)

        self.setFixedSize(self._size)
        self.setMinimumSize(self.sizeHint())

    def update_object_set(self, obj_set):
        self.object_set = obj_set
        self.update()

    @property
    def block_length(self):
        return Block.WIDTH * self.zoom

    def resizeEvent(self, event: QResizeEvent):
        self.update()

    def sizeHint(self):
        return self.current_size

    @property
    def current_size(self):
        return QSize(self.block_length * 16, self.block_length * 16)

    def zoom_in(self):
        self.zoom += 1
        self._after_zoom()

    def zoom_out(self):
        self.zoom = max(self.zoom - 1, 1)
        self._after_zoom()

    def _after_zoom(self):
        new_size = QSize(self.sprites_horiz * Block.WIDTH * self.zoom, self.sprites_vert * Block.HEIGHT * self.zoom)

        self.setFixedSize(new_size)

    def mouseReleaseEvent(self, event: QMouseEvent):
        released_button = event.button()

        if released_button == Qt.LeftButton:
            self.on_left_mouse_button_up(event)
        elif released_button == Qt.RightButton:
            pass  # self.on_right_mouse_button_up(event)

    def on_left_mouse_button_up(self, event: QMouseEvent):
        x, y = event.pos().toTuple()

        column = x // self.block_length
        row = y // self.block_length

        self.selected = column + (row * 0x10)
        self.pattern_display.selected(self.selected)
        self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        x, y = event.pos().toTuple()

        block_length = Block.WIDTH * self.zoom

        column = x // block_length
        row = y // block_length

        dec_index = row * self.sprites_horiz + column
        hex_index = hex(dec_index).upper().replace("X", "x")

        status_message = f"Row: {row}, Column: {column}, Index: {dec_index} / {hex_index}"

        self.pattern_display.status_bar.showMessage(status_message)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)

        bg_color = bg_color_for_object_set(self.object_set, 0)
        painter.setBrush(QBrush(bg_color))

        painter.drawRect(QRect(QPoint(0, 0), self.size()))

        graphics_set = PatternTableHandler(self.object_set)
        palette = load_palette(self.object_set, 0)
        transparent = get_setting("block_transparency", True)

        horizontal = self.sprites_horiz

        block_length = Block.WIDTH * self.zoom

        for i in range(self.sprites):
            tile = Tile.from_rom(i, palette, 0, graphics_set)

            x = (i % horizontal) * block_length
            y = (i // horizontal) * block_length

            tile.draw(painter, x, y, block_length, transparent=transparent)
