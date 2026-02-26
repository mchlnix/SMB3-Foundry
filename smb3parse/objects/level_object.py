from smb3parse.levels import DEFAULT_HORIZONTAL_HEIGHT
from smb3parse.objects import InLevelObject
from smb3parse.objects.object_set import (
    ENEMY_ITEM_OBJECT_SET,
    PLAINS_OBJECT_SET,
    WORLD_MAP_OBJECT_SET,
)
from smb3parse.util import lrange

Domain = int
ObjectId = int
ObjectSetNo = int


def _obj_range(object_set: ObjectSetNo, start: ObjectId) -> list[ObjectId]:
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


def goes_to_next_level(object_set_num: ObjectSetNo, domain: Domain, obj_id: ObjectId):
    # there are special level objects, like doors, that will take the player to the jump destination
    object_id_ranges_by_domain_and_definition: dict[ObjectSetNo, dict[Domain, list[ObjectId]]] = {
        PLAINS_OBJECT_SET: {
            0: [0x04],
        },
        2: {
            0: [0x00, 0x06],
        },
        3: {
            0: [0x0F],
        },
        4: {
            0: [0x05],
        },
        5: {},
        6: {
            0: [0x0A],
        },
        7: {
            0: [0x04],
        },
        8: {
            0: [0x0A],
        },
        9: {
            0: [0x0B],
        },
        10: {},
        11: {},
        12: {
            0: [0x05],
        },
        13: {},
        14: {
            0: [0x0F],
        },
        15: {
            0: [0x04],
        },
        16: {
            0: [0x08, 0xD5],
        },
    }

    for definition in range(1, ENEMY_ITEM_OBJECT_SET):
        # these objects are in all level object definitions
        object_id_ranges_by_domain_and_definition[definition][1] = [0x90, 0xC0, 0xE0]
        object_id_ranges_by_domain_and_definition[definition][2] = [0x07, 0x10]

    object_id_ranges_by_domain = object_id_ranges_by_domain_and_definition[object_set_num]

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
