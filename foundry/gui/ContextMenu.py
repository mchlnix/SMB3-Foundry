from enum import Enum
from typing import Self, Sequence

from PySide6.QtCore import QPoint, SignalInstance
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu

from foundry import icon
from foundry.game.gfx.objects import EnemyItem, LevelObject
from foundry.game.gfx.objects.object_like import ObjectLike
from foundry.game.level.LevelRef import LevelRef
from smb3parse.data_points import Position


class CMMode(Enum):
    BG = 1
    OBJ = 2
    LIST = 3


MAX_ORIGIN = 0xFF, 0xFF


class ContextMenu(QMenu):
    def __init__(self, level_ref: LevelRef):
        super(ContextMenu, self).__init__()

        self.level_ref = level_ref

        self.copied_objects: list[ObjectLike] = []
        self.copied_objects_origin = Position.from_xy(0, 0)

        self.last_opened_at = QPoint(0, 0)

    def get_position(self) -> QPoint:
        return self.last_opened_at

    def set_copied_objects(self, objects: Sequence[ObjectLike]):
        if not objects:
            return

        self.copied_objects = [obj.copy() for obj in objects]

        min_x, min_y = MAX_ORIGIN

        for obj in objects:
            obj_x, obj_y = obj.get_position()

            min_x = min(min_x, obj_x)
            min_y = min(min_y, obj_y)

        min_x = max(min_x, 0)
        min_y = max(min_y, 0)

        self.copied_objects_origin = Position.from_xy(min_x, min_y)

    def get_copied_objects(self) -> tuple[list[ObjectLike], Position]:
        return self.copied_objects, self.copied_objects_origin

    def popup(self, pos: QPoint, at: QAction = None):
        self.last_opened_at = pos

        return super(ContextMenu, self).popup(pos, at)


class LevelContextMenu(ContextMenu):
    triggered: SignalInstance

    def __init__(self, level_ref: LevelRef):
        super(LevelContextMenu, self).__init__(level_ref)

        self.add_object_action = self.addAction("Place Object")
        self.add_object_action.setIcon(icon("plus.svg"))
        self.grab_selected_object_action = self.addAction("Grab Object")
        self.grab_selected_object_action.setIcon(icon("crosshair.svg"))

        self.addSeparator()

        self.cut_action = self.addAction("Cut")
        self.cut_action.setIcon(icon("scissors.svg"))
        self.copy_action = self.addAction("Copy")
        self.copy_action.setIcon(icon("copy.svg"))
        self.paste_action = self.addAction("Paste")
        self.paste_action.setIcon(icon("clipboard.svg"))

        self.addSeparator()

        self.into_foreground_action = self.addAction("To Foreground")
        self.into_foreground_action.setIcon(icon("upload.svg"))
        self.into_background_action = self.addAction("To Background")
        self.into_background_action.setIcon(icon("download.svg"))

        self.addSeparator()

        self.remove_action = self.addAction("Remove")
        self.remove_action.setIcon(icon("minus.svg"))

        self.object_to_grab: LevelObject | EnemyItem | None = None

    def as_object_menu(self, level_object: LevelObject | EnemyItem | None) -> Self:
        return self._setup_items(CMMode.OBJ, level_object)

    def as_background_menu(self, level_object: LevelObject | EnemyItem | None) -> Self:
        return self._setup_items(CMMode.BG, level_object)

    def as_list_menu(self, level_object: LevelObject | EnemyItem | None) -> Self:
        return self._setup_items(CMMode.LIST, level_object)

    def _setup_items(self, mode: CMMode | None, object_under_cursor: LevelObject | EnemyItem | None) -> Self:
        self.object_to_grab = object_under_cursor

        objects_selected = bool(self.level_ref.selected_objects)
        objects_copied = bool(self.copied_objects)

        self.grab_selected_object_action.setEnabled(object_under_cursor is not None)
        self.grab_selected_object_action.setText(
            f"Grab '{object_under_cursor.name}'" if object_under_cursor else "Nothing to grab"
        )

        self.cut_action.setEnabled(not mode == CMMode.BG and objects_selected)
        self.copy_action.setEnabled(not mode == CMMode.BG and objects_selected)
        self.paste_action.setEnabled(not mode == CMMode.LIST and objects_copied)

        self.into_background_action.setEnabled(not mode == CMMode.BG and objects_selected)
        self.into_foreground_action.setEnabled(not mode == CMMode.BG and objects_selected)

        self.remove_action.setEnabled(not mode == CMMode.BG and objects_selected)
        self.add_object_action.setEnabled(not mode == CMMode.LIST)

        return self
