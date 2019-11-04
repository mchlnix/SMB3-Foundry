from typing import List, Union, Tuple

import wx

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


class ContextMenu(wx.Menu):
    def __init__(self):
        super(ContextMenu, self).__init__()

        self.copied_objects = None
        self.copied_objects_origin = 0, 0
        self.last_opened_at = wx.Point(0, 0)

        self.Append(id=ID_CTX_CUT, item="Cut")
        self.Append(id=ID_CTX_COPY, item="Copy")
        self.Append(id=ID_CTX_PASTE, item="Paste")
        self.AppendSeparator()
        self.Append(id=ID_CTX_REMOVE, item="Remove")
        self.Append(id=ID_CTX_ADD_OBJECT, item="Add Object")
        self.Append(id=ID_CTX_ADD_ENEMY, item="Add Enemy/Item")

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

    def set_position(self, position: wx.Point):
        self.last_opened_at = position

    def get_position(self) -> Tuple[int, int]:
        return self.last_opened_at.Get()

    def get_all_menu_item_ids(self) -> List[int]:
        return [item.GetId() for item in self.GetMenuItems()]

    def as_object_menu(self) -> "ContextMenu":
        self._setup_items(MODE_OBJ)

        return self

    def as_background_menu(self) -> "ContextMenu":
        self._setup_items(MODE_BG)

        return self

    def as_list_menu(self) -> "ContextMenu":
        self._setup_items(MODE_LIST)

        return self

    def _setup_items(self, mode: int):
        self.FindItemById(ID_CTX_CUT).Enable(not mode == MODE_BG)
        self.FindItemById(ID_CTX_COPY).Enable(not mode == MODE_BG)
        self.FindItemById(ID_CTX_PASTE).Enable(
            not mode == MODE_LIST and bool(self.copied_objects)
        )

        self.FindItemById(ID_CTX_REMOVE).Enable(not mode == MODE_BG)
        self.FindItemById(ID_CTX_ADD_OBJECT).Enable(not mode == MODE_LIST)
        self.FindItemById(ID_CTX_ADD_ENEMY).Enable(not mode == MODE_LIST)
