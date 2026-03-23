from PySide6.QtCore import Qt, Signal, SignalInstance
from PySide6.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QWidget

from foundry.game.gfx.objects.in_level.enemy_item import EnemyItem
from foundry.game.gfx.objects.in_level.enemy_item_factory import EnemyItemFactory
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from foundry.game.gfx.objects.in_level.level_object import LevelObject
from foundry.game.gfx.objects.in_level.level_object_factory import LevelObjectFactory
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

        self.tabbed_tool_box = TabbedToolBox()
        self.tabbed_tool_box.object_icon_clicked.connect(self._on_object_icon_selected)

        layout.addWidget(self.tabbed_tool_box, stretch=1)
        layout.addWidget(current_item_widget)

        self._object_set_index = -1
        self._graphic_set_index = -1

    # TODO: Just give level reference?
    def set_object_set(self, object_set_index: int, graphic_set_index: int, palette_group_index: int):
        needs_full_update = self._object_set_index != object_set_index

        self._object_set_index = object_set_index
        self._graphic_set_index = graphic_set_index

        if needs_full_update:
            self.tabbed_tool_box.set_object_set(object_set_index, graphic_set_index, palette_group_index)

        else:
            self.tabbed_tool_box.set_graphic_set(graphic_set_index, palette_group_index)

            self._update_currently_selected_object_icon(object_set_index, graphic_set_index, palette_group_index)

    def _update_currently_selected_object_icon(
        self, object_set_index: int, graphic_set_index: int, palette_group_index: int
    ):
        # TODO Could this be put into the level icon class itself?

        current_object = self.current_object_icon.object

        if current_object is None:
            return

        if isinstance(current_object, LevelObject):
            lvl_factory = LevelObjectFactory(
                object_set_index,
                graphic_set_index,
                palette_group_index,
                [],
                vertical_level=False,
                size_minimal=True,
            )

            new_object = factory.from_properties(current_object.domain, current_object.obj_index, 0, 0, None, 0)

        elif isinstance(current_object, EnemyItem):
            factory = EnemyItemFactory(object_set_index, palette_group_index)

            new_object = factory.from_properties(current_object.obj_index, 0, 0)

        else:
            raise ValueError(f"Unknown object type: {type(current_object)}")

        self.current_object_icon.set_object(new_object)

    def _on_object_icon_selected(self, object_icon: ObjectIcon):
        if object_icon.object is None:
            return

        self.select_object(object_icon.object)

        self.object_selected.emit(object_icon.object)

    def select_object(self, level_object: InLevelObject):
        if not isinstance(level_object, (LevelObject, EnemyItem)):
            return

        if (level_object := self.tabbed_tool_box.get_equivalent(level_object)) is None:
            return

        self.tabbed_tool_box.select_object(level_object)

        self.current_object_icon.set_object(level_object)
        self.current_object_name.setText(level_object.name)
        self.add_recent_object(level_object)

    def add_recent_object(self, level_object: InLevelObject):
        self.tabbed_tool_box.add_recent_object(level_object)
