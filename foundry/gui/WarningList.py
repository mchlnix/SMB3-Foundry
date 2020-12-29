from typing import List

from PySide2.QtCore import QRect, Qt, Signal, SignalInstance
from PySide2.QtGui import QCursor, QFocusEvent
from PySide2.QtWidgets import QLabel, QVBoxLayout, QWidget

from foundry.game.gfx.objects.EnemyItem import EnemyObject
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
            if obj.description == "MSG_CRASH":
                self.warnings.append(
                    f"Object at {obj.get_position()} will likely cause the game to crash, when loading or on screen."
                )

        self.update()
        self.warnings_updated.emit(bool(self.warnings))

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
