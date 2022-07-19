from itertools import product
from typing import Optional

from PySide6.QtCore import QMimeData, QSize, Qt, Signal, SignalInstance
from PySide6.QtGui import QDrag, QImage, QMouseEvent, QPaintEvent, QPainter
from PySide6.QtWidgets import QGridLayout, QSizePolicy, QWidget

from foundry.game.gfx.Palette import bg_color_for_palette_group
from foundry.game.gfx.objects import (
    EnemyItemFactory,
    LevelObject,
    LevelObjectFactory,
    get_minimal_icon_object,
)
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from smb3parse.objects import MAX_DOMAIN, MAX_ENEMY_ITEM_ID, MAX_ID_VALUE


class ObjectIcon(QWidget):
    MIN_SIZE = QSize(32, 32)
    MAX_SIZE = MIN_SIZE * 2

    clicked: SignalInstance = Signal()
    object_placed: SignalInstance = Signal()

    def __init__(self, level_object: Optional[InLevelObject] = None):
        super(ObjectIcon, self).__init__()

        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.setSizePolicy(size_policy)

        self.zoom = 1

        self.object: Optional[InLevelObject] = None
        self.image = QImage()

        self.set_object(level_object)

        self.draw_background_color = True

        self.max_size = self.MIN_SIZE

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return super(ObjectIcon, self).mouseMoveEvent(event)

        drag = QDrag(self)

        mime_data = QMimeData()

        object_bytes = bytearray()

        if isinstance(self.object, LevelObject):
            object_bytes.append(0)
        else:
            object_bytes.append(1)

        object_bytes.extend(self.object.to_bytes())

        mime_data.setData("application/level-object", object_bytes)

        drag.setMimeData(mime_data)

        if drag.exec() == Qt.MoveAction:
            self.object_placed.emit()

    def set_object(self, level_object: Optional[InLevelObject]):
        if level_object is not None:
            self.object = get_minimal_icon_object(level_object)

            if self.object:
                self.image = self.object.as_image()
                self.setToolTip(self.object.name)

                return

        self.image = QImage()
        self.setToolTip("")

        self.update()

    def heightForWidth(self, width: int) -> int:
        current_width, current_height = self.image.size().toTuple()

        height = current_height / current_width * width

        return height

    def sizeHint(self):
        if self.object is not None and self.fits_inside(self.image.size() * 2, self.max_size):
            return self.image.size() * 2
        else:
            return self.max_size

    def paintEvent(self, event: QPaintEvent):
        if self.object is not None:
            painter = QPainter(self)

            if self.draw_background_color:
                painter.fillRect(event.rect(), bg_color_for_palette_group(self.object.palette_group))

            scaled_image = self.image.scaled(self.size(), aspectMode=Qt.KeepAspectRatio)

            x = (self.width() - scaled_image.width()) // 2
            y = (self.height() - scaled_image.height()) // 2

            painter.drawImage(x, y, scaled_image)

        return super(ObjectIcon, self).paintEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.clicked.emit()

        return super(ObjectIcon, self).mouseReleaseEvent(event)

    @staticmethod
    def fits_inside(size1: QSize, size2: QSize):
        return size1.width() <= size2.width() and size1.height() <= size2.height()


class ObjectToolBox(QWidget):
    object_icon_clicked: SignalInstance = Signal(ObjectIcon)
    object_placed: SignalInstance = Signal(ObjectIcon)

    def __init__(self, parent: Optional[QWidget] = None):
        super(ObjectToolBox, self).__init__(parent)

        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        self._layout = QGridLayout(self)
        self._layout.setAlignment(Qt.AlignCenter)

        self._layout.setAlignment(Qt.AlignHCenter)

    def add_object(self, level_object: InLevelObject, index: int = -1):
        icon = ObjectIcon(level_object)

        icon.clicked.connect(self._on_icon_clicked)
        icon.object_placed.connect(lambda: self.object_placed.emit(icon))

        if index == -1:
            index = self._layout.count()

        self._layout.addWidget(icon, index // 2, index % 2)

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

            if not isinstance(level_object, LevelObject) or level_object.name in ["MSG_NOTHING", "MSG_CRASH"]:
                continue

            self.add_object(level_object)

    def add_from_enemy_set(self, object_set_index: int):
        factory = EnemyItemFactory(object_set_index, 0)

        for obj_index in range(MAX_ENEMY_ITEM_ID + 1):
            enemy_item = factory.from_properties(obj_index, x=0, y=0)

            if enemy_item.name in ["MSG_NOTHING", "MSG_CRASH"]:
                continue

            self.add_object(enemy_item)

    def clear(self):
        self._extract_objects()

    def _on_icon_clicked(self):
        self.object_icon_clicked.emit(self.sender())

    @property
    def draw_background_color(self):
        return self._layout.itemAt(0).draw_background_color

    @draw_background_color.setter
    def draw_background_color(self, value):
        for index in range(self._layout.count()):
            self._layout.itemAt(index).draw_background_color = value

    def has_object(self, level_object):
        return self.index_of_object(level_object) != -1

    def index_of_object(self, level_object):
        for index in range(self._layout.count()):
            if self._layout.itemAtPosition(index // 2, index % 2).widget().object == level_object:
                return index
        else:
            return -1

    def _extract_objects(self):
        objects = []

        while True:
            item = self._layout.takeAt(0)

            if item is None:
                break
            else:
                objects.append(item.widget().object)
                item.widget().deleteLater()

        return objects

    def place_at_front(self, level_object):
        objects = self._extract_objects()

        if level_object in objects:
            objects.remove(level_object)

        objects.insert(0, level_object)

        assert self._layout.count() == 0

        for obj in objects:
            self.add_object(obj)
