import abc

from PySide6.QtCore import QRect

EXPANDS_NOT = 0b00
EXPANDS_HORIZ = 0b01
EXPANDS_VERT = 0b10
EXPANDS_BOTH = EXPANDS_HORIZ | EXPANDS_VERT


class ObjectLike(abc.ABC):
    obj_index: int
    domain: int
    name: str

    rect: QRect

    is_4byte: bool

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
    def set_position(self, x, y):
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
        if block_length != 1:
            x, y = self.rect.topLeft().toTuple()
            w, h = self.rect.size().toTuple()

            x *= block_length
            w *= block_length
            y *= block_length
            h *= block_length

            return QRect(x, y, w, h)
        else:
            return self.rect

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
