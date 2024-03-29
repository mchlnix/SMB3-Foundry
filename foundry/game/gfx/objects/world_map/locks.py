from PySide6.QtCore import QPoint, QRect, QSize
from PySide6.QtGui import QColor, QPainter

from foundry.game.gfx.drawable import load_from_png
from foundry.game.gfx.drawable.Block import get_worldmap_tile
from foundry.game.gfx.objects.world_map.map_object import MapObject
from smb3parse.data_points import FortressFXData, Position

KEY_IMG = load_from_png(63, 2)


class Lock(MapObject):
    def __init__(self, fortress_fx_data: FortressFXData):
        super(Lock, self).__init__()

        self.data = fortress_fx_data

        self.replacement_tile = get_worldmap_tile(self.data.replacement_block_index)

    def draw(self, painter: QPainter, block_length, transparent, selected=False):
        pos = QPoint(*self.data.pos.xy) * block_length

        rect = QRect(pos, QSize(block_length, block_length))

        painter.drawImage(rect.topLeft(), KEY_IMG.scaled(block_length, block_length))

        if selected:
            painter.fillRect(rect, QColor(0x00, 0xFF, 0x00, 0x80))

    def set_position(self, x, y):
        self.data.pos = Position.from_xy(x, y)

    def get_position(self) -> tuple[int, int]:
        return self.data.pos.xy

    def change_type(self, new_type):
        pass
