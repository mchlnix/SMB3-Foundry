from dataclasses import dataclass
from dataclasses import astuple
import yaml
from yaml import CLoader as Loader

from foundry.game.Range import Range
from foundry.game.ObjectDefinitions import load_object_definition_tile
from foundry import data_dir

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


@dataclass
class ObjectSetLevelData:
    name: str = ""
    jump_offset: int = 0x10010
    range: Range = Range(0, 0)

    @property
    def level_offset(self):
        return self.jump_offset

    @classmethod
    def from_dict(cls, dic: dict):
        """Makes ObjectSetLevelData from a dictionary"""
        jump_offset = dic["jump_offset"]
        jump_offset = int(jump_offset[1:], 16) if \
            isinstance(jump_offset, str) and jump_offset.startswith("$") else int(dic["jump_offset"])
        return cls(
            name=dic["name"],
            jump_offset=jump_offset,
            range=Range.from_dict(dic["range"])
        )


def load_obj_lvl_data_from_yaml(file_path: str):
    with open(file_path) as f:
        lvl_data = yaml.load(f, Loader=Loader)
    for key, set in lvl_data.items():
        lvl_data[key] = ObjectSetLevelData.from_dict(set)
    return lvl_data


class ObjectSet:
    def __init__(self, object_set_number: int):
        self.number = object_set_number

        if self.number == ENEMY_ITEM_OBJECT_SET:
            self.level_offset = 0
            self.name = "Enemy/Item Object set"
        else:
            self.name, self.level_offset, self._level_range = astuple(object_set_level_data[object_set_number])

            self._ending_graphic_offset = _ending_graphic_offset[object_set_number]

    @property
    def ending_graphic_offset(self):
        """Provides the end of level graphic rom offset"""
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

        return self._level_range.is_inside(memory_address)

    def object_length(self, domain: int, object_id: int) -> int:
        """
        Returns the byte length of an object with the given id, in the given domain in this object set.

        :param int domain: The domain of the object in question. Between 0 and 7.
        :param int object_id: The id of the object in question. Between 0 and 255.

        :return: The byte length of the object.
        :rtype: int
        """
        return load_object_definition_tile(self.number, object_id, domain).bytes


object_set_level_data = load_obj_lvl_data_from_yaml(data_dir.joinpath("object_level_data.yaml"))

with open(data_dir.joinpath("ending_graphic_offsets.yaml")) as f:
    ending_offset = yaml.load(f, Loader=Loader)
_ending_graphic_offset = [int(end_offset[1:], 16) if isinstance(end_offset, str) and end_offset.startswith("$")
                          else int(end_offset) for _, end_offset in ending_offset.items()]
