import abc
from dataclasses import dataclass

from PySide2.QtCore import QRect
from foundry.game.Size import Size
from foundry.game.Position import Position
from foundry.game.Rect import Rect

EXPANDS_NOT = 0b00
EXPANDS_HORIZ = 0b01
EXPANDS_VERT = 0b10
EXPANDS_BOTH = EXPANDS_HORIZ | EXPANDS_VERT


@dataclass
class ObjectLike(abc.ABC):
    obj_index: int = 0
    domain: int = 0
    description: str = ""
    rect: QRect = QRect()
    is_4byte: bool = False

    @abc.abstractmethod
    def render(self):
        pass

    @abc.abstractmethod
    def draw(self, dc, zoom, transparent):
        pass

    @abc.abstractmethod
    def get_status_info(self):
        pass

    @abc.abstractmethod
    def set_position(self, pos):
        pass

    @abc.abstractmethod
    def move_by(self, dx, dy):
        pass

    @abc.abstractmethod
    def get_position(self):
        pass

    @abc.abstractmethod
    def resize_by(self, dx, dy):
        pass

    @abc.abstractmethod
    def point_in(self, x, y):
        pass

    def get_rect(self, block_length=1) -> QRect:
        """Scales the rect to the correct dimensions"""
        return Rect.scale_from(Rect.from_qrect(self.rect), block_length)

    @abc.abstractmethod
    def change_type(self, new_type):
        pass

    @abc.abstractmethod
    def __contains__(self, point):
        pass

    @abc.abstractmethod
    def to_bytes(self):
        pass

    def expands(self):
        return EXPANDS_NOT

    def primary_expansion(self):
        return EXPANDS_NOT

    @staticmethod
    def in_bounds(pos):
        pos.x = max(pos.x, 0)
        pos.y = max(pos.y, 0)
        return pos
