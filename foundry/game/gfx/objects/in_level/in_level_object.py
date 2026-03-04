import abc

from foundry.game import EXPANDS_NOT
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects.object_like import ObjectLike
from foundry.game.gfx.Palette import PaletteGroup
from foundry.game.ObjectSet import ObjectSet


class InLevelObject(ObjectLike, abc.ABC):
    object_set: ObjectSet
    palette_group: PaletteGroup

    _obj_index: int
    domain: int
    is_4byte: bool

    data: bytearray

    rendered_width: int
    """Width after rendering the object. Only changes for expanding types."""
    rendered_height: int
    """Height after rendering the object. Only changes for expanding types."""

    anim_frame: int = 0

    def __init__(self):
        super(InLevelObject, self).__init__()

        # TODO base this on Position, like MapObjects do
        self.x_position = 0
        self.y_position = 0

    def display_size(self, zoom_factor: int = 1):
        return (
            self.rendered_width * Block.SIDE_LENGTH * zoom_factor,
            self.rendered_height * Block.SIDE_LENGTH * zoom_factor,
        )

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
    def increment_type(self):
        pass

    @abc.abstractmethod
    def decrement_type(self):
        pass

    @abc.abstractmethod
    def copy(self):
        pass

    @abc.abstractmethod
    def to_bytes(self):
        pass

    def expands(self):
        return EXPANDS_NOT

    def primary_expansion(self):
        return EXPANDS_NOT
