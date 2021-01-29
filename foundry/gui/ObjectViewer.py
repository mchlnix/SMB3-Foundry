from typing import Union

from PySide2.QtCore import QPoint, QSize
from PySide2.QtGui import QPaintEvent, QPainter
from PySide2.QtWidgets import QComboBox, QHBoxLayout, QLayout, QStatusBar, QToolBar, QVBoxLayout, QWidget

from foundry.game.gfx.GraphicsSet import GRAPHIC_SET_NAMES
from foundry.game.gfx.drawable.Block import Block, get_block
from foundry.game.gfx.objects.Jump import Jump
from foundry.game.gfx.objects.LevelObj.ObjectLikeLevelObjectRendererAdapter import (
    ObjectLikeLevelObjectRendererAdapter as LevelObject,
)
from foundry.game.gfx.objects.LevelObjectFactory import LevelObjectFactory
from foundry.gui.CustomChildWindow import CustomChildWindow
from foundry.gui.LevelSelector import OBJECT_SET_ITEMS
from foundry.gui.Spinner import Spinner
from foundry.gui.util import clear_layout

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
        self.graphic_set_dropdown.addItems(GRAPHIC_SET_NAMES)
        self.graphic_set_dropdown.setCurrentIndex(1)

        self.object_set_dropdown.currentIndexChanged.connect(self.on_object_set)
        self.graphic_set_dropdown.currentIndexChanged.connect(self.on_graphic_set)

        _toolbar.addWidget(self.object_set_dropdown)
        _toolbar.addWidget(self.graphic_set_dropdown)

        self.addToolBar(_toolbar)

        self.drawing_area = ObjectDrawArea(self, 1)

        self.status_bar = QStatusBar(parent=self)
        self.status_bar.showMessage(self.drawing_area.current_object.name)

        self.setStatusBar(self.status_bar)

        self.drawing_area.update()

        self.block_list = BlockArray(self, self.drawing_area.current_object)

        central_widget = QWidget()
        central_widget.setLayout(QVBoxLayout())
        central_widget.layout().addWidget(self.drawing_area)
        central_widget.layout().addWidget(self.block_list)

        self.setCentralWidget(central_widget)

        self.layout().setSizeConstraint(QLayout.SetFixedSize)

        return

    def set_object_and_graphic_set(self, object_set: int, graphics_set: int):
        self.object_set_dropdown.setCurrentIndex(object_set - 1)
        self.graphic_set_dropdown.setCurrentIndex(graphics_set)

        self.drawing_area.change_object_set(object_set)
        self.drawing_area.change_graphic_set(graphics_set)

        self.block_list.update_object(self.drawing_area.current_object)
        self.status_bar.showMessage(self.drawing_area.current_object.name)

    def on_object_set(self):
        object_set = self.object_set_dropdown.currentIndex() + 1
        graphics_set = object_set

        self.set_object_and_graphic_set(object_set, graphics_set)

    def on_graphic_set(self):
        object_set = self.object_set_dropdown.currentIndex() + 1
        graphics_set = self.graphic_set_dropdown.currentIndex()

        self.set_object_and_graphic_set(object_set, graphics_set)

    def set_object(self, domain: int, obj_index: int, secondary_length: int):
        object_data = bytearray(4)

        object_data[0] = domain << 5
        object_data[1] = 0
        object_data[2] = obj_index
        object_data[3] = secondary_length

        self.spin_domain.setValue(domain)
        self.spin_type.setValue(obj_index)
        self.spin_length.setValue(secondary_length)

        self.drawing_area.update_object(object_data)
        self.block_list.update_object(self.drawing_area.current_object)

        if self.drawing_area.current_object.is_4byte:
            self.spin_length.setEnabled(True)
        else:
            self.spin_length.setValue(0)
            self.spin_length.setEnabled(False)

        self.drawing_area.update()

        self.status_bar.showMessage(self.drawing_area.current_object.name)

    def on_spin(self, _):
        domain = self.spin_domain.value()
        obj_index = self.spin_type.value()
        secondary_length = self.spin_length.value()

        self.set_object(domain, obj_index, secondary_length)


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
        if isinstance(self.current_object, Jump):
            return

        self.setMinimumSize(
            QSize(self.current_object.rendered_width * Block.WIDTH, self.current_object.rendered_height * Block.HEIGHT)
        )

    def update_object(self, object_data: Union[bytearray, LevelObject, Jump] = None):
        if object_data is None:
            object_data = self.current_object.data
        elif isinstance(object_data, (LevelObject, Jump)):
            object_data = object_data.data

        self.current_object = self.object_factory.from_data(object_data, 0)

        self.resize(QSize())
        self.update()

    def paintEvent(self, event: QPaintEvent):
        if not isinstance(self.current_object, LevelObject):
            return

        painter = QPainter(self)

        painter.translate(
            QPoint(-Block.WIDTH * self.current_object.x_position, -Block.HEIGHT * self.current_object.y_position)
        )

        self.current_object.draw(painter, Block.WIDTH, transparent=True)


class BlockArray(QWidget):
    def __init__(self, parent, level_object: LevelObject):
        super(BlockArray, self).__init__(parent)

        self.setLayout(QHBoxLayout())

        self.setContentsMargins(0, 0, 0, 0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        self.level_object = level_object

        self.update_object(level_object)

    def update_object(self, level_object: LevelObject):
        self.level_object = level_object

        clear_layout(self.layout())

        for block_index in self.level_object.blocks:
            block = get_block(
                block_index,
                self.level_object.palette_group,
                self.level_object.level_object_renderer.graphics_set,
                self.level_object.level_object_renderer.block_group_renderer.tsa_data,
            )
            self.layout().addWidget(BlockArea(block))

        self.update()


class BlockArea(QWidget):
    def __init__(self, block: Block):
        super(BlockArea, self).__init__()

        self.block = block

        self.setContentsMargins(0, 0, 0, 0)
        self.setToolTip(hex(self.block.index))

    def sizeHint(self):
        return QSize(Block.WIDTH, Block.HEIGHT)

    def paintEvent(self, event):
        painter = QPainter(self)

        self.block.draw(painter, 0, 0, Block.WIDTH)
