from math import ceil

from PySide6.QtCore import QPoint, QRect, QSize, QTimer, Signal, SignalInstance
from PySide6.QtGui import QMouseEvent, QPainter, QPaintEvent, QPen, QResizeEvent, Qt
from PySide6.QtWidgets import QComboBox, QLabel, QLayout, QStatusBar, QToolBar, QWidget

from foundry import icon
from foundry.game.File import ROM
from foundry.game.gfx.drawable.Block import Block, get_block
from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx.Palette import PALETTE_GROUPS_PER_OBJECT_SET, load_palette_group
from foundry.gui import OBJECT_SET_ITEMS
from foundry.gui.widgets.Spinner import Spinner
from foundry.gui.windows.CustomChildWindow import CustomChildWindow
from smb3parse.constants import TILE_NAMES
from smb3parse.objects.object_set import WORLD_MAP_OBJECT_SET


class BlockViewer(CustomChildWindow):
    def __init__(self, parent):
        super(BlockViewer, self).__init__(parent, _("Block Viewer"))

        self._object_set = 0
        self.block_bank = BlockBank(parent=self)

        self.setCentralWidget(self.block_bank)

        self.toolbar = QToolBar(self)

        # TRANSLATORS: Object set refers to a collection of objects
        self.prev_os_action = self.toolbar.addAction(icon("arrow-left.svg"), _("Previous object set"))
        self.prev_os_action.triggered.connect(self.prev_object_set)

        # TRANSLATORS: Object set refers to a collection of objects
        self.next_os_action = self.toolbar.addAction(icon("arrow-right.svg"), _("Next object set"))
        self.next_os_action.triggered.connect(self.next_object_set)

        self.zoom_out_action = self.toolbar.addAction(icon("zoom-out.svg"), _("Zoom Out"))
        self.zoom_out_action.triggered.connect(self.block_bank.zoom_out)

        self.zoom_in_action = self.toolbar.addAction(icon("zoom-in.svg"), _("Zoom In"))
        self.zoom_in_action.triggered.connect(self.block_bank.zoom_in)

        self.bank_dropdown = QComboBox(parent=self.toolbar)
        self.bank_dropdown.addItems(OBJECT_SET_ITEMS)
        self.bank_dropdown.setCurrentIndex(0)

        self.bank_dropdown.currentIndexChanged.connect(self.on_combo)

        self.palette_group_spinner = Spinner(self, maximum=PALETTE_GROUPS_PER_OBJECT_SET - 1, base=10)
        self.palette_group_spinner.valueChanged.connect(self.on_palette)

        self.toolbar.addWidget(self.bank_dropdown)
        # TRANSLATORS: Keep spaces for padding
        self.toolbar.addWidget(QLabel(_(" Object Palette: ")))
        self.toolbar.addWidget(self.palette_group_spinner)

        self.addToolBar(self.toolbar)

        self.layout().setSizeConstraint(QLayout.SetFixedSize)

        self.setStatusBar(QStatusBar(self))
        self.block_bank.status_message_changed.connect(self.statusBar().showMessage)

    @property
    def object_set(self):
        return self._object_set

    @object_set.setter
    def object_set(self, value):
        self._object_set = value

        self._after_object_set()

    @property
    def palette_group(self):
        return self.palette_group_spinner.value()

    @palette_group.setter
    def palette_group(self, value):
        self.palette_group_spinner.setValue(value)

    def prev_object_set(self):
        self.object_set = max(self.object_set - 1, 0)

    def next_object_set(self):
        self.object_set = min(self.object_set + 1, 0xE)

    def _after_object_set(self):
        self.block_bank.object_set = self.object_set

        self.bank_dropdown.setCurrentIndex(self.object_set)

        self.block_bank.update()

    def on_combo(self, _):
        self.object_set = self.bank_dropdown.currentIndex()

        self.block_bank.object_set = self.object_set

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

        status_message = f"{hex_index} @ ({column}, {row}){tile_name}"

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

        graphics_set = GraphicsSet.from_number(self.object_set)

        palette = load_palette_group(self.object_set, self.palette_group_index)
        tsa_data = ROM.get_tsa_data(self.object_set)

        horizontal = self.sprites_horiz

        block_length = Block.WIDTH * self.zoom

        for i in range(self.sprites):
            block = get_block(i, palette, graphics_set, tsa_data)

            x = (i % horizontal) * block_length
            y = (i // horizontal) * block_length

            block.draw(painter, x, y, block_length)

        painter.setPen(QPen(Qt.gray, 1))

        # rows
        for y in range(16):
            y *= block_length

            painter.drawLine(QPoint(0, y), QPoint(16 * block_length, y))

        # columns
        for x in range(16):
            x *= block_length

            painter.drawLine(QPoint(x, 0), QPoint(x, 16 * block_length))
