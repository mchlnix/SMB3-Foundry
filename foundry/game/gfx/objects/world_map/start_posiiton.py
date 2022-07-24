from PySide6.QtCore import QPoint
from PySide6.QtGui import QPainter

from foundry.game.gfx.drawable import load_from_png
from foundry.game.gfx.objects.world_map.map_object import MapObject
from smb3parse.data_points import Position

mario_png = load_from_png(59, 53)


class StartPosition(MapObject):
    def __init__(self, start_pos: Position):
        super(StartPosition, self).__init__()

        self.pos = start_pos

    def set_position(self, x, y):
        self.pos.y = y

    def get_position(self):
        return self.pos.xy

    def draw(self, painter: QPainter, block_length, transparent):
        x, y = self.get_position()

        x *= block_length
        y *= block_length

        painter.drawImage(QPoint(x, y), mario_png.scaled(block_length, block_length))

    def change_type(self, new_type):
        pass
