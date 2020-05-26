from typing import Optional, List

from foundry.game.gfx.objects.Jump import Jump
from foundry.game.gfx.objects.LevelObject import LevelObject
from foundry.game.gfx.Palette import load_palette
from foundry.game.gfx.GraphicsSet import GraphicsSet


class LevelObjectFactory:
    object_set: int
    graphic_set: int
    palette_group_index: int

    graphics_set: Optional[GraphicsSet] = None
    palette_group: list = []

    def __init__(
        self,
        object_set: int,
        graphic_set: int,
        palette_group_index: int,
        objects_ref: List[LevelObject],
        vertical_level: bool,
        size_minimal: bool = False,
    ):
        self.set_object_set(object_set)
        self.set_graphic_set(graphic_set)
        self.set_palette_group_index(palette_group_index)
        self.objects_ref = objects_ref
        self.vertical_level = vertical_level

        self.size_minimal = size_minimal

    def set_object_set(self, object_set: int):
        self.object_set = object_set

    def set_graphic_set(self, graphic_set: int):
        self.graphic_set = graphic_set
        self.graphics_set = GraphicsSet(self.graphic_set)

    def set_palette_group_index(self, palette_group_index: int):
        self.palette_group_index = palette_group_index
        self.palette_group = load_palette(self.object_set, self.palette_group_index)

    def from_data(self, data: bytearray, index: int):
        if Jump.is_jump(data):
            return Jump(data)

        assert self.graphics_set is not None

        # todo get rid of index by fixing ground map
        return LevelObject(
            data,
            self.object_set,
            self.palette_group,
            self.graphics_set,
            self.objects_ref,
            self.vertical_level,
            index,
            size_minimal=self.size_minimal,
        )

    def from_properties(
        self, domain: int, object_index: int, x: int, y: int, length: Optional[int], index: int,
    ):
        data = bytearray(3)

        data[0] = domain << 5 | y
        data[1] = x
        data[2] = object_index

        if length is not None:
            data.append(length)

        obj = self.from_data(data, index)

        if isinstance(obj, LevelObject):
            obj.set_position(x, y)

        return obj
