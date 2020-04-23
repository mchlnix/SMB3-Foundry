from PySide2.QtCore import Signal, SignalInstance
from PySide2.QtWidgets import QScrollArea, QTabWidget

from foundry.gui.ObjectToolBox import ObjectIcon, ObjectToolBox


class TabbedToolBox(QTabWidget):
    object_icon_clicked: SignalInstance = Signal(ObjectIcon)

    def __init__(self, parent=None):
        super(TabbedToolBox, self).__init__(parent)

        self.setTabPosition(self.South)

        self._recent_toolbox = ObjectToolBox(self)
        self._recent_toolbox.object_icon_clicked.connect(self.object_icon_clicked)

        self._objects_toolbox = ObjectToolBox(self)
        self._objects_toolbox.object_icon_clicked.connect(self.object_icon_clicked)

        self._enemies_toolbox = ObjectToolBox(self)
        self._enemies_toolbox.object_icon_clicked.connect(self.object_icon_clicked)

        object_scroll_area = QScrollArea(self)
        object_scroll_area.setWidgetResizable(True)
        object_scroll_area.setWidget(self._objects_toolbox)

        enemies_scroll_area = QScrollArea(self)
        enemies_scroll_area.setWidgetResizable(True)
        enemies_scroll_area.setWidget(self._enemies_toolbox)

        self.addTab(self._recent_toolbox, "Recent")
        self.addTab(object_scroll_area, "Objects")
        self.addTab(enemies_scroll_area, "Enemies")

    def set_object_set(self, object_set_index, graphic_set_index=-1):
        self._recent_toolbox.clear()
        self._objects_toolbox.clear()
        self._objects_toolbox.add_from_object_set(object_set_index, graphic_set_index)

        self._enemies_toolbox.clear()
        self._enemies_toolbox.add_from_enemy_set(object_set_index)
