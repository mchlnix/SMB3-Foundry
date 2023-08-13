from PySide6.QtCore import Qt, Signal, SignalInstance
from PySide6.QtWidgets import QScrollArea, QScrollBar, QTabWidget

from foundry.game.gfx.objects import EnemyItem, LevelObject
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject

from .ObjectToolBox import ObjectIcon, ObjectToolBox

_INDEX_RECENTLY_USED = 0


class TabbedToolBox(QTabWidget):
    """Holds 3 ObjectToolboxes. One for Level Objects, one for enemies and one for recently used items."""

    object_icon_clicked: SignalInstance = Signal(ObjectIcon)

    def __init__(self, parent=None):
        super(TabbedToolBox, self).__init__(parent)

        self.setTabPosition(self.TabPosition.East)

        self._recent_toolbox = ObjectToolBox(self)
        self._recent_toolbox.setObjectName("Recent")
        self._recent_toolbox.object_icon_clicked.connect(self.object_icon_clicked.emit)

        self._objects_toolbox = ObjectToolBox(self)
        self._objects_toolbox.setObjectName("Level Objects")
        self._objects_toolbox.object_icon_clicked.connect(self.object_icon_clicked.emit)

        self._enemies_toolbox = ObjectToolBox(self)
        self._enemies_toolbox.setObjectName("Enemies")
        self._enemies_toolbox.object_icon_clicked.connect(self.object_icon_clicked.emit)

        for toolbox in (self._recent_toolbox, self._objects_toolbox, self._enemies_toolbox):
            scroll_area = QScrollArea(self)
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(toolbox)

            self.addTab(scroll_area, toolbox.objectName())

        self.show_level_object_tab()

        self.setWhatsThis(
            "<b>Object Toolbox</b><br/>"
            "Contains all objects and enemies/items, that can be placed in this type of level. Which are "
            "available depends on the object set, that is selected for this level.<br/>"
            "You can drag and drop objects into the level or click to select them. After selecting "
            "an object, you can place it by clicking the middle mouse button anywhere in the level."
            "<br/><br/>"
            "Note: Some items, like blocks with items in them, are displayed as they appear in the ROM, "
            "mouse over them and check their names in the ToolTip, or use the object dropdown to find "
            "them directly."
        )

    def sizeHint(self):
        orig_size = super().sizeHint()
        scrollbar_width = QScrollBar(Qt.Orientation.Vertical).sizeHint().width()

        orig_size.setWidth(orig_size.width() + self.tabBar().width() + scrollbar_width)

        return orig_size

    def show_recent_tab(self):
        self.setCurrentIndex(_INDEX_RECENTLY_USED)

    def show_level_object_tab(self):
        self.setCurrentIndex(1)

    def show_enemy_item_tab(self):
        self.setCurrentIndex(2)

    def select_object(self, level_object):
        recent_tab_showing = self.currentIndex() == _INDEX_RECENTLY_USED

        if self._recent_toolbox.has_object(level_object) and recent_tab_showing:
            pass
        elif isinstance(level_object, LevelObject):
            self.show_level_object_tab()
        elif isinstance(level_object, EnemyItem):
            self.show_enemy_item_tab()

    def set_object_set(self, object_set_index, graphic_set_index=-1):
        self._recent_toolbox.clear()
        self._objects_toolbox.clear()
        self._objects_toolbox.add_from_object_set(object_set_index, graphic_set_index)

        self._enemies_toolbox.clear()
        self._enemies_toolbox.add_from_enemy_set(object_set_index)

    def add_recent_object(self, level_object: InLevelObject):
        self._recent_toolbox.place_at_front(level_object)

    def get_equivalent(self, level_object: LevelObject | EnemyItem):
        return self._objects_toolbox.get_equivalent(level_object) or self._enemies_toolbox.get_equivalent(level_object)
