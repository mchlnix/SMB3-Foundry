from smb3parse.constants import (
    AIR_SHIP_OBJECT_SET,
    BASE_OFFSET,
    CLOUDY_OBJECT_SET,
    DESERT_OBJECT_SET,
    DUNGEON_OBJECT_SET,
    ENEMY_ITEM_OBJECT_SET,
    GIANT_OBJECT_SET,
    HILLY_OBJECT_SET,
    ICE_OBJECT_SET,
    MAX_OBJECT_SET,
    MIN_OBJECT_SET,
    MUSHROOM_OBJECT_SET,
    OBJECT_SET_NAMES,
    PAGE_A000_OFFSET,
    PIPE_OBJECT_SET,
    PIRANHA_PLANT_OBJECT_SET,
    PLAINS_OBJECT_SET,
    SKY_OBJECT_SET,
    SPADE_BONUS_OBJECT_SET,
    UNDERGROUND_OBJECT_SET,
    WATER_OBJECT_SET,
    WORLD_MAP_OBJECT_SET,
    Constants,
)
from smb3parse.util.rom import PRG_BANK_SIZE, Rom

# number of consecutive objects in a group that share the same byte length
OBJECT_GROUP_SIZE = 16


def assert_valid_object_set_number(object_set_number: int):
    if not is_valid_object_set_number(object_set_number):
        raise ValueError(f"Object set number {object_set_number} is invalid.")


def is_valid_object_set_number(object_set_number: int):
    return object_set_number in range(MIN_OBJECT_SET, MAX_OBJECT_SET + 1)


class ObjectSet:
    def __init__(self, rom: Rom, object_set_number: int):
        self.rom = rom
        self.number = object_set_number

        self.level_offset = BASE_OFFSET

        if self.number != ENEMY_ITEM_OBJECT_SET:
            object_set_offset = self.rom.int(Constants.OFFSET_BY_OBJECT_SET_A000 + self.number) * PRG_BANK_SIZE

            self.level_offset += object_set_offset - PAGE_A000_OFFSET

            self._ending_graphic_index = _object_set_to_ending_graphic_index[object_set_number]

        if self.number < len(OBJECT_SET_NAMES):
            self.name = OBJECT_SET_NAMES[self.number]
        else:
            self.name = f"Object Set {self.number:#x}"

    @property
    def ending_graphic_index(self):
        if self.number == ENEMY_ITEM_OBJECT_SET:
            raise ValueError(f"{self.name} is not a level object set and does not provide an ending graphic offset.")

        return self._ending_graphic_index

    def __repr__(self):
        return f"ObjectSet({self.number}), {self.name}"


# TODO this could be read out of the ROM see LoadLevel_EndGoalDecoSquare
_object_set_to_ending_graphic_index = {
    WORLD_MAP_OBJECT_SET: 0,
    PLAINS_OBJECT_SET: 0,
    DUNGEON_OBJECT_SET: 0,
    HILLY_OBJECT_SET: 0,
    MUSHROOM_OBJECT_SET: 0,
    AIR_SHIP_OBJECT_SET: 0,
    CLOUDY_OBJECT_SET: 0,
    UNDERGROUND_OBJECT_SET: 0,
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
