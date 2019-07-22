from game.gfx.objects.Jump import Jump
from game.gfx.objects.LevelObject import LevelObject, GROUND
from game.ObjectDefinitions import load_object_definitions
from game.gfx.Palette import load_palette
from game.gfx.PatternTable import PatternTable


class LevelObjectFactory:
    object_set: int
    graphic_set: int
    palette_group_index: int

    object_definitions: list = []
    pattern_table: PatternTable = None
    palette_group: list = []

    def __init__(
        self,
        object_set,
        graphic_set,
        palette_group_index,
        objects_ref,
        vertical_level,
        size_minimal=False,
    ):
        self.set_object_set(object_set)
        self.set_graphic_set(graphic_set)
        self.set_palette_group_index(palette_group_index)
        self.objects_ref = objects_ref
        self.vertical_level = vertical_level

        self.size_minimal = size_minimal

    def set_object_set(self, object_set):
        self.object_set = object_set
        self.object_definitions = load_object_definitions(self.object_set)

    def set_graphic_set(self, graphic_set):
        self.graphic_set = graphic_set
        self.pattern_table = PatternTable(self.graphic_set)

    def set_palette_group_index(self, palette_group_index):
        self.palette_group_index = palette_group_index
        self.palette_group = load_palette(self.object_set, self.palette_group_index)

    def from_data(self, data, index):
        if Jump.is_jump(data):
            return Jump(data)

        # todo get rid of index by fixing ground map
        return LevelObject(
            data,
            self.object_set,
            self.object_definitions,
            self.palette_group,
            self.pattern_table,
            self.objects_ref,
            self.vertical_level,
            index,
            size_minimal=self.size_minimal,
        )

    def from_properties(self, domain, object_index, x, y, length, index):
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
