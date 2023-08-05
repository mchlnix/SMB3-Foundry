from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QColor, QPaintEvent, QPainter
from PySide6.QtWidgets import QWidget

from foundry.game.level.LevelRef import LevelRef


class SizeBar(QWidget):
    DEFAULT_SIZE = QSize(10, 10)

    def __init__(self, level_ref: LevelRef):
        super(SizeBar, self).__init__()

        self.level = level_ref

        self.original_value: float = 1.0
        self.current_value: float = 1.0
        self.value_color = QColor.black

    def sizeHint(self) -> QSize:
        size = super(SizeBar, self).sizeHint()

        size.setHeight(self.DEFAULT_SIZE.height())

        return size

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)

        painter.fillRect(event.rect(), self.palette().base())

        if self.level.level is None:
            return

        total_length = max(self.current_value, self.original_value, 1)

        pixels_per_byte = event.rect().width() / total_length

        bar = QRect(event.rect())
        bar.setWidth(int(pixels_per_byte * self.current_value))

        if self.current_value > self.original_value:
            painter.fillRect(bar, Qt.red)
        else:
            painter.fillRect(bar, self.value_color)
