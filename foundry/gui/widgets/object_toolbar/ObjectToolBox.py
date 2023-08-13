from itertools import product
from typing import Optional

from PySide6.QtCore import QSize, Qt, Signal, SignalInstance
from PySide6.QtWidgets import QGridLayout, QSizePolicy, QWidget

from foundry.game import should_be_placeable
from foundry.game.gfx.objects import EnemyItemFactory, LevelObjectFactory
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from smb3parse.objects import MAX_DOMAIN, MAX_ENEMY_ITEM_ID, MAX_ID_VALUE
from smb3parse.util import apply
from .object_icon import ObjectIcon


COLUMN_COUNT = 2


class ObjectToolBox(QWidget):
    """A 2 column grid of Level Objects, Enemies or both. Clickable to select Item to place with the mouse."""

    object_icon_clicked: SignalInstance = Signal(ObjectIcon)

    def __init__(self, parent: Optional[QWidget] = None):
        super(ObjectToolBox, self).__init__(parent)

        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        self._layout = QGridLayout(self)
        self._layout.setAlignment(Qt.AlignCenter)

        self._layout.setAlignment(Qt.AlignHCenter)

    def sizeHint(self):
        orig_size_hint: QSize = super().sizeHint()
        width = COLUMN_COUNT * ObjectIcon.MIN_SIZE.width()

        orig_size_hint.setWidth(width)

        return orig_size_hint

    def add_object(self, level_object: InLevelObject, index: int = -1):
        icon = ObjectIcon(level_object)

        icon.clicked.connect(self._on_icon_clicked)

        if index == -1:
            index = self._layout.count()

        self._layout.addWidget(icon, index // COLUMN_COUNT, index % COLUMN_COUNT)

    def add_from_object_set(self, object_set_index: int, graphic_set_index: int = -1):
        if graphic_set_index == -1:
            graphic_set_index = object_set_index

        factory = LevelObjectFactory(
            object_set_index,
            graphic_set_index,
            0,
            [],
            vertical_level=False,
            size_minimal=True,
        )

        domains = range(MAX_DOMAIN + 1)
        object_ids = list(range(0x00, 0x10)) + list(range(0x10, MAX_ID_VALUE, 0x10))

        level_objects = [
            factory.from_properties(domain, obj_index, 0, 0, None, 0)
            for domain, obj_index in product(domains, object_ids)
        ]

        valid_level_objects = filter(should_be_placeable, level_objects)

        apply(self.add_object, valid_level_objects)

    def add_from_enemy_set(self, object_set_index: int):
        factory = EnemyItemFactory(object_set_index)

        enemy_items = map(factory.from_properties, range(MAX_ENEMY_ITEM_ID + 1))

        valid_enemy_items = filter(should_be_placeable, enemy_items)

        apply(self.add_object, valid_enemy_items)

    def clear(self):
        self._extract_objects()

    def _on_icon_clicked(self):
        self.object_icon_clicked.emit(self.sender())

    @property
    def draw_background_color(self):
        return self._layout.itemAt(0).draw_background_color

    @draw_background_color.setter
    def draw_background_color(self, value):
        for index in range(self._layout.count()):
            self._layout.itemAt(index).draw_background_color = value

    def has_object(self, level_object):
        return self.index_of_object(level_object) != -1

    def get_equivalent(self, level_object):
        for index in range(self._layout.count()):
            internal_object = self._layout.itemAtPosition(index // COLUMN_COUNT, index % COLUMN_COUNT).widget().object

            if internal_object.object_set == level_object.object_set and internal_object.type == level_object.type:
                return internal_object

        else:
            return None

    def index_of_object(self, level_object):
        for index in range(self._layout.count()):
            if self._layout.itemAtPosition(index // COLUMN_COUNT, index % COLUMN_COUNT).widget().object == level_object:
                return index
        else:
            return -1

    def _extract_objects(self):
        objects = []

        while True:
            item = self._layout.takeAt(0)

            if item is None:
                break
            else:
                objects.append(item.widget().object)
                item.widget().deleteLater()

        return objects

    def place_at_front(self, level_object):
        objects = self._extract_objects()

        if level_object in objects:
            objects.remove(level_object)

        objects.insert(0, level_object)

        assert self._layout.count() == 0

        for obj in objects:
            self.add_object(obj)
