from PySide2.QtWidgets import QScrollArea, QTabWidget

from foundry.gui.ObjectToolBox import ObjectToolBox


class TabbedToolBox(QTabWidget):
    def __init__(self, parent=None):
        super(TabbedToolBox, self).__init__(parent)

        self.setTabPosition(self.South)

        self._recent_toolbox = ObjectToolBox(self)
        self._objects_toolbox = ObjectToolBox(self)
        self._enemies_toolbox = ObjectToolBox(self)

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
