from PySide6.QtCore import QSize, Qt, Signal, SignalInstance
from PySide6.QtGui import QDrag, QImage, QMouseEvent, QPainter, QPaintEvent
from PySide6.QtWidgets import QSizePolicy, QWidget

from foundry.game.gfx import object_to_image
from foundry.game.gfx.drawable import load_from_object_sprite_sheet
from foundry.game.gfx.objects import get_minimal_icon_object
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from foundry.game.gfx.objects.in_level.jump import Jump
from foundry.game.gfx.objects.in_level.level_object import LevelObject
from foundry.game.gfx.Palette import bg_color_for_palette_group
from foundry.gui.visualization.MainView import object_to_mime_data

objects_to_use_pngs_instead = {
    "'?' with flower": load_from_object_sprite_sheet(0, 4),
    "'?' with leaf": load_from_object_sprite_sheet(1, 4),
    "'?' with star": load_from_object_sprite_sheet(2, 4),
    "'?' with continuous star": load_from_object_sprite_sheet(3, 4),
    "brick with flower": load_from_object_sprite_sheet(6, 4),
    "brick with leaf": load_from_object_sprite_sheet(7, 4),
    "brick with star": load_from_object_sprite_sheet(8, 4),
    "brick with continuous star": load_from_object_sprite_sheet(9, 4),
    "brick with multi-coin": load_from_object_sprite_sheet(10, 4),
    "brick with 1-up": load_from_object_sprite_sheet(11, 4),
    "brick with vine": load_from_object_sprite_sheet(12, 4),
    "brick with p-switch": load_from_object_sprite_sheet(13, 4),
    "invisible coin": load_from_object_sprite_sheet(14, 4),
    "invisible 1-up": load_from_object_sprite_sheet(15, 4),
    "bricks with single coins": load_from_object_sprite_sheet(18, 4),
    "note block with flower": load_from_object_sprite_sheet(35, 5),
    "note block with leaf": load_from_object_sprite_sheet(36, 5),
    "note block with star": load_from_object_sprite_sheet(37, 5),
    "wooden block with flower": load_from_object_sprite_sheet(38, 5),
    "wooden block with leaf": load_from_object_sprite_sheet(39, 5),
    "wooden block with star": load_from_object_sprite_sheet(40, 5),
    "silver coins (appear when you hit a p-switch)": load_from_object_sprite_sheet(53, 5),
}


class ObjectIcon(QWidget):
    """Icon showing a minimized version of a Level Object or Enemy. Can be dragged from to get the item data."""

    MIN_SIZE = QSize(32, 32)
    MAX_SIZE = MIN_SIZE * 2

    clicked: SignalInstance = Signal()

    def __init__(self, level_object: InLevelObject | None = None):
        super(ObjectIcon, self).__init__()

        size_policy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # set to False so move event is only fired, when they are clicked and dragged
        self.setMouseTracking(False)

        self.setSizePolicy(size_policy)

        self.zoom = 1

        self.object: InLevelObject | None = None
        self.image = QImage()

        self.set_object(level_object)

        self.draw_background_color = True

        self.max_size = self.MIN_SIZE

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return super(ObjectIcon, self).mouseMoveEvent(event)

        assert self.object is not None

        drag = QDrag(self)

        mime_data = object_to_mime_data(self.object)

        drag.setMimeData(mime_data)

        if drag.exec() != Qt.DropAction.IgnoreAction:
            self.clicked.emit()

        return None

    def set_object(self, level_object: InLevelObject | None):
        if isinstance(level_object, Jump):
            return

        elif level_object is not None and (obj := get_minimal_icon_object(level_object)):
            self.object = obj

            if obj.name.lower() in objects_to_use_pngs_instead:
                self.image = objects_to_use_pngs_instead[obj.name.lower()]
            else:
                self.image = object_to_image(obj)

            if isinstance(obj, LevelObject):
                additional_data = f"{obj.domain:#x} {obj.obj_index:#x}"
            else:
                additional_data = f"{obj.obj_index:#x}"

            self.setToolTip(f"{obj.name}, {additional_data}")

        else:
            self.image = QImage()

        self.update_image()
        self.update()

    def update_image(self):
        if isinstance(self.object, Jump):
            return

        elif self.object is None:
            self.image = QImage()

        elif self.object.name.lower() in objects_to_use_pngs_instead:
            self.image = objects_to_use_pngs_instead[self.object.name.lower()]

        else:
            self.image = object_to_image(self.object)

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

            scaled_image = self.image.scaled(self.size(), aspectMode=Qt.AspectRatioMode.KeepAspectRatio)

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
