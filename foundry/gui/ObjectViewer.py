from typing import Union

from PySide2.QtCore import QPoint, QSize
from PySide2.QtGui import QPaintEvent, QPainter
from PySide2.QtWidgets import QComboBox, QLayout, QStatusBar, QToolBar, QWidget

from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects.Jump import Jump
from foundry.game.gfx.objects.LevelObjectController import LevelObjectController
from foundry.game.gfx.objects.LevelObjectFactory import LevelObjectFactory
from foundry.gui.CustomChildWindow import CustomChildWindow
from foundry.gui.LevelSelector import OBJECT_SET_ITEMS
from foundry.gui.Spinner import Spinner

ID_SPIN_DOMAIN = 1
ID_SPIN_TYPE = 2
ID_SPIN_LENGTH = 3
ID_OBJECT_SET_DROPDOWN = 4
ID_GFX_SET_DROPDOWN = 5

MAX_DOMAIN = 7
MAX_TYPE = 0xFF
MAX_LENGTH = 0xFF


class ObjectViewer(CustomChildWindow):
    def __init__(self, parent):
        super(ObjectViewer, self).__init__(parent, title="Object Viewer")

        self.spin_domain = Spinner(self, MAX_DOMAIN)
        self.spin_domain.valueChanged.connect(self.on_spin)

        self.spin_type = Spinner(self, MAX_TYPE)
        self.spin_type.valueChanged.connect(self.on_spin)

        self.spin_length = Spinner(self, MAX_LENGTH)
        self.spin_length.setDisabled(True)
        self.spin_length.valueChanged.connect(self.on_spin)

        _toolbar = QToolBar(self)

        _toolbar.addWidget(self.spin_domain)
        _toolbar.addWidget(self.spin_type)
        _toolbar.addWidget(self.spin_length)

        self.object_set_dropdown = QComboBox(_toolbar)
        self.object_set_dropdown.addItems(OBJECT_SET_ITEMS[1:])
        self.object_set_dropdown.setCurrentIndex(0)

        self.graphic_set_dropdown = QComboBox(_toolbar)
        self.graphic_set_dropdown.addItems([f"Graphics Set {gfx_set}" for gfx_set in range(32)])
        self.graphic_set_dropdown.setCurrentIndex(1)

        self.object_set_dropdown.currentIndexChanged.connect(self.on_object_set)
        self.graphic_set_dropdown.currentIndexChanged.connect(self.on_graphic_set)

        _toolbar.addWidget(self.object_set_dropdown)
        _toolbar.addWidget(self.graphic_set_dropdown)

        self.addToolBar(_toolbar)

        self.object_set = 1

        self.drawing_area = ObjectDrawArea(self, self.object_set)

        self.status_bar = QStatusBar(parent=self)
        self.status_bar.showMessage(self.drawing_area.current_object.description)

        self.setStatusBar(self.status_bar)

        self.setCentralWidget(self.drawing_area)

        self.drawing_area.update()

        self.layout().setSizeConstraint(QLayout.SetFixedSize)

    def on_object_set(self):
        self.object_set = self.object_set_dropdown.currentIndex() + 1

        gfx_set = self.object_set

        self.graphic_set_dropdown.setCurrentIndex(gfx_set)

        self.drawing_area.change_object_set(self.object_set)

        self.drawing_area.change_graphic_set(gfx_set)
        self.status_bar.showMessage(self.drawing_area.current_object.description)

    def on_graphic_set(self):
        gfx_set = self.graphic_set_dropdown.currentIndex()

        self.drawing_area.change_graphic_set(gfx_set)
        self.status_bar.showMessage(self.drawing_area.current_object.description)

    def on_spin(self, _):
        object_data = bytearray(4)

        object_data[0] = self.spin_domain.value() << 5
        object_data[1] = 0
        object_data[2] = self.spin_type.value()
        object_data[3] = self.spin_length.value()

        self.drawing_area.update_object(object_data)

        if self.drawing_area.current_object.is_4byte:
            self.spin_length.setEnabled(True)
        else:
            self.spin_length.setValue(0)
            self.spin_length.setEnabled(False)

        self.drawing_area.update()

        self.status_bar.showMessage(self.drawing_area.current_object.description)


class ObjectDrawArea(QWidget):
    def __init__(self, parent, object_set, graphic_set=1, palette_index=0):
        super(ObjectDrawArea, self).__init__(parent)

        self.object_factory = LevelObjectFactory(object_set, graphic_set, palette_index, [], False, size_minimal=True)

        self.current_object = self.object_factory.from_data(bytearray([0x0, 0x0, 0x0]), 0)

        self.update_object()

        self.resize(QSize())

    def change_object_set(self, object_set: int):
        self.object_factory.set_object_set(object_set)

        self.update_object()

    def change_graphic_set(self, graphic_set: int):
        self.object_factory.set_graphic_set(graphic_set)
        self.update_object()

    def resize(self, size: QSize):
        self.setMinimumSize(
            QSize(self.current_object.rendered_width * Block.WIDTH, self.current_object.rendered_height * Block.HEIGHT)
        )

    def update_object(self, object_data: Union[bytearray, LevelObjectController, Jump] = None):
        if object_data is None:
            object_data = self.current_object.data
        elif isinstance(object_data, (LevelObjectController, Jump)):
            object_data = object_data.data

        self.current_object = self.object_factory.from_data(object_data, 0)

        self.resize(QSize())
        self.update()

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)

        painter.translate(
            QPoint(
                -Block.WIDTH * self.current_object.rendered_base_x, -Block.HEIGHT * self.current_object.rendered_base_y
            )
        )

        self.current_object.draw(painter, Block.WIDTH, transparent=True)
