from typing import Optional

from PySide6.QtCore import QSize
from PySide6.QtGui import QPaintEvent, QPainter
from PySide6.QtWidgets import QWidget

from foundry.game.level.WorldMap import WorldMap


class WorldMapView(QWidget):
    def __init__(self, parent: Optional[QWidget], world: WorldMap):
        super(WorldMapView, self).__init__(parent)

        self.world = world
        self.zoom = 2

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)

        self.world.draw(painter, self.zoom)

    def sizeHint(self) -> QSize:
        return self.world.q_size * self.zoom
