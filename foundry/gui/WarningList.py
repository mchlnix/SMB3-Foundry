import json
from typing import Sequence

from PySide6.QtCore import QEvent, QRect, Qt, Signal, SignalInstance
from PySide6.QtGui import QCursor, QFocusEvent
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from foundry import root_dir
from foundry.game import GROUND
from foundry.game.ObjectDefinitions import GeneratorType
from foundry.game.gfx.objects import EnemyItem
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.LevelView import LevelView
from foundry.gui.ObjectList import ObjectList
from foundry.gui.dialogs.HeaderEditor import CAMERA_MOVEMENTS
from foundry.gui.util import clear_layout
from smb3parse.constants import (
    OBJ_AUTOSCROLL,
    OBJ_BOOMBOOM,
    OBJ_CHEST_EXIT,
    OBJ_CHEST_ITEM_SETTER,
    OBJ_HAMMER_BRO,
    OBJ_PIPE_EXITS,
    OBJ_TREASURE_CHEST,
)
from smb3parse.objects.object_set import DUNGEON_OBJECT_SET, PLAINS_OBJECT_SET


class WarningList(QWidget):
    warnings_updated: SignalInstance = Signal(bool)

    def __init__(
        self,
        parent,
        level_ref: LevelRef,
        level_view_ref: LevelView,
        object_list_ref: ObjectList,
    ):
        super(WarningList, self).__init__(parent)

        self.level_ref = level_ref
        self.level_ref.data_changed.connect(self._update_warnings)

        self.level_view_ref = level_view_ref
        self.object_list = object_list_ref

        self.setLayout(QVBoxLayout())
        self.setWindowFlag(Qt.Popup)
        self.layout().setContentsMargins(5, 5, 5, 5)

        self._enemy_dict: dict[str, tuple[str, str]] = {}
        self._build_enemy_clan_dict()

        self.warnings: list[tuple[str, list[InLevelObject]]] = []

    def _update_warnings(self):
        self.warnings.clear()

        level = self.level_ref.level

        # check, that all jumps are inside the level
        for jump in level.jumps:
            if not level.get_rect(1).contains(jump.get_rect(1, level.is_vertical)):
                self.warn(f"{jump} is outside of the level bounds.", [])

        # jump set without a next area
        if level.jumps and not level.has_next_area:
            self.warn("Level has jumps set, but no Jump Destination in Level Header.", [])

        # level objects and enemies are inside the level
        for obj in level.get_all_objects():
            if isinstance(obj, EnemyItem) and obj.obj_index == OBJ_AUTOSCROLL:
                continue

            if not level.get_rect().contains(obj.get_rect()):
                self.warn(f"{obj} is outside of level bounds.", [obj])

        # level objects to ground hitting the level edge
        for obj in level.objects:
            if obj.object_info == (PLAINS_OBJECT_SET, 0, 0x06):
                continue

            if obj.orientation in [
                GeneratorType.HORIZ_TO_GROUND,
                GeneratorType.PYRAMID_TO_GROUND,
            ]:
                if obj.y_position + obj.rendered_height == GROUND:
                    self.warn(
                        f"{obj} extends until the level bottom. This can crash the game.",
                        [obj],
                    )

        # autoscroll objects
        for item in level.enemies:
            if item.obj_index == OBJ_AUTOSCROLL:
                if item.y_position >= 0x60:
                    self.warn(
                        f"{item}'s y-position is too low. Maximum is 95 or 0x5F.",
                        [item],
                    )

                if level.header.scroll_type_index != 0:
                    self.warn(
                        f"Level has auto scrolling enabled, but the scrolling type in the level header is not "
                        f"'{CAMERA_MOVEMENTS[0]}. This might not work as expected.",
                        [],
                    )

        autoscroll_items = [item for item in level.enemies if item.obj_index == OBJ_AUTOSCROLL]

        if len(autoscroll_items) > 1:
            self.warn(
                "Level has more than one AutoScrolling items. Does that work?",
                autoscroll_items,
            )

        # no items, that would crash the game
        for obj in level.objects:
            if obj.name == "MSG_CRASH" or "SMAS only" in obj.name:
                self.warn(
                    f"Object at {obj.get_position()} will likely cause the game to crash, when loading or on "
                    f"screen.",
                    [obj],
                )

        # incompatible enemies
        enemies_in_level = [enemy for enemy in level.enemies if enemy.name in self._enemy_dict]

        for enemy in enemies_in_level.copy():
            enemies_in_level.pop(0)

            clan, group = self._enemy_dict[enemy.name]

            for other_enemy in enemies_in_level:
                other_clan, other_group = self._enemy_dict[other_enemy.name]

                if clan == other_clan and group != other_group:
                    self.warn(
                        f"{enemy} incompatible with {other_enemy}, when on same screen",
                        [enemy, other_enemy],
                    )

        # boom boom not in dungeon level
        for enemy in level.enemies:
            if enemy.type != OBJ_BOOMBOOM:
                continue

            if level.object_set_number != DUNGEON_OBJECT_SET:
                self.warn(
                    "You should only use BoomBoom enemies in levels of object set 'Dungeon'.",
                    [enemy],
                )

            if enemy.y_position < 0x10:
                self.warn(
                    "If your BoomBoom has a lower y-position than 16, you need to add 1 to your Lock Index.",
                    [enemy],
                )

            break

        for enemy in level.enemies:
            if enemy.type != OBJ_PIPE_EXITS:
                continue

            if not level.header.pipe_ends_level:
                self.warn(
                    "You have a Pipe Pair Exit set (Level Settings), " "but Pipes don't end your Level (Lever Header).",
                    [],
                )

            break

        chest_exit_objects = self._find_enemies_in_level(OBJ_CHEST_EXIT)
        chest_exit_items = self._find_enemies_in_level(OBJ_CHEST_ITEM_SETTER)
        chest_objects = self._find_enemies_in_level(OBJ_TREASURE_CHEST)
        hammer_bro_objects = self._find_enemies_in_level(OBJ_HAMMER_BRO)

        # hammer bro level, does not end with chest
        if hammer_bro_objects and not chest_exit_objects:
            self.warn(
                "You have a Hammer Bro in your level, but it does not end by getting the chest. "
                "Go to Level Settings.",
                hammer_bro_objects,
            )

        # level ends with chest, but no item set
        if not hammer_bro_objects and not chest_exit_items and chest_exit_objects:
            self.warn(
                "You've set the level to end with getting a Chest, but there is no item in the chest.",
                chest_exit_objects,
            )

        if hammer_bro_objects and chest_exit_items:
            self.warn(
                "You are setting the item of a chest, but in Hammer Bros Levels, this is done through the Hammer "
                "Bros of the world map.",
                chest_exit_items,
            )

        if chest_exit_items and not chest_objects:
            self.warn(
                f"You have {len(chest_exit_items)} Chest Item objects, but no chest in the level to set items for.",
                chest_exit_items,
            )
        elif chest_objects and not chest_exit_items:
            self.warn(
                f"You have {len(chest_objects)} Chests, but no object that sets their items in the level. ",
                chest_objects,
            )

        self.update()
        self.warnings_updated.emit(bool(self.warnings))

    def _find_enemies_in_level(self, enemy_id: int) -> list[EnemyItem]:
        return [enemy for enemy in self.level_ref.level.enemies if enemy.type == enemy_id]

    def _build_enemy_clan_dict(self):
        with open(root_dir.joinpath("data", "enemy_data.json"), "r") as enemy_data_file:
            enemy_data = json.loads(enemy_data_file.read())

            self._enemy_dict.clear()

            for clan, groups in enemy_data.items():
                for group, enemy_list in groups.items():
                    for enemy in enemy_list:
                        self._enemy_dict[enemy] = (clan, group)

    def warn(self, msg: str, objects: Sequence[InLevelObject] | None = None):
        if objects is None:
            objects = []

        self.warnings.append((msg, list(objects)))

    def update(self):
        self.hide()

        clear_layout(self.layout())

        for warning in self.warnings:
            warning_message, related_objects = warning

            label = WarningLabel(warning_message, related_objects)
            label.hovered.connect(self._focus_objects)

            self.layout().addWidget(label)

        super(WarningList, self).update()

    def show(self):
        pos = QCursor.pos()
        pos.setY(pos.y() + 10)

        self.setGeometry(QRect(pos, self.layout().sizeHint()))

        super(WarningList, self).show()

    def _focus_objects(self):
        objects = self.sender().related_objects

        if objects:
            self.level_ref.blockSignals(True)

            self.level_view_ref.select_objects(objects)
            self.level_view_ref.scroll_to_objects(objects)
            self.object_list.update_content()

            self.level_ref.blockSignals(False)

    def focusOutEvent(self, event: QFocusEvent):
        self.hide()

        super(WarningList, self).focusOutEvent(event)


class WarningLabel(QLabel):
    hovered: SignalInstance = Signal()

    def __init__(self, text: str, related_objects: list[InLevelObject]):
        super(WarningLabel, self).__init__(text)

        self.related_objects = related_objects

    def enterEvent(self, event: QEvent):
        self.hovered.emit()

        return super(WarningLabel, self).enterEvent(event)
