from enum import Enum
from typing import List, Tuple, Union

from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QMenu

from foundry.game.gfx.objects.EnemyItem import EnemyObject
from foundry.game.gfx.objects.LevelObject import LevelObject
from foundry.game.level.LevelRef import LevelRef


class CMAction(Enum):
    REMOVE = 1
    ADD_OBJECT = 2
    COPY = 4
    PASTE = 5
    CUT = 6
    BACKGROUND = 7
    FOREGROUND = 8


class CMMode(Enum):
    BG = 1
    OBJ = 2
    LIST = 3


ID_PROP: bytes = "ID"

MAX_ORIGIN = 0xFF, 0xFF


class ContextMenu(QMenu):
    def __init__(self, level_ref: LevelRef):
        super(ContextMenu, self).__init__()

        self.level_ref = level_ref

        self.copied_objects = None
        self.copied_objects_origin = 0, 0
        self.last_opened_at = QPoint(0, 0)

        self.cut_action = self.addAction("Cut")
        self.cut_action.setProperty(ID_PROP, CMAction.CUT)

        self.copy_action = self.addAction("Copy")
        self.copy_action.setProperty(ID_PROP, CMAction.COPY)

        self.paste_action = self.addAction("Paste")
        self.paste_action.setProperty(ID_PROP, CMAction.PASTE)

        self.addSeparator()

        self.into_background_action = self.addAction("To Background")
        self.into_background_action.setProperty(ID_PROP, CMAction.BACKGROUND)

        self.into_foreground_action = self.addAction("To Foreground")
        self.into_foreground_action.setProperty(ID_PROP, CMAction.FOREGROUND)

        self.addSeparator()

        self.remove_action = self.addAction("Remove")
        self.remove_action.setProperty(ID_PROP, CMAction.REMOVE)

        self.add_object_action = self.addAction("Add Object")
        self.add_object_action.setProperty(ID_PROP, CMAction.ADD_OBJECT)

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
        return self._setup_items(CMMode.OBJ)

    def as_background_menu(self) -> "ContextMenu":
        return self._setup_items(CMMode.BG)

    def as_list_menu(self) -> "ContextMenu":
        return self._setup_items(CMMode.LIST)

    def _setup_items(self, mode: CMMode):
        objects_selected = bool(self.level_ref.selected_objects)
        objects_copied = bool(self.copied_objects)

        self.cut_action.setEnabled(not mode == CMMode.BG and objects_selected)
        self.copy_action.setEnabled(not mode == CMMode.BG and objects_selected)
        self.paste_action.setEnabled(not mode == CMMode.LIST and objects_copied)

        self.into_background_action.setEnabled(not mode == CMMode.BG and objects_selected)
        self.into_foreground_action.setEnabled(not mode == CMMode.BG and objects_selected)

        self.remove_action.setEnabled(not mode == CMMode.BG and objects_selected)
        self.add_object_action.setEnabled(not mode == CMMode.LIST)

        return self
