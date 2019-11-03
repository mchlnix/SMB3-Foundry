from math import ceil

from PySide2.QtCore import QSize, QRect, QPoint, QObject
from PySide2.QtGui import Qt, QKeyEvent, QCloseEvent, QPaintEvent, QPainter, QColor, QBrush, QResizeEvent, QMouseEvent
from PySide2.QtWidgets import QStyle, QComboBox, QMainWindow, QToolBar, QWidget, QLayout, QStatusBar

from game.File import ROM
from game.gfx.Palette import get_bg_color_for, load_palette
from game.gfx.PatternTable import PatternTable
from game.gfx.drawable.Block import Block
from gui.LevelSelector import OBJECT_SET_ITEMS


class BlockViewer(QMainWindow):
    def __init__(self, parent):
        super(BlockViewer, self).__init__(parent)
        self.setWindowTitle("Block Viewer")

        self.object_set = 0
        self.sprite_bank = BlockBank(parent=self, object_set=self.object_set)

        self.setCentralWidget(self.sprite_bank)

        self._toolbar = QToolBar(self)

        prev_os_action = self._toolbar.addAction(self.style().standardIcon(QStyle.SP_ArrowLeft), "Previous object set")
        prev_os_action.triggered.connect(self.prev_object_set)
        next_os_action = self._toolbar.addAction(self.style().standardIcon(QStyle.SP_ArrowRight), "Next object set")
        next_os_action.triggered.connect(self.next_object_set)

        assert isinstance(self.sprite_bank, QObject)

        zoom_out_action = self._toolbar.addAction("-")
        zoom_out_action.triggered.connect(self.sprite_bank.zoom_out)

        zoom_in_action = self._toolbar.addAction("+")
        zoom_in_action.triggered.connect(self.sprite_bank.zoom_in)

        self.bank_dropdown = QComboBox(parent=self._toolbar)
        self.bank_dropdown.addItems(OBJECT_SET_ITEMS)
        self.bank_dropdown.setCurrentIndex(0)

        self.bank_dropdown.currentIndexChanged.connect(self.on_combo)

        self._toolbar.addWidget(self.bank_dropdown)

        self.addToolBar(self._toolbar)

        self.layout().setSizeConstraint(QLayout.SetFixedSize)

        self.setStatusBar(QStatusBar(self))

        return

    def prev_object_set(self):
        self.object_set = max(self.object_set - 1, 0)

        self._after_object_set()

    def next_object_set(self):
        self.object_set = min(self.object_set + 1, 0xE)

        self._after_object_set()

    def _after_object_set(self):
        self.sprite_bank.object_set = self.object_set

        self.bank_dropdown.setCurrentIndex(self.object_set)

        self.sprite_bank.update()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.hide()

    def on_combo(self, _):
        self.object_set = self.bank_dropdown.currentIndex()

        self.sprite_bank.object_set = self.object_set

        self.sprite_bank.update()

    def closeEvent(self, event: QCloseEvent):
        self.hide()


class BlockBank(QWidget):
    def __init__(self, parent, object_set=0, zoom=2):
        super(BlockBank, self).__init__(parent)
        self.setMouseTracking(True)

        self.sprites = 256
        self.sprites_horiz = 16
        self.sprites_vert = ceil(self.sprites / self.sprites_horiz)

        self.object_set = object_set
        self.zoom = zoom

        self._size = QSize(self.sprites_horiz * Block.WIDTH * self.zoom, self.sprites_vert * Block.HEIGHT * self.zoom)

        self.setFixedSize(self._size)

        return

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

        self.parent().statusBar().showMessage(status_message)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)

        bg_color = QColor(*get_bg_color_for(self.object_set, 0))
        painter.setBrush(QBrush(bg_color))

        painter.drawRect(QRect(QPoint(0, 0), self.size()))

        pattern_table = PatternTable(self.object_set)
        palette = load_palette(self.object_set, 0)
        tsa_data = ROM.get_tsa_data(self.object_set)

        horizontal = self.sprites_horiz

        block_length = Block.WIDTH * self.zoom

        for i in range(self.sprites):
            block = Block(i, palette, pattern_table, tsa_data)

            x = (i % horizontal) * block_length
            y = (i // horizontal) * block_length

            block.draw(painter, x, y, block_length)

        return
