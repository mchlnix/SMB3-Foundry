import wx

from File import ROM
from game.gfx import PatternTable
from game.gfx.objects.MapObject import MapObject
from game.gfx import load_palette
from Sprite import Block
from game.level.LevelLike import LevelLike

OVERWORLD_OBJECT_SET = 0
OVERWORLD_GRAPHIC_SET = 0


class WorldMap(LevelLike):
    WIDTH = 16
    HEIGHT = 9

    VISIBLE_BLOCKS = WIDTH * HEIGHT

    def __init__(self, world_index):
        super(WorldMap, self).__init__(0, world_index, None)

        self.name = f"World {world_index} - Overworld"

        self.pattern_table = PatternTable(OVERWORLD_GRAPHIC_SET)
        self.palette_group = load_palette(OVERWORLD_OBJECT_SET, 0)

        start = ROM.W_LAYOUT_OS_LIST[world_index - 1]
        end = ROM.rom_data.find(0xFF, start)

        self.offset = start

        self.object_set = OVERWORLD_OBJECT_SET
        self.tsa_data = ROM.get_tsa_data(self.object_set)

        self.objects = []

        obj_data = ROM().bulk_read(end - start, start)

        self._load_objects(obj_data)

        self._calc_size()

    def _load_objects(self, obj_data):
        self.objects.clear()

        for index, block_index in enumerate(obj_data):
            screen_offset = (index // WorldMap.VISIBLE_BLOCKS) * WorldMap.WIDTH

            x = screen_offset + (index % WorldMap.WIDTH)
            y = (index // WorldMap.WIDTH) % WorldMap.HEIGHT

            block = Block(
                block_index, self.palette_group, self.pattern_table, self.tsa_data
            )

            self.objects.append(MapObject(block, x, y))

        assert len(self.objects) % WorldMap.HEIGHT == 0

    def _calc_size(self):
        self.width = len(self.objects) // WorldMap.HEIGHT
        self.height = WorldMap.HEIGHT

        self.size = self.width, self.height

    def add_object(self, obj, _):
        self.objects.append(obj)

        self.objects.sort(key=WorldMap._array_index)

    @staticmethod
    def _array_index(obj):
        return obj.y_position * WorldMap.WIDTH + obj.x_position

    def get_object_names(self):
        return [obj.name for obj in self.objects]

    def draw(self, dc, zoom, transparency=None):
        for obj in self.objects:
            obj.draw(dc, zoom, transparency)

    def index_of(self, obj):
        return self.objects.index(obj)

    def get_all_objects(self):
        return self.objects

    def object_at(self, x, y):
        point = wx.Point(x, y)

        for obj in reversed(self.objects):
            if obj.rect.Contains(point):
                return obj

        return None

    def to_bytes(self):
        return_array = bytearray(len(self.objects))

        for obj in self.objects:
            index = self._array_index(obj)

            return_array[index] = obj.to_bytes()

        return [(self.offset, return_array)]

    def from_bytes(self, data):
        offset, obj_bytes = data

        self.offset = offset
        self._load_objects(obj_bytes)

        self._calc_size()
