from PySide6.QtCore import Qt, Signal, SignalInstance
from PySide6.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QWidget

from foundry.game.gfx.objects import EnemyItem, LevelObject
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from foundry.game.gfx.objects.object_like import ObjectLike

from .ObjectToolBox import ObjectIcon
from .TabbedToolBox import TabbedToolBox


class ObjectToolBar(QWidget):
    """The Widget holding the tabbed toolbox and the current item icon. Sits at the top of the hierarchy."""

    object_selected: SignalInstance = Signal(ObjectLike)

    def __init__(self, parent=None):
        super(ObjectToolBar, self).__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)

        self.current_object_icon = ObjectIcon()
        self.current_object_icon.max_size = self.current_object_icon.MAX_SIZE

        self.current_object_name = QLabel()
        self.current_object_name.setWordWrap(True)
        self.current_object_name.setAlignment(Qt.AlignCenter)
        self.current_object_name.setContentsMargins(0, 0, 0, 0)

        current_item_widget = QGroupBox()
        current_item_widget.setContentsMargins(5, 10, 5, 5)
        current_item_widget.setFixedWidth(self.current_object_icon.MAX_SIZE.width() * 2)

        current_item_widget.setWhatsThis(
            "<b>Current Object</b><br/>"
            "Shows the currently selected object and its name. It can be placed by "
            "clicking the middle mouse button anywhere in the level."
        )

        current_item_layout = QVBoxLayout(current_item_widget)
        current_item_layout.addWidget(self.current_object_icon, alignment=Qt.AlignCenter)
        current_item_layout.addWidget(self.current_object_name, alignment=Qt.AlignCenter)

        self.tool_box = TabbedToolBox()
        self.tool_box.object_icon_clicked.connect(self._on_object_icon_selected)

        layout.addWidget(self.tool_box, stretch=1)
        layout.addWidget(current_item_widget)

    def set_object_set(self, object_set_index: int, graphic_set_index: int = -1):
        self.tool_box.set_object_set(object_set_index, graphic_set_index)

    def _on_object_icon_selected(self, object_icon: ObjectIcon):
        if object_icon.object is not None:
            self.select_object(object_icon.object)

            self.object_selected.emit(object_icon.object)

    def select_object(self, level_object: InLevelObject):
        if not isinstance(level_object, (LevelObject, EnemyItem)):
            return

        if (level_object := self.tool_box.get_equivalent(level_object)) is None:
            return

        self.tool_box.select_object(level_object)

        self.current_object_icon.set_object(level_object)
        self.current_object_name.setText(level_object.name)
        self.add_recent_object(level_object)

    def add_recent_object(self, level_object: InLevelObject):
        self.tool_box.add_recent_object(level_object)
