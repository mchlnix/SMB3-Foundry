from PySide2.QtCore import QPoint

from foundry.game.File import ROM
from foundry.game.gfx.Palette import load_palette
from foundry.game.gfx.PatternTable import PatternTable
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects.MapObject import MapObject
from foundry.game.level.LevelLike import LevelLike
from smb3parse.levels.world_map import (
    WorldMap as _WorldMap,
    WORLD_MAP_SCREEN_SIZE,
    WORLD_MAP_SCREEN_WIDTH,
    WORLD_MAP_HEIGHT,
)
from smb3parse.objects.object_set import WORLD_MAP_OBJECT_SET

OVERWORLD_GRAPHIC_SET = 0


class WorldMap(LevelLike):
    def __init__(self, world_index):
        super(WorldMap, self).__init__(0, world_index, None)

        self._internal_world_map = _WorldMap.from_world_number(ROM().rom_data, world_index)

        self.name = f"World {world_index} - Overworld"

        self.pattern_table = PatternTable(OVERWORLD_GRAPHIC_SET)
        self.palette_group = load_palette(WORLD_MAP_OBJECT_SET, 0)

        self.offset = self._internal_world_map.memory_address

        self.object_set = WORLD_MAP_OBJECT_SET
        self.tsa_data = ROM.get_tsa_data(self.object_set)

        self.objects = []

        self._load_objects(self._internal_world_map.layout_bytes)

        self._calc_size()

    def _load_objects(self, obj_data):
        self.objects.clear()

        for index, block_index in enumerate(obj_data):
            screen_offset = (index // WORLD_MAP_SCREEN_SIZE) * WORLD_MAP_SCREEN_WIDTH

            x = screen_offset + (index % WORLD_MAP_SCREEN_WIDTH)
            y = (index // WORLD_MAP_SCREEN_WIDTH) % WORLD_MAP_HEIGHT

            block = Block(block_index, self.palette_group, self.pattern_table, self.tsa_data)

            self.objects.append(MapObject(block, x, y))

        assert len(self.objects) % WORLD_MAP_HEIGHT == 0

    def _calc_size(self):
        self.width = len(self.objects) // WORLD_MAP_HEIGHT
        self.height = WORLD_MAP_HEIGHT

        self.size = self.width, self.height

    def add_object(self, obj, _):
        self.objects.append(obj)

        self.objects.sort(key=self._array_index)

    @staticmethod
    def _array_index(obj):
        return obj.y_position * WORLD_MAP_SCREEN_WIDTH + obj.x_position

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
        point = QPoint(x, y)

        for obj in reversed(self.objects):
            if obj.rect.contains(point):
                return obj

        return None

    def to_bytes(self):
        return_array = bytearray(len(self.objects))

        for obj in self.objects:
            index = self._array_index(obj)

            return_array[index] = obj.to_bytes()

        return self.offset, return_array

    def from_bytes(self, data, _=None):
        offset, obj_bytes = data

        self.offset = offset
        self._load_objects(obj_bytes)

        self._calc_size()

    def get_object(self, index):
        return self.objects[index]

    def remove_object(self, obj):
        self.objects.remove(obj)
