from typing import List, Union, Tuple

from PySide2.QtCore import QPoint
from PySide2.QtWidgets import QMenu

from foundry.game.gfx.objects.EnemyItem import EnemyObject
from foundry.game.gfx.objects.LevelObject import LevelObject

ID_CTX_REMOVE = 701
ID_CTX_ADD_OBJECT = 702
ID_CTX_ADD_ENEMY = 703
ID_CTX_COPY = 704
ID_CTX_PASTE = 705
ID_CTX_CUT = 706

MODE_BG = 0
MODE_OBJ = 1
MODE_LIST = 2

MAX_ORIGIN = 0xFF, 0xFF


class ContextMenu(QMenu):
    def __init__(self):
        super(ContextMenu, self).__init__()

        self.copied_objects = None
        self.copied_objects_origin = 0, 0
        self.last_opened_at = QPoint(0, 0)

        self.cut_action = self.addAction("Cut")
        self.cut_action.setProperty("ID", ID_CTX_CUT)

        self.copy_action = self.addAction("Copy")
        self.copy_action.setProperty("ID", ID_CTX_COPY)

        self.paste_action = self.addAction("Paste")
        self.paste_action.setProperty("ID", ID_CTX_PASTE)

        self.addSeparator()

        self.remove_action = self.addAction("Remove")
        self.remove_action.setProperty("ID", ID_CTX_REMOVE)

        self.add_object_action = self.addAction("Add Object")
        self.add_object_action.setProperty("ID", ID_CTX_ADD_OBJECT)

        self.add_enemy_action = self.addAction("Add Enemy/Item")
        self.add_enemy_action.setProperty("ID", ID_CTX_ADD_ENEMY)

    def set_copied_objects(self, objects: List[Union[LevelObject, EnemyObject]]):
        if not objects:
            return

        self.copied_objects = objects

        min_x, min_y = MAX_ORIGIN

        for obj in objects:
            obj_x, obj_y = obj.get_position()

            min_x = min(min_x, obj_x)
            min_y = min(min_y, obj_y)

        min_x = max(min_x, 0)
        min_y = max(min_y, 0)

        self.copied_objects_origin = min_x, min_y

    def get_copied_objects(self) -> Tuple[List[Union[LevelObject, EnemyObject]], Tuple[int, int]]:
        return self.copied_objects, self.copied_objects_origin

    def set_position(self, position: QPoint):
        self.last_opened_at = position

    def get_position(self) -> Tuple[int, int]:
        x, y = self.last_opened_at.toTuple()

        return x, y

    def get_all_menu_item_ids(self):
        return [action.property("ID") for action in self.actions()]

    def as_object_menu(self) -> "ContextMenu":
        return self._setup_items(MODE_OBJ)

    def as_background_menu(self) -> "ContextMenu":
        return self._setup_items(MODE_BG)

    def as_list_menu(self) -> "ContextMenu":
        return self._setup_items(MODE_LIST)

    def _setup_items(self, mode: int):

        self.cut_action.setEnabled(not mode == MODE_BG)
        self.copy_action.setEnabled(not mode == MODE_BG)
        self.paste_action.setEnabled(not mode == MODE_LIST and bool(self.copied_objects))

        self.remove_action.setEnabled(not mode == MODE_BG)
        self.add_object_action.setEnabled(not mode == MODE_LIST)
        self.add_enemy_action.setEnabled(not mode == MODE_LIST)

        return self
