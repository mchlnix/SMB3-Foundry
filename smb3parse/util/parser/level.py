from dataclasses import dataclass, field

from smb3parse.constants import (
    CLOUDY_OBJECT_SET,
    ENEMY_ITEM_OBJECT_SET,
    ENEMY_SIZE,
    GIANT_OBJECT_SET,
    HILLY_OBJECT_SET,
    PIRANHA_PLANT_OBJECT_SET,
    PLAINS_OBJECT_SET,
    UNDERGROUND_OBJECT_SET,
)
from smb3parse.levels import HEADER_LENGTH
from smb3parse.objects.level_object import goes_to_next_level
from smb3parse.util.parser.object import ParsedEnemy, ParsedObject


@dataclass
class ParsedLevel:
    object_set_num: int
    graphics_set_num: int
    object_palette_num: int
    enemy_palette_num: int
    screen_memory: list[int]
    parsed_objects: list[ParsedObject]
    parsed_enemies: list[ParsedEnemy] = field(default_factory=list)

    @property
    def object_data_length(self):
        return HEADER_LENGTH + sum(len(obj.obj_bytes) for obj in self.parsed_objects)

    @property
    def enemy_data_length(self):
        return len(self.parsed_enemies) * ENEMY_SIZE

    def has_jump(self):
        return any(map(goes_to_next_level, self.parsed_objects + self.parsed_enemies))  # type:ignore

    def has_generic_exit(self):
        """
        Certain objects jump not to the Destination marked in the level header, but a predefined Exit Level, that every
        world can set freely.

        :return: Returns True, if this Level has such an object.
        """
        if self.object_set_num in [HILLY_OBJECT_SET, UNDERGROUND_OBJECT_SET]:
            domain = 4
            id_range = range(0xE0, 0xF0)
        elif self.object_set_num == CLOUDY_OBJECT_SET:
            domain = 3
            id_range = range(0x60, 0x70)
        elif self.object_set_num in [PIRANHA_PLANT_OBJECT_SET, GIANT_OBJECT_SET]:
            domain = 3
            id_range = range(0x50, 0x70)
        else:
            return False

        return any(
            parsed_object.domain == domain and parsed_object.obj_id in id_range for parsed_object in self.parsed_objects
        )

    def has_big_q_level(self):
        """
        Certain objects jump not to the Destination marked in the level header, but a predefined Big Question Mark
        Level, that every world can set freely.

        :return: Returns True if this Level has such an object.
        """
        if self.object_set_num in range(PLAINS_OBJECT_SET, ENEMY_ITEM_OBJECT_SET):
            domain = 1
            id_range = range(0xB0, 0xC0)
        else:
            return False

        return any(
            parsed_object.domain == domain and parsed_object.obj_id in id_range for parsed_object in self.parsed_objects
        )
