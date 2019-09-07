from collections import namedtuple

WORLD_MAP_OBJECT_SET = 0x00
ENEMY_ITEM_OBJECT_SET = 0x10

MIN_OBJECT_SET = WORLD_MAP_OBJECT_SET
MAX_OBJECT_SET = 0x0F


def is_valid_object_set_number(object_set_number: int):
    return object_set_number in range(MIN_OBJECT_SET, MAX_OBJECT_SET + 1)


ObjectSetLevelData = namedtuple("ObjectSetPointerType", "offset name level_range")

object_set_level_data = [
    ObjectSetLevelData(0x0000, "Map Screen", range(0x18010, 0x1A00F)),
    ObjectSetLevelData(0x4000, "Plains", range(0x1E512, 0x2000F)),
    ObjectSetLevelData(0x10000, "Dungeon", range(0x2A7F7, 0x2C00F)),
    ObjectSetLevelData(0x6000, "Hilly", range(0x20587, 0x2200F)),
    ObjectSetLevelData(0x8000, "Sky", range(0x227E0, 0x2400F)),
    ObjectSetLevelData(0xC000, "Piranha Plant", range(0x26A6F, 0x2800F)),
    ObjectSetLevelData(0xA000, "Water", range(0x24BA7, 0x2600F)),
    ObjectSetLevelData(0x0000, "Mushroom House", range(0x0000, 0x0000)),
    ObjectSetLevelData(0xA000, "Pipe", range(0x24BA7, 0x2600F)),
    ObjectSetLevelData(0xE000, "Desert", range(0x28F3F, 0x2A00F)),
    ObjectSetLevelData(0x14000, "Ship", range(0x2EC07, 0x3000F)),
    ObjectSetLevelData(0xC000, "Giant", range(0x26A6F, 0x2800F)),
    ObjectSetLevelData(0x8000, "Ice", range(0x227E0, 0x2400F)),
    ObjectSetLevelData(0xC000, "Cloudy", range(0x26A6F, 0x2800F)),
    ObjectSetLevelData(0x0000, "Underground", range(0x1A587, 0x1C00F)),
    ObjectSetLevelData(0x0000, "Spade House", range(0xA010, 0xC00F)),
]


class ObjectSet:
    def __init__(self, object_set_number: int):
        self._object_set_number = object_set_number

        self.level_offset, self._name, self._level_range = object_set_level_data[object_set_number]

    def is_in_level_range(self, level_offset: int) -> bool:
        return level_offset in self._level_range
