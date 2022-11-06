from smb3parse.levels import DEFAULT_HORIZONTAL_HEIGHT
from smb3parse.objects import InLevelObject
from smb3parse.objects.object_set import (
    AIR_SHIP_OBJECT_SET,
    CLOUDY_OBJECT_SET,
    DESERT_OBJECT_SET,
    DUNGEON_OBJECT_SET,
    ENEMY_ITEM_OBJECT_SET,
    GIANT_OBJECT_SET,
    HILLY_OBJECT_SET,
    ICE_OBJECT_SET,
    MUSHROOM_OBJECT_SET,
    PIPE_OBJECT_SET,
    PIRANHA_PLANT_OBJECT_SET,
    PLAINS_OBJECT_SET,
    SKY_OBJECT_SET,
    SPADE_BONUS_OBJECT_SET,
    UNDERGROUND_OBJECT_SET,
    WATER_OBJECT_SET,
    WORLD_MAP_OBJECT_SET,
)
from smb3parse.util import lrange

ENEMY_OBJECT_DEFINITION = 12

object_set_to_definition = {
    WORLD_MAP_OBJECT_SET: 0,
    PLAINS_OBJECT_SET: 1,
    MUSHROOM_OBJECT_SET: 1,
    SPADE_BONUS_OBJECT_SET: 1,
    HILLY_OBJECT_SET: 2,
    SKY_OBJECT_SET: 3,
    DUNGEON_OBJECT_SET: 4,
    AIR_SHIP_OBJECT_SET: 5,
    CLOUDY_OBJECT_SET: 6,
    DESERT_OBJECT_SET: 7,
    WATER_OBJECT_SET: 8,
    PIPE_OBJECT_SET: 8,
    PIRANHA_PLANT_OBJECT_SET: 9,
    GIANT_OBJECT_SET: 9,
    ICE_OBJECT_SET: 10,
    UNDERGROUND_OBJECT_SET: 11,
    ENEMY_ITEM_OBJECT_SET: ENEMY_OBJECT_DEFINITION,
}


def _obj_range(object_set: int, start: int) -> list[int]:
    """
    Expands a given obj_id start value to all possible object ids, that object could have.

    >>> _obj_range(PLAINS_OBJECT_SET, 0x0A)
    [0x0A]

    >>> _obj_range(WORLD_MAP_OBJECT_SET, 0xA0)
    [0xA0]

    >>> _obj_range(PLAINS_OBJECT_SET, 0xA0)
    [0xA0, 0xA1, ..., 0xAE, 0xAF]

    """
    if object_set in [WORLD_MAP_OBJECT_SET, ENEMY_ITEM_OBJECT_SET]:
        return [start]

    if start < 0x10:
        return [start]

    return lrange(start, start + 0x10)


def goes_to_next_level(object_set_num: int, domain: int, obj_id: int):
    # TODO only domain 0 is different, so condense this more
    object_id_ranges_by_domain_and_definition: dict[int, dict[int, list[int]]] = {
        1: {
            0: [0x04],
        },
        2: {
            0: [0x0F],
        },
        3: {
            0: [0x05],
        },
        4: {
            0: [0x00, 0x06],
        },
        5: {},
        6: {},
        7: {
            0: [0x0B],
        },
        8: {
            0: [0x0A],
        },
        9: {},
        10: {
            0: [0x05],
        },
        11: {
            0: [0x0F],
        },
        12: {
            0: [0x08, 0xD5],
        },
    }

    for definition in range(1, 12):
        # these objects are in all level object definitions
        object_id_ranges_by_domain_and_definition[definition][1] = [0x90, 0xC0, 0xE0]
        object_id_ranges_by_domain_and_definition[definition][2] = [0x07, 0x10]

    definition = object_set_to_definition[object_set_num]

    if definition not in object_set_to_definition:
        return False

    object_id_ranges_by_domain = object_id_ranges_by_domain_and_definition[definition]

    if domain not in object_id_ranges_by_domain:
        return False

    return any(obj_id in _obj_range(object_set_num, jump_obj_id) for jump_obj_id in object_id_ranges_by_domain[domain])


class LevelObject(InLevelObject):
    def __init__(self, data: bytearray):
        super(LevelObject, self).__init__(data)

        if len(data) not in [3, 4]:
            raise ValueError(f"Length of the given data must be 3 or 4, was {len(data)}.")

        self.domain = data[0] >> 5
        self.y = data[0] & 0b0001_1111

        if self.y > DEFAULT_HORIZONTAL_HEIGHT:
            raise ValueError(
                f"Data designating y value cannot be higher than {DEFAULT_HORIZONTAL_HEIGHT}, was {self.y}."
            )

        self.id = data[1]
        self.x = data[2]

        if len(data) == 4:
            self.additional_length = data[3]
