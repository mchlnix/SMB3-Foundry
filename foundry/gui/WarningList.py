from typing import List

from PySide2.QtCore import QRect, Qt, Signal, SignalInstance
from PySide2.QtGui import QCursor, QFocusEvent
from PySide2.QtWidgets import QLabel, QVBoxLayout, QWidget

from foundry.game.ObjectDefinitions import GeneratorType
from foundry.game.gfx.objects.LevelObject import GROUND
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.util import clear_layout


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
            if not level.get_rect().contains(obj.get_rect()):
                self.warnings.append(f"{obj} is outside of level bounds.")

        # level objects to ground hitting the level edge
        for obj in level.objects:
            if obj.description.lower() == "weird vine":
                continue

            if obj.orientation in [GeneratorType.HORIZ_TO_GROUND, GeneratorType.PYRAMID_TO_GROUND]:
                if obj.y_position + obj.rendered_height == GROUND:
                    self.warnings.append(f"{obj} extends until the level bottom. This can crash the game.")

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
