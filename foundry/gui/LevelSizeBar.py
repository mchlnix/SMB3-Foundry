from PySide2.QtCore import QRect, QSize, Qt
from PySide2.QtGui import QColor, QPaintEvent, QPainter
from PySide2.QtWidgets import QSizePolicy, QWidget

from foundry.game.level.Level import Level


class LevelSizeBar(QWidget):
    DEFAULT_SIZE = QSize(10, 10)

    def __init__(self, parent, level):
        super(LevelSizeBar, self).__init__(parent)

        self.level: Level = level

        self.level.data_changed.connect(self.update)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

    def sizeHint(self) -> QSize:
        size = super(LevelSizeBar, self).sizeHint()

        size.setHeight(self.DEFAULT_SIZE.height())

        return size

    def update(self):
        self.setToolTip(f"{self.value_description}: {self.current_value}/{self.original_value} Bytes")

        return super(LevelSizeBar, self).update()

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)

        painter.fillRect(event.rect(), self.palette().base())

        if self.level is None:
            return

        total_length = max(self.current_value, self.original_value)

        pixels_per_byte = event.rect().width() / total_length

        bar = QRect(event.rect())
        bar.setWidth(pixels_per_byte * self.current_value)

        if self.current_value > self.original_value:
            painter.fillRect(bar, Qt.red)
        else:
            painter.fillRect(bar, self.value_color)

    @property
    def value_color(self):
        return QColor.fromRgb(0x58D858)

    @property
    def value_description(self):
        return "Objects"

    @property
    def original_value(self):
        return self.level.object_size_on_disk

    @property
    def current_value(self):
        return self.level.current_object_size()
