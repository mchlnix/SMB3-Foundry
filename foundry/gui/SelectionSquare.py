from PySide6.QtCore import QRect, QPoint
from PySide6.QtGui import QPen, Qt, QColor, QPainter

STROKE_COLOR = QColor(0x00, 0x00, 0x00, 0x80)


class SelectionSquare:
    def __init__(self):
        self.start_point = QPoint(0, 0)
        self.end_point = QPoint(0, 0)

        self.active = False
        self.should_draw = False

        self.rect = QRect(self.start_point, self.end_point)

        self.pen = QPen(STROKE_COLOR, 1)
        self.brush = Qt.NoBrush

    def is_active(self):
        return self.active

    def start(self, point: QPoint):
        self.active = True

        self.start_point = point

    def set_current_end(self, point: QPoint):
        if not self.active:
            return

        self.should_draw = True

        self.end_point = point

        self.rect = QRect(self.start_point, self.end_point)

    def stop(self):
        self.active = False
        self.should_draw = False

    def get_rect(self):
        return self.rect

    def get_adjusted_rect(self, horizontal_factor: int, vertical_factor: int) -> QRect:
        x, y = self.get_rect().topLeft().toTuple()
        width, height = self.get_rect().size().toTuple()

        x //= horizontal_factor
        width //= horizontal_factor

        y //= vertical_factor
        height //= vertical_factor

        return QRect(x, y, width + 1, height + 1)

    def draw(self, painter: QPainter):
        if self.should_draw:
            painter.setPen(self.pen)
            painter.setBrush(self.brush)

            painter.drawRect(self.rect)
