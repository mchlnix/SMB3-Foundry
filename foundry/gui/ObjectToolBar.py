from typing import Union

from PySide2.QtCore import Qt, Signal, SignalInstance
from PySide2.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from foundry.game.gfx.objects.EnemyItem import EnemyObject
from foundry.game.gfx.objects.LevelObject import LevelObject
from foundry.game.gfx.objects.ObjectLike import ObjectLike
from foundry.gui.ObjectToolBox import ObjectIcon
from foundry.gui.TabbedToolBox import TabbedToolBox


class ObjectToolBar(QWidget):
    object_selected: SignalInstance = Signal(ObjectLike)

    def __init__(self, parent=None):
        super(ObjectToolBar, self).__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.current_object_icon = ObjectIcon()

        self.current_object_name = QLabel()
        self.current_object_name.setWordWrap(True)
        self.current_object_name.setAlignment(Qt.AlignCenter)

        current_item_widget = QWidget()
        current_item_widget.setFixedWidth(self.current_object_icon.MAX_SIZE.width() * 2)

        current_item_layout = QVBoxLayout(current_item_widget)
        current_item_layout.addWidget(QWidget(), stretch=1)
        current_item_layout.addWidget(self.current_object_icon, alignment=Qt.AlignCenter)
        current_item_layout.addWidget(self.current_object_name, alignment=Qt.AlignCenter)
        current_item_layout.addWidget(QWidget(), stretch=1)
        current_item_layout.setContentsMargins(0, 0, 0, 0)

        self.tool_box = TabbedToolBox()
        self.tool_box.object_icon_clicked.connect(self._on_object_icon_selected)

        layout.addWidget(current_item_widget)
        layout.addWidget(self.tool_box)

    def set_object_set(self, object_set_index: int, graphic_set_index: int = -1):
        self.tool_box.set_object_set(object_set_index, graphic_set_index)

    def _on_object_icon_selected(self, object_icon: ObjectIcon):
        self.select_object(object_icon.object)

        self.object_selected.emit(object_icon.object)

    def select_object(self, level_object: Union[LevelObject, EnemyObject]):
        self.tool_box.select_object(level_object)

        self.current_object_icon.set_object(level_object)
        self.current_object_name.setText(level_object.description)

    def on_toolbar_area_changed(self, new_toolbar_area):
        if new_toolbar_area == Qt.TopToolBarArea:
            self.tool_box.setTabPosition(self.tool_box.North)
        else:
            self.tool_box.setTabPosition(self.tool_box.South)

    def add_recent_object(self, level_object: Union[EnemyObject, LevelObject]):
        self.tool_box.add_recent_object(level_object)