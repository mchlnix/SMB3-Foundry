"""Test doubles for localization display-boundary regressions."""

from types import SimpleNamespace

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget

from foundry.game.gfx.objects.in_level.jump import Jump
from foundry.gui.dialogs.LevelHeaderEditor import (
    LEVEL_LENGTHS,
    CameraMovement,
    HeaderMusic,
    HeaderStartAction,
    HeaderTime,
)


class CounterLevelRef(QObject):

    data_changed = Signal()

    def __init__(self):
        super().__init__()
        self.object_size_on_disk = 20
        self.enemy_size_on_disk = 12
        self.level = SimpleNamespace(attached_to_rom=False, object_set_number=0)
        self.jumps = [Jump.from_properties(3, 0, 0, 0)]

    def current_object_size(self) -> int:
        return 7

    def current_enemies_size(self) -> int:
        return 5


class StatusLevelRef(QObject):

    data_changed = Signal()

    def __init__(self, selected_object):
        super().__init__()
        self.selected_objects = [selected_object]


class StatusLevelObject:

    name = "Underwater Flat Ground"

    def get_status_info(self):
        return [("Width", 3), ("Height", 2), ("GeneratorType", "None"), ("Ending", "None")]


class EnemyItem:

    name = "Still Bullet Bill"

    def get_status_info(self):
        return [("Name", self.name), ("X", 4), ("Y", 5)]


class HeaderJumpObjectSet:

    level_offset = 0x2000


class Header:

    jump_level_offset = 0x40
    jump_enemy_offset = 0x80
    jump_object_set = HeaderJumpObjectSet()


class HeaderLevelRef(QObject):

    data_changed = Signal()
    palette_changed = Signal()

    def __init__(self):
        super().__init__()
        self.length = LEVEL_LENGTHS[0]
        self.music_index = HeaderMusic.PLAIN_LEVEL
        self.time_index = HeaderTime.SECONDS_300
        self.scroll_type = CameraMovement.LOCKED_UNLESS_CLIMBING_FLYING
        self.is_vertical = False
        self.pipe_ends_level = False
        self.start_x_index = 0
        self.start_y_index = 0
        self.start_action = HeaderStartAction.NONE
        self.object_palette_index = 0
        self.enemy_palette_index = 0
        self.graphic_set = 0
        self.next_area_object_set_no = 0
        self.header = Header()
        self.header_bytes = bytearray(range(9))


class FakeScribeTool(QWidget):

    selection_changed = Signal(int)
    tile_selected = Signal(int)

    def __init__(self, *_args, **_kwargs):
        super().__init__()
        self.retranslate_count = 0

    def clearSelection(self):
        pass

    def retranslate_ui(self):
        self.retranslate_count += 1


class FakeWorldMapLevelSelect(QWidget):

    level_clicked = Signal(object)
    level_selected = Signal(object)

    def __init__(self, *_args, **_kwargs):
        super().__init__()
