import json
from typing import List

from PySide2.QtCore import QRect, Qt, Signal, SignalInstance
from PySide2.QtGui import QCursor, QFocusEvent
from PySide2.QtWidgets import QLabel, QVBoxLayout, QWidget

from foundry.game.ObjectDefinitions import GeneratorType
from foundry.game.gfx.objects.EnemyItem import EnemyObject
from foundry.game.gfx.objects.LevelObject import GROUND
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.HeaderEditor import SCROLL_DIRECTIONS
from foundry.gui.util import clear_layout
from smb3parse.constants import OBJ_AUTOSCROLL
from smb3parse.objects.object_set import PLAINS_OBJECT_SET


class WarningList(QWidget):
    warnings_updated: SignalInstance = Signal(bool)

    def __init__(self, parent, level_ref: LevelRef):
        super(WarningList, self).__init__(parent)

        self.level_ref = level_ref
        self.level_ref.data_changed.connect(self._update_warnings)

        self.setLayout(QVBoxLayout())
        self.setWindowFlag(Qt.Popup)
        self.layout().setContentsMargins(5, 5, 5, 5)

        self._enemy_dict = {}
        self._build_enemy_clan_dict()

        self.warnings: List[str] = []

    def _update_warnings(self):
        self.warnings.clear()

        level = self.level_ref.level

        # check, that all jumps are inside the level
        for jump in level.jumps:
            if not level.get_rect(1).contains(jump.get_rect(1, level.is_vertical)):
                self.warnings.append(f"{jump} is outside of the level bounds.")

        # jump set without a next area
        if level.jumps and not level.has_next_area:
            self.warnings.append("Level has jumps set, but no Jump Destination in Level Header.")

        # level objects and enemies are inside the level
        for obj in level.get_all_objects():
            if isinstance(obj, EnemyObject) and obj.obj_index == OBJ_AUTOSCROLL:
                continue

            if not level.get_rect().contains(obj.get_rect()):
                self.warnings.append(f"{obj} is outside of level bounds.")

        # level objects to ground hitting the level edge
        for obj in level.objects:
            if obj.object_info == (PLAINS_OBJECT_SET, 0, 0x06):
                continue

            if obj.orientation in [GeneratorType.HORIZ_TO_GROUND, GeneratorType.PYRAMID_TO_GROUND]:
                if obj.y_position + obj.rendered_height == GROUND:
                    self.warnings.append(f"{obj} extends until the level bottom. This can crash the game.")

        # autoscroll objects
        for item in level.enemies:
            if item.obj_index == OBJ_AUTOSCROLL:
                if item.y_position >= 0x60:
                    self.warnings.append(f"{item}'s y-position is too low. Maximum is 95 or 0x5F.")

                if level.header.scroll_type_index != 0:
                    self.warnings.append(
                        f"Level has auto scrolling enabled, but the scrolling type in the level header is not "
                        f"'{SCROLL_DIRECTIONS[0]}. This might not work as expected."
                    )

        if len([item for item in level.enemies if item.obj_index == OBJ_AUTOSCROLL]) > 1:
            self.warnings.append("Level has more than one AutoScrolling items. Does that work?")

        # no items, that would crash the game
        for obj in level.objects:
            if obj.name == "MSG_CRASH":
                self.warnings.append(
                    f"Object at {obj.get_position()} will likely cause the game to crash, when loading or on screen."
                )

        # incompatible enemies
        enemies_in_level = [enemy for enemy in level.enemies if enemy.name in self._enemy_dict]

        for enemy in enemies_in_level.copy():
            enemies_in_level.pop(0)

            clan, group = self._enemy_dict[enemy.name]

            for other_enemy in enemies_in_level:
                other_clan, other_group = self._enemy_dict[other_enemy.name]

                if clan == other_clan and group != other_group:
                    self.warnings.append(f"{enemy} incompatible with {other_enemy}, when on same screen")

        self.update()
        self.warnings_updated.emit(bool(self.warnings))

    def _build_enemy_clan_dict(self):
        with open("data/enemy_data.json", "r") as enemy_data_file:
            enemy_data = json.loads(enemy_data_file.read())

            self._enemy_dict.clear()

            for clan, groups in enemy_data.items():
                for group, enemy_list in groups.items():
                    for enemy in enemy_list:
                        self._enemy_dict[enemy] = (clan, group)

    def update(self):
        self.hide()

        clear_layout(self.layout())

        for warning in self.warnings:
            self.layout().addWidget(QLabel(warning))

        super(WarningList, self).update()

    def show(self):
        pos = QCursor.pos()
        pos.setY(pos.y() + 10)

        self.setGeometry(QRect(pos, self.layout().sizeHint()))

        super(WarningList, self).show()

    def focusOutEvent(self, event: QFocusEvent):
        self.hide()

        super(WarningList, self).focusOutEvent(event)
