import abc

from PySide6.QtGui import QImage

from foundry.game import EXPANDS_NOT
from foundry.game.ObjectSet import ObjectSet
from foundry.game.gfx.Palette import PaletteGroup
from foundry.game.gfx.objects.object_like import ObjectLike


class InLevelObject(ObjectLike, abc.ABC):
    object_set: ObjectSet
    palette_group: PaletteGroup

    _obj_index: int
    domain: int
    is_4byte: bool

    rendered_width: int

    def __init__(self):
        super(InLevelObject, self).__init__()

        self.x_position = 0
        self.y_position = 0

    @property
    def obj_index(self):
        return self._obj_index

    @obj_index.setter
    def obj_index(self, value):
        self._obj_index = value

    @abc.abstractmethod
    def render(self):
        pass

    @abc.abstractmethod
    def get_status_info(self):
        pass

    @abc.abstractmethod
    def resize_by(self, dx, dy):
        pass

    @abc.abstractmethod
    def as_image(self) -> QImage:
        pass

    @abc.abstractmethod
    def increment_type(self):
        pass

    @abc.abstractmethod
    def decrement_type(self):
        pass

    @abc.abstractmethod
    def to_bytes(self):
        pass

    def expands(self):
        return EXPANDS_NOT

    def primary_expansion(self):
        return EXPANDS_NOT
