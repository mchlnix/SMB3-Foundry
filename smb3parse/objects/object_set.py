from collections import namedtuple

WORLD_MAP_OBJECT_SET = 0x00
PLAINS_OBJECT_SET = 0x01
DUNGEON_OBJECT_SET = 0x02
HILLY_OBJECT_SET = 0x03
SKY_OBJECT_SET = 0x04
PIRANHA_PLANT_OBJECT_SET = 0x05
WATER_OBJECT_SET = 0x06
MUSHROOM_OBJECT_SET = 0x07
PIPE_OBJECT_SET = 0x08
DESERT_OBJECT_SET = 0x09
AIR_SHIP_OBJECT_SET = 0x0A
GIANT_OBJECT_SET = 0x0B
ICE_OBJECT_SET = 0x0C
CLOUDY_OBJECT_SET = 0x0D
UNDERGROUND_OBJECT_SET = 0x0E
SPADE_BONUS_OBJECT_SET = 0x0F
ENEMY_ITEM_OBJECT_SET = 0x10

PLAINS_GRAPHICS_SET = 0x01
DUNGEON_GRAPHICS_SET = 0x02
HILLY_GRAPHICS_SET = 0x03
SKY_GRAPHICS_SET = 0x04
DESERT_GRAPHICS_SET = 0x09
CLOUDY_GRAPHICS_SET = 0x0D
UNDERGROUND_GRAPHICS_SET = 0x0E
ENEMY_ITEM_GRAPHICS_SET = 0x4C

MIN_OBJECT_SET = WORLD_MAP_OBJECT_SET
MAX_OBJECT_SET = 0x0F

# amount of consecutive objects in a group, that share the same byte length
OBJECT_GROUP_SIZE = 16


def assert_valid_object_set_number(object_set_number: int):
    if not is_valid_object_set_number(object_set_number):
        raise ValueError(f"Object set number {object_set_number} is invalid.")


def is_valid_object_set_number(object_set_number: int):
    return object_set_number in range(MIN_OBJECT_SET, MAX_OBJECT_SET + 1)


class ObjectSet:
    def __init__(self, object_set_number: int):
        self.number = object_set_number

        if self.number == ENEMY_ITEM_OBJECT_SET:
            self.level_offset = 0
            self.name = "Enemy/Item Object set"
        else:
            self.level_offset, self.name, self._level_range = object_set_level_data[object_set_number]

            self._object_length_lookup_table = _object_set_to_object_length_lookup_table[object_set_number]

            self._ending_graphic_offset = _ending_graphic_offset[object_set_number]

    @property
    def ending_graphic_offset(self):
        if self.number == ENEMY_ITEM_OBJECT_SET:
            raise ValueError(f"{self.name} is not a level object set and does not provide an ending graphic offset.")

        return self._ending_graphic_offset

    def is_in_level_range(self, memory_address: int) -> bool:
        """
        Checks if a given memory address falls inside the range of memory, where levels, using this object set, are
        allowed to be placed inside the rom.

        :param int memory_address: The memory address a level should be stored at.

        :return: Whether the level can be safely stored at the given address or not.
        :rtype: bool
        """
        if self.number == ENEMY_ITEM_OBJECT_SET:
            raise ValueError(f"{self.name} is not a level object set and does not provide a memory range.")

        return memory_address in self._level_range

    def object_length(self, domain: int, object_id: int) -> int:
        """
        Returns the byte length of an object with the given id, in the given domain in this object set.

        :param int domain: The domain of the object in question. Between 0 and 7.
        :param int object_id: The id of the object in question. Between 0 and 255.

        :return: The byte length of the object; either 3 or 4.
        :rtype: int
        """
        if self.number == ENEMY_ITEM_OBJECT_SET:
            return 3  # size of all enemies and items

        return self._object_length_lookup_table[domain][object_id // OBJECT_GROUP_SIZE]


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


_object_length_lookup_table = [
    (
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
    ),
    (
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
    ),
    (
        (3, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
    ),
    (
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3),
        (3, 3, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, 4, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
    ),
    (
        (3, 3, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3),
        (3, 3, 3, 3, 4, 3, 3, 4, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
    ),
    (
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3),
        (3, 4, 4, 3, 4, 3, 3, 4, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
    ),
    (
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
    ),
    (
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3),
        (3, 3, 3, 3, 3, 4, 3, 3, 3, 3, 3, 3, 3, 4, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
    ),
]

_object_set_to_object_length_lookup_table = {
    WORLD_MAP_OBJECT_SET: _object_length_lookup_table[0],
    PLAINS_OBJECT_SET: _object_length_lookup_table[0],
    MUSHROOM_OBJECT_SET: _object_length_lookup_table[0],
    SPADE_BONUS_OBJECT_SET: _object_length_lookup_table[0],
    HILLY_OBJECT_SET: _object_length_lookup_table[1],
    UNDERGROUND_OBJECT_SET: _object_length_lookup_table[1],
    SKY_OBJECT_SET: _object_length_lookup_table[2],
    ICE_OBJECT_SET: _object_length_lookup_table[2],
    DUNGEON_OBJECT_SET: _object_length_lookup_table[3],
    AIR_SHIP_OBJECT_SET: _object_length_lookup_table[4],
    PIRANHA_PLANT_OBJECT_SET: _object_length_lookup_table[5],
    GIANT_OBJECT_SET: _object_length_lookup_table[5],
    CLOUDY_OBJECT_SET: _object_length_lookup_table[5],
    DESERT_OBJECT_SET: _object_length_lookup_table[6],
    WATER_OBJECT_SET: _object_length_lookup_table[7],
    PIPE_OBJECT_SET: _object_length_lookup_table[7],
    # 16: Enemy/Item set always 3 bytes
}

_ending_graphic_offset = {
    WORLD_MAP_OBJECT_SET: 0,
    PLAINS_OBJECT_SET: 0,
    DUNGEON_OBJECT_SET: 0,
    HILLY_OBJECT_SET: 0,
    MUSHROOM_OBJECT_SET: 0,
    AIR_SHIP_OBJECT_SET: 0,
    CLOUDY_OBJECT_SET: 0,
    UNDERGROUND_OBJECT_SET: 0,  # Underground
    SPADE_BONUS_OBJECT_SET: 0,
    ENEMY_ITEM_OBJECT_SET: 0,
    SKY_OBJECT_SET: 1,
    ICE_OBJECT_SET: 1,
    PIRANHA_PLANT_OBJECT_SET: 2,
    DESERT_OBJECT_SET: 2,
    GIANT_OBJECT_SET: 2,
    WATER_OBJECT_SET: 3,
    PIPE_OBJECT_SET: 3,
}
