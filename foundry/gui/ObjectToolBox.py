from itertools import product
from typing import Optional, Union

from PySide2.QtCore import QSize
from PySide2.QtGui import QColor, QImage, QPaintEvent, QPainter, Qt
from PySide2.QtWidgets import QHBoxLayout, QSizePolicy, QWidget

from foundry.game.gfx.Palette import bg_color_for_palette
from foundry.game.gfx.objects.EnemyItemFactory import EnemyItemFactory
from foundry.game.gfx.objects.LevelObject import LevelObject, get_minimal_icon
from foundry.game.gfx.objects.LevelObjectFactory import LevelObjectFactory
from smb3parse.objects import MAX_DOMAIN, MAX_ENEMY_ITEM_ID, MAX_ID_VALUE
from smb3parse.objects.enemy_item import EnemyItem


class ObjectToolBox(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super(ObjectToolBox, self).__init__(parent)

        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.setContentsMargins(0, 10, 0, 15)

        self._layout = QHBoxLayout(self)

    def add_object(self, level_object: Union[EnemyItem, LevelObject]):
        icon = ObjectIcon(level_object)

        self._layout.addWidget(icon)

    def add_from_object_set(self, object_set_index: int, graphic_set_index: int = -1):
        if graphic_set_index == -1:
            graphic_set_index = object_set_index

        factory = LevelObjectFactory(
            object_set_index, graphic_set_index, 0, [], vertical_level=False, size_minimal=True
        )

        object_ids = list(range(0x00, 0x10)) + list(range(0x10, MAX_ID_VALUE, 0x10))

        for domain, obj_index in product(range(MAX_DOMAIN + 1), object_ids):
            level_object = factory.from_properties(
                domain=domain, object_index=obj_index, x=0, y=0, length=None, index=0
            )

            if not isinstance(level_object, LevelObject) or level_object.description in ["MSG_NOTHING", "MSG_CRASH"]:
                continue

            self.add_object(level_object)

    def add_from_enemy_set(self, object_set_index: int):
        factory = EnemyItemFactory(object_set_index, 0)

        for obj_index in range(MAX_ENEMY_ITEM_ID + 1):
            enemy_item = factory.from_properties(obj_index, x=0, y=0)

            if enemy_item.description in ["MSG_NOTHING", "MSG_CRASH"]:
                continue

            self.add_object(enemy_item)

    def clear(self):
        while item := self._layout.takeAt(0):
            if item is None:
                break
            else:
                item.widget().deleteLater()

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

    def __init__(self, level_object: Optional[LevelObject] = None):
        super(ObjectIcon, self).__init__()

        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.setSizePolicy(size_policy)

        self.zoom = 1

        self.object = None
        self.image = QImage()

        self.set_object(level_object)

        self.draw_background_color = True

    def set_object(self, level_object: Optional[LevelObject]):
        self.object = level_object

        if self.object is not None:
            self.image = get_minimal_icon(level_object)
            self.setToolTip(level_object.description)
        else:
            self.image = QImage()
            self.setToolTip("")

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
        if self.object is not None:
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
