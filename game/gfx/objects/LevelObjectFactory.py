from game.gfx.objects.LevelObject import LevelObject
from ObjectDefinitions import load_object_definition
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
        self, object_set, graphic_set, palette_group_index, objects_ref, vertical_level
    ):
        self.set_object_set(object_set)
        self.set_graphic_set(graphic_set)
        self.set_palette_group_index(palette_group_index)
        self.objects_ref = objects_ref
        self.vertical_level = vertical_level

    def set_object_set(self, object_set):
        self.object_set = object_set
        self.object_definitions = load_object_definition(self.object_set)

    def set_graphic_set(self, graphic_set):
        self.graphic_set = graphic_set
        self.pattern_table = PatternTable(self.graphic_set)

    def set_palette_group_index(self, palette_group_index):
        self.palette_group_index = palette_group_index
        self.palette_group = load_palette(self.object_set, self.palette_group_index)

    # todo get rid of index by fixing ground map
    def from_data(self, data, index):
        return LevelObject(
            data,
            self.object_set,
            self.object_definitions,
            self.palette_group,
            self.pattern_table,
            self.objects_ref,
            self.vertical_level,
            index,
        )

    def from_properties(self, domain, object_index, x, y, length, index):
        data = bytearray(3)

        data[0] = domain << 5 | 0
        data[1] = 0
        data[2] = object_index

        if length is not None:
            data.append(length)

        obj = self.from_data(data, index)
        obj.set_position(x, y)

        return obj
