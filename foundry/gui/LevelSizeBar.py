from PySide2.QtCore import QRect, QSize, Qt
from PySide2.QtGui import QPaintEvent, QPainter
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
        total_current_size = self.level.current_object_size() + self.level.current_enemies_size()
        total_original_size = self.level.size_on_disk

        self.setToolTip(
            f"Objects: {self.level.current_object_size()} Bytes, "
            f"Enemies/Items: {self.level.current_enemies_size()} Bytes, "
            f"Total: {total_current_size}/{total_original_size} Bytes"
        )

        return super(LevelSizeBar, self).update()

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)

        if self.level is None:
            painter.fillRect(event.rect(), self.palette().base())
            return

        original_length = self.level.object_size_on_disk + self.level.enemy_size_on_disk
        current_length = self.level.current_object_size() + self.level.current_enemies_size()

        if current_length > original_length:
            painter.fillRect(event.rect(), Qt.red)
            return

        elif current_length < original_length:
            # paint background of unused bytes
            painter.fillRect(event.rect(), self.palette().base())

        total_length = max(original_length, current_length)

        pixels_per_byte = event.rect().width() / total_length

        object_rect = QRect(event.rect())
        object_rect.setWidth(pixels_per_byte * self.level.current_object_size())

        enemy_rect = QRect(event.rect())
        enemy_rect.setLeft(enemy_rect.left() + object_rect.width())
        enemy_rect.setWidth(pixels_per_byte * self.level.current_enemies_size())

        painter.fillRect(object_rect, Qt.blue)
        painter.fillRect(enemy_rect, Qt.yellow)
