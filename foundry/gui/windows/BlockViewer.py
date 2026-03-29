from math import ceil

from PySide6.QtCore import QPoint, QRect, QSize, QTimer, Signal, SignalInstance
from PySide6.QtGui import QMouseEvent, QPainter, QPaintEvent, QPen, QResizeEvent, Qt
from PySide6.QtWidgets import QComboBox, QLabel, QLayout, QStatusBar, QToolBar, QWidget

from foundry import icon
from foundry.game.gfx import BlockCache
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.GraphicsSet import GRAPHIC_SET_NAMES
from foundry.game.gfx.Palette import PALETTE_GROUPS_PER_OBJECT_SET
from foundry.gui import OBJECT_SET_ITEMS
from foundry.gui.widgets.Spinner import Spinner
from foundry.gui.windows.CustomChildWindow import CustomChildWindow
from smb3parse.constants import TILE_NAMES, UNDERGROUND_OBJECT_SET, WORLD_MAP_OBJECT_SET


class BlockViewer(CustomChildWindow):
    def __init__(self, parent):
        super(BlockViewer, self).__init__(parent, "Block Viewer")

        self._object_set = 0
        self._graphics_set_number = 0
        self.block_bank = BlockBank(parent=self)

        self.setCentralWidget(self.block_bank)

        self.object_set_toolbar = QToolBar(self)

        self.prev_os_action = self.object_set_toolbar.addAction(icon("arrow-left.svg"), "Previous object set")
        self.prev_os_action.triggered.connect(self.prev_object_set)

        self.next_os_action = self.object_set_toolbar.addAction(icon("arrow-right.svg"), "Next object set")
        self.next_os_action.triggered.connect(self.next_object_set)

        self.zoom_out_action = self.object_set_toolbar.addAction(icon("zoom-out.svg"), "Zoom Out")
        self.zoom_out_action.triggered.connect(self.block_bank.zoom_out)

        self.zoom_in_action = self.object_set_toolbar.addAction(icon("zoom-in.svg"), "Zoom In")
        self.zoom_in_action.triggered.connect(self.block_bank.zoom_in)

        self.object_set_dropdown = QComboBox(parent=self.object_set_toolbar)
        self.object_set_dropdown.addItems(OBJECT_SET_ITEMS[WORLD_MAP_OBJECT_SET : UNDERGROUND_OBJECT_SET + 1])
        self.object_set_dropdown.setCurrentIndex(0)

        self.object_set_dropdown.currentIndexChanged.connect(self.set_object_set)

        self.graphics_set_dropdown = QComboBox(parent=self.object_set_toolbar)
        self.graphics_set_dropdown.addItems(GRAPHIC_SET_NAMES)
        self.graphics_set_dropdown.setCurrentIndex(0)

        self.graphics_set_dropdown.currentIndexChanged.connect(self.set_graphics_set)

        self.palette_group_spinner = Spinner(self, maximum=PALETTE_GROUPS_PER_OBJECT_SET - 1, base=10)
        self.palette_group_spinner.valueChanged.connect(self.on_palette)

        self.object_set_toolbar.addWidget(self.object_set_dropdown)
        self.object_set_toolbar.addWidget(self.graphics_set_dropdown)

        self.object_set_toolbar.addWidget(QLabel(" Palette: "))
        self.object_set_toolbar.addWidget(self.palette_group_spinner)

        self.addToolBar(self.object_set_toolbar)

        self.layout().setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        self.setStatusBar(QStatusBar(self))
        self.block_bank.status_message_changed.connect(self.statusBar().showMessage)

    @property
    def object_set(self):
        return self._object_set

    @object_set.setter
    def object_set(self, value):
        self._object_set = value
        self.object_set_dropdown.setCurrentIndex(self.object_set)
        self.graphics_set_number = value

        self._after_object_set()

    def set_object_set(self, object_set: int):
        self.object_set = object_set

    @property
    def graphics_set_number(self):
        return self._graphics_set_number

    @graphics_set_number.setter
    def graphics_set_number(self, value):
        self._graphics_set_number = value
        self.graphics_set_dropdown.setCurrentIndex(self.graphics_set_number)

        self._after_object_set()

    def set_graphics_set(self, graphics_set: int):
        self.graphics_set_number = graphics_set

    @property
    def palette_group(self):
        return self.palette_group_spinner.value()

    @palette_group.setter
    def palette_group(self, value):
        self.palette_group_spinner.setValue(value)

    def prev_object_set(self):
        self.object_set = max(self.object_set - 1, WORLD_MAP_OBJECT_SET)

    def next_object_set(self):
        self.object_set = min(self.object_set + 1, UNDERGROUND_OBJECT_SET)

    def _after_object_set(self):
        self.block_bank.object_set = self.object_set
        self.block_bank.palette_group_index = self.palette_group
        self.block_bank.graphics_set = self.graphics_set_number

        self.block_bank.update()

    def on_palette(self, value):
        self.block_bank.palette_group_index = value
        self.block_bank.update()


class BlockBank(QWidget):
    status_message_changed: SignalInstance = Signal(str)
    clicked: SignalInstance = Signal(int)

    def __init__(self, parent, object_set=0, palette_group_index=0, zoom=2):
        super(BlockBank, self).__init__(parent)
        self.setMouseTracking(True)

        self.sprites = 255  # 0xFF is the delimiter
        self.zoom_step = 256
        self.sprites_horiz = 16
        self.sprites_vert = ceil(self.sprites / self.sprites_horiz)

        self.object_set = object_set
        self.palette_group_index = palette_group_index
        self.graphics_set = 0
        self.zoom = zoom

        self._size = QSize(
            self.sprites_horiz * Block.WIDTH * self.zoom,
            self.sprites_vert * Block.HEIGHT * self.zoom,
        )

        self.last_clicked_index = 0x00

        self.setFixedSize(self._size)

        self.draw_timer = QTimer(self)
        self.draw_timer.timeout.connect(self.repaint)
        self.draw_timer.setInterval(100)

        self.draw_timer.start()

    def resizeEvent(self, event: QResizeEvent):
        self.update()

    def zoom_in(self):
        self.zoom += 1
        self._after_zoom()

    def zoom_out(self):
        self.zoom = max(self.zoom - 1, 1)
        self._after_zoom()

    def _after_zoom(self):
        new_size = QSize(
            self.sprites_horiz * Block.WIDTH * self.zoom,
            self.sprites_vert * Block.HEIGHT * self.zoom,
        )

        self.setFixedSize(new_size)

    def mouseMoveEvent(self, event: QMouseEvent):
        x, y = event.position().toPoint().toTuple()

        block_length = Block.WIDTH * self.zoom

        column = x // block_length
        row = y // block_length

        dec_index = row * self.sprites_horiz + column
        hex_index = hex(dec_index).upper().replace("X", "x")

        if self.object_set == WORLD_MAP_OBJECT_SET:
            tile_name = " – " + TILE_NAMES[dec_index]
        else:
            tile_name = ""

        status_message = f"{dec_index} / {hex_index} @ ({column}, {row}){tile_name}"

        self.status_message_changed.emit(status_message)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        x, y = event.position().toPoint().toTuple()

        block_length = Block.WIDTH * self.zoom

        column = x // block_length
        row = y // block_length

        dec_index = row * self.sprites_horiz + column

        if dec_index < 0xFF:
            self.last_clicked_index = dec_index
            self.clicked.emit(dec_index)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)

        painter.drawRect(QRect(QPoint(0, 0), self.size()))

        horizontal = self.sprites_horiz

        block_length = Block.WIDTH * self.zoom

        for block_index in range(self.sprites):
            block = BlockCache.block(
                block_index,
                self.object_set,
                self.palette_group_index,
                self.graphics_set,
            )

            x = (block_index % horizontal) * block_length
            y = (block_index // horizontal) * block_length

            block.draw(painter, x, y, block_length)

        painter.setPen(QPen(Qt.GlobalColor.gray, 1))

        # rows
        for y in range(16):
            y *= block_length

            painter.drawLine(QPoint(0, y), QPoint(16 * block_length, y))

        # columns
        for x in range(16):
            x *= block_length

            painter.drawLine(QPoint(x, 0), QPoint(x, 16 * block_length))
