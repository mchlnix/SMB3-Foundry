from PySide2.QtGui import Qt
from PySide2.QtWidgets import QScrollArea, QSizePolicy, QTabWidget

from foundry.gui.ObjectToolBox import ObjectToolBox


class TabbedToolBox(QTabWidget):
    def __init__(self, parent=None):
        super(TabbedToolBox, self).__init__(parent)

        self._recent_toolbox = ObjectToolBox(self)
        self._all_toolbox = ObjectToolBox(self)

        all_scroll_area = QScrollArea(self)
        all_scroll_area.viewport().setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        all_scroll_area.setWidgetResizable(True)
        all_scroll_area.setWidget(self._all_toolbox)

        self.addTab(self._recent_toolbox, "Recent")
        self.addTab(all_scroll_area, "All")

    def set_object_set(self, object_set_index, graphic_set_index=-1):
        self._recent_toolbox.clear()
        self._all_toolbox.clear()
        self._all_toolbox.add_from_object_set(object_set_index, graphic_set_index)
