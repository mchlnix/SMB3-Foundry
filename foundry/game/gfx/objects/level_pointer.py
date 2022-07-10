from PySide6.QtCore import QPoint, QRect, QSize
from PySide6.QtGui import QColor, QPainter, QPen

from foundry.game.gfx.objects.LevelObject import SCREEN_WIDTH
from foundry.game.gfx.objects.ObjectLike import ObjectLike
from smb3parse.data_points import LevelPointerData


class LevelPointer(ObjectLike):
    def __init__(self, level_pointer_data: LevelPointerData):
        self.data = level_pointer_data

    def render(self):
        pass

    def draw(self, painter: QPainter, block_length, transparent, selected=False):
        pos = QPoint(*self.data.pos.xy) * block_length

        rect = QRect(pos, QSize(block_length, block_length))

        if selected:
            painter.fillRect(rect, QColor(0x00, 0xFF, 0x00, 0x80))

        painter.setPen(QPen(QColor(0xFF, 0x00, 0x00, 0x80), 4))

        painter.drawRect(rect)

    def get_status_info(self):
        pass

    def set_position(self, x, y):
        self.data.screen = x // SCREEN_WIDTH
        self.data.x = x % SCREEN_WIDTH
        self.data.y = y

    def move_by(self, dx, dy):
        x, y = self.get_position()
        new_x = x + dx
        new_y = y + dy

        self.set_position(new_x, new_y)

    def get_position(self) -> tuple[int, int]:
        return self.data.screen * SCREEN_WIDTH + self.data.x, self.data.y

    def resize_by(self, dx, dy):
        pass

    def point_in(self, x, y):
        return x, y == self.get_position()

    def change_type(self, new_type):
        pass

    def __contains__(self, point):
        pass

    def to_bytes(self):
        pass

    def __lt__(self, other):
        if isinstance(other, LevelPointer):
            other = other.data

        return self.data < other
