from itertools import product
from typing import Optional

from PySide2.QtCore import QSize
from PySide2.QtGui import QColor, QPaintEvent, QPainter, Qt
from PySide2.QtWidgets import QHBoxLayout, QSizePolicy, QWidget

from foundry.game.gfx.Palette import bg_color_for_palette
from foundry.game.gfx.objects.LevelObject import LevelObject, get_minimal_icon
from foundry.game.gfx.objects.LevelObjectFactory import LevelObjectFactory
from smb3parse.objects import MAX_DOMAIN, MAX_ID_VALUE
from smb3parse.objects.object_set import PLAINS_GRAPHICS_SET, PLAINS_OBJECT_SET


class ObjectToolBox(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super(ObjectToolBox, self).__init__(parent)

        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

    def _fill_tool_box(self):
        object_ids = list(range(0x00, 0x10)) + list(range(0x10, MAX_ID_VALUE, 0x10))

        for domain, obj_index in product(range(MAX_DOMAIN + 1), object_ids):
            level_object = self.factory.from_properties(
                domain=domain, object_index=obj_index, x=0, y=0, length=None, index=0
            )

            if not isinstance(level_object, LevelObject) or level_object.description in ["MSG_NOTHING", "MSG_CRASH"]:
                continue

            icon = ObjectIcon(level_object)

            self._layout.addWidget(icon)

    def update(self):
        self.factory = LevelObjectFactory(
            PLAINS_OBJECT_SET, PLAINS_GRAPHICS_SET, 0, [], vertical_level=False, size_minimal=True
        )

        self._fill_tool_box()

    @property
    def draw_background_color(self):
        return self._layout.itemAt(0).draw_background_color

    @draw_background_color.setter
    def draw_background_color(self, value):
        for index in range(self._layout.count()):
            self._layout.itemAt(index).draw_background_color = value


class ObjectIcon(QWidget):
    MIN_SIZE = QSize(32, 32)
    MAX_SIZE = MIN_SIZE * 2

    def __init__(self, level_object: LevelObject):
        super(ObjectIcon, self).__init__()

        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        size_policy.setHeightForWidth(True)
        self.setSizePolicy(size_policy)

        self.setContentsMargins(0, 0, 0, 0)

        self.zoom = 1

        self.object = level_object

        self.image = get_minimal_icon(level_object)
        self.setToolTip(level_object.description)

        self.draw_background_color = False

    def heightForWidth(self, width: int) -> int:
        current_width, current_height = self.image.size().toTuple()

        height = current_height / current_width * width

        return height

    def sizeHint(self):
        if self.fits_inside(self.image.size() * 2, self.MAX_SIZE):
            return self.image.size() * 2
        else:
            return self.MAX_SIZE

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)

        if self.draw_background_color:
            painter.fillRect(event.rect(), QColor(*bg_color_for_palette(self.object.palette_group)))

        scaled_image = self.image.scaled(self.size(), aspectMode=Qt.KeepAspectRatio)

        x = (self.width() - scaled_image.width()) // 2
        y = (event.rect().height() - scaled_image.height()) // 2

        painter.drawImage(x, y, scaled_image)

        super(ObjectIcon, self).paintEvent(event)

    @staticmethod
    def fits_inside(size1: QSize, size2: QSize):
        return size1.width() <= size2.width() and size1.height() <= size2.height()
