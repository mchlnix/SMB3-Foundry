from PySide6.QtCore import QPointF, QTimer
from PySide6.QtGui import QMouseEvent, QPainter
from PySide6.QtWidgets import QWidget

from foundry.game.File import ROM
from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx.Palette import load_palette_group
from foundry.game.gfx.drawable.Block import Block, get_block, get_tile
from smb3parse.levels import LEVEL_SCREEN_WIDTH
from smb3parse.util.parser.level import ParsedLevel

width = LEVEL_SCREEN_WIDTH * 15
height = 27


class Canvas(QWidget):
    def __init__(self, level: ParsedLevel):
        super(Canvas, self).__init__()

        self.level = level

        self.timer = QTimer()
        self.timer.setInterval(120)
        self.timer.timeout.connect(self.anim_timer)  # type: ignore

        self.timer.start()

        self.palette_group = load_palette_group(level.object_set_num, level.object_palette_num)
        self.gfx_set = GraphicsSet.from_number(level.graphics_set_num)
        self.tsa_data = ROM.get_tsa_data(level.object_set_num)

        self.setFixedSize(width * Block.SIDE_LENGTH, height * Block.SIDE_LENGTH)

        self.show()

    def anim_timer(self):
        self.gfx_set.anim_frame += 1
        self.gfx_set.anim_frame %= 4
        get_tile.cache_clear()

        self.repaint()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)

        for i, block_index in enumerate(self.level.screen_memory):
            screen = i // (LEVEL_SCREEN_WIDTH * 27)

            x = (i % LEVEL_SCREEN_WIDTH) + screen * LEVEL_SCREEN_WIDTH
            y = (i // LEVEL_SCREEN_WIDTH) % height

            block = get_block(block_index, self.palette_group, self.gfx_set, self.tsa_data)

            block.draw(painter, x * Block.SIDE_LENGTH, y * Block.SIDE_LENGTH, Block.SIDE_LENGTH)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self._find_object_at_pos(event.position().toPoint())

    def _find_object_at_pos(self, pos: QPoint):
        x = (pos.x() // Block.SIDE_LENGTH) % LEVEL_SCREEN_WIDTH
        y = pos.y() // Block.SIDE_LENGTH
        screen = pos.x() // LEVEL_SCREEN_WIDTH // Block.SIDE_LENGTH

        index = screen * LEVEL_SCREEN_WIDTH * 27
        index += y * LEVEL_SCREEN_WIDTH
        index += x

        for level_object in reversed(self.level.parsed_objects):
            for pos_in_mem, tile_id in level_object.tiles_in_level:
                if pos_in_mem == index:
                    print("Hit", str(level_object))
                    return
