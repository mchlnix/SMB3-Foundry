from PySide2.QtGui import Qt
from PySide2.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from foundry.gui.ObjectToolBox import ObjectIcon
from foundry.gui.TabbedToolBox import TabbedToolBox


class ObjectToolBar(QWidget):
    def __init__(self, parent=None):
        super(ObjectToolBar, self).__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.current_object_icon = ObjectIcon()
        self.current_object_name = QLabel()

        current_item_layout = QVBoxLayout()
        current_item_layout.addWidget(QWidget(), stretch=1)
        current_item_layout.addWidget(self.current_object_icon, alignment=Qt.AlignCenter)
        current_item_layout.addWidget(self.current_object_name, alignment=Qt.AlignCenter)
        current_item_layout.addWidget(QWidget(), stretch=1)
        current_item_layout.setContentsMargins(0, 0, 0, 0)

        self.tool_box = TabbedToolBox()

        layout.addLayout(current_item_layout)
        layout.addWidget(self.tool_box)

    def set_object_set(self, object_set_index: int, graphic_set_index: int = -1):
        self.tool_box.set_object_set(object_set_index, graphic_set_index)

        first_object_icon = self.tool_box._all_toolbox.layout().itemAt(0).widget()

        self.current_object_icon.set_object(first_object_icon.object)
        self.current_object_name.setText(first_object_icon.object.description)
