from math import ceil

from PySide2.QtCore import QSize, QRect, QPoint, QObject
from PySide2.QtGui import Qt, QKeyEvent, QCloseEvent, QPaintEvent, QPainter, QColor, QBrush, QResizeEvent
from PySide2.QtWidgets import QStyle, QComboBox, QMainWindow, QToolBar, QWidget, QLayout

from game.File import ROM
from game.gfx.Palette import get_bg_color_for, load_palette
from game.gfx.PatternTable import PatternTable
from game.gfx.drawable.Block import Block
from gui.LevelSelector import OBJECT_SET_ITEMS

ID_ZOOM_IN = 10001
ID_ZOOM_OUT = 10002
ID_PREV_BANK = 10003
ID_NEXT_BANK = 10004
ID_BANK_DROPDOWN = 10005


class BlockViewer(QMainWindow):
    def __init__(self, parent):
        super(BlockViewer, self).__init__(parent)
        self.setWindowTitle("Block Viewer")

        self.object_set = 0
        self.sprite_bank = BlockBank(parent=self, object_set=self.object_set)

        self.setCentralWidget(self.sprite_bank)

        self._toolbar = QToolBar(self)

        self._toolbar.addAction(self.style().standardIcon(QStyle.SP_ArrowLeft), "Previous object set")
        self._toolbar.addAction(self.style().standardIcon(QStyle.SP_ArrowRight), "Next object set")

        assert isinstance(self.sprite_bank, QObject)

        zoom_out_action = self._toolbar.addAction("-")
        zoom_out_action.triggered.connect(self.sprite_bank.zoom_out)

        zoom_in_action = self._toolbar.addAction("+")
        zoom_in_action.triggered.connect(self.sprite_bank.zoom_in)

        self.bank_dropdown = QComboBox(parent=self._toolbar)
        self.bank_dropdown.addItems(OBJECT_SET_ITEMS)
        self.bank_dropdown.setCurrentIndex(0)

        self._toolbar.addWidget(self.bank_dropdown)

        self.addToolBar(self._toolbar)

        self.layout().setSizeConstraint(QLayout.SetFixedSize)

        return

        self.Bind(wx.EVT_COMBOBOX, self.on_combo)
        self.Bind(wx.EVT_CLOSE, self.on_exit)
        self.Bind(wx.EVT_SIZE, self.on_resize)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_press)

        self.SetStatusBar(wx.StatusBar(self))
        self.GetStatusBar().SetFieldsCount(3)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.hide()

    def on_combo(self, _):
        self.object_set = self.bank_dropdown.GetSelection()

        self.sprite_bank.object_set = self.object_set

        self.sprite_bank.Refresh()

    def closeEvent(self, event: QCloseEvent):
        self.hide()


class BlockBank(QWidget):
    def __init__(self, parent, object_set=0, zoom=2):
        self.sprites = 256
        self.sprites_horiz = 16
        self.sprites_vert = ceil(self.sprites / self.sprites_horiz)

        self.object_set = object_set
        self.zoom = zoom

        self._size = QSize(self.sprites_horiz * Block.WIDTH * self.zoom, self.sprites_vert * Block.HEIGHT * self.zoom)

        super(BlockBank, self).__init__(parent)

        self.setFixedSize(self._size)

        return

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_MOTION, self.on_mouse_motion)

        self.SetSize(self._size)

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

    def on_mouse_motion(self, event):
        x, y = event.GetPosition().Get()

        block_length = Block.WIDTH * self.zoom

        column = x // block_length
        row = y // block_length

        dec_index = row * self.sprites_horiz + column
        hex_index = hex(dec_index).upper().replace("X", "x")

        self.GetParent().SetStatusText(f"Row: {row}", 0)
        self.GetParent().SetStatusText(f"Column: {column}", 1)
        self.GetParent().SetStatusText(f"Index: {dec_index} / {hex_index}", 2)

        event.Skip()

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
