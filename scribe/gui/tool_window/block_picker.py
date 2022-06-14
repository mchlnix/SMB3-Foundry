from PySide6.QtCore import QSize, Signal, SignalInstance
from PySide6.QtGui import QMouseEvent, QPaintEvent, QPainter, Qt
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QVBoxLayout, QWidget

from foundry.game.File import ROM
from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx.Palette import load_palette_group
from foundry.game.gfx.drawable.Block import Block
from foundry.gui.BlockViewer import BlockBank
from smb3parse.objects.object_set import WORLD_MAP_OBJECT_SET


class BlockIcon(QWidget):
    clicked: SignalInstance = Signal(int)

    def __init__(self, block_id=0, zoom_level=2):
        super(BlockIcon, self).__init__()

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.block_id = block_id

        self.block = Block(
            block_id,
            load_palette_group(WORLD_MAP_OBJECT_SET, 0),
            GraphicsSet(0),
            ROM.get_tsa_data(WORLD_MAP_OBJECT_SET),
        )

        self.zoom_level = zoom_level

    def set_block_id(self, block_id) -> int:
        old_block_id = self.block_id
        self.block_id = block_id

        self.block = Block(
            block_id,
            load_palette_group(WORLD_MAP_OBJECT_SET, 0),
            GraphicsSet(0),
            ROM.get_tsa_data(WORLD_MAP_OBJECT_SET),
        )

        self.update()

        return old_block_id

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.block_id)

    def sizeHint(self) -> QSize:
        return QSize(Block.WIDTH, Block.HEIGHT) * self.zoom_level

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)

        self.block.draw(painter, 0, 0, Block.WIDTH * self.zoom_level)

        return super(BlockIcon, self).paintEvent(event)


class BlockList(QWidget):
    block_was_picked: SignalInstance = Signal(int)

    def __init__(self):
        super(BlockList, self).__init__()

        self.setLayout(QHBoxLayout())

        self.current_block = BlockIcon(0, zoom_level=4)
        self.recent_blocks = [BlockIcon(255) for _ in range(9)]

        self.layout().addWidget(self.current_block)
        self.layout().addSpacing(10)

        for block_icon in self.recent_blocks:
            block_icon.clicked.connect(self.set_current_block)
            self.layout().addWidget(block_icon)

    def set_current_block(self, new_block_id):
        if self.current_block.block_id == new_block_id:
            return

        last_block_id = self.current_block.block_id

        self.current_block.set_block_id(new_block_id)

        for block_icon in self.recent_blocks:
            if block_icon.block_id == last_block_id:
                break

            last_block_id = block_icon.set_block_id(last_block_id)

            if last_block_id == new_block_id:
                break

        self.block_was_picked.emit(new_block_id)


class BlockPicker(QWidget):
    def __init__(self):
        super(BlockPicker, self).__init__()

        self.setLayout(QVBoxLayout())

        self.block_bank = BlockBank(self)
        self.block_list = BlockList()

        self.block_bank.clicked.connect(self.block_list.set_current_block)

        self.layout().addWidget(self.block_bank)
        self.layout().addWidget(self.block_list)

    def set_zoom(self, zoom_level):
        self.block_bank.zoom = zoom_level
