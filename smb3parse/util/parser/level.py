from dataclasses import dataclass, field

from smb3parse.objects.level_object import goes_to_next_level, object_set_to_definition
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

    def has_jump(self):
        return any(
            goes_to_next_level(self.object_set_num, parsed_object.domain, parsed_object.obj_id)
            for parsed_object in self.parsed_objects
        ) or any(
            goes_to_next_level(self.object_set_num, parsed_enemy.domain, parsed_enemy.obj_id)
            for parsed_enemy in self.parsed_enemies
        )

    # TODO put those in level object next to goes_to_level?
    def has_generic_exit(self):
        """
        Certain objects jump not to the Destination marked in the level header, but a predefined Exit Level, that every
        world can set freely.

        :return: Returns True, if this Level has such an object.
        """
        definition = object_set_to_definition[self.object_set_num]

        if definition in [2, 11]:
            domain = 4
            id_range = range(0xE0, 0xF0)
        elif definition == 6:
            domain = 3
            id_range = range(0x60, 0x70)
        elif definition == 9:
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

        :return: Returns True, if this Level has such an object.
        """
        definition = object_set_to_definition[self.object_set_num]

        if definition in range(1, 12):
            domain = 1
            id_range = range(0xB0, 0xC0)
        else:
            return False

        return any(
            parsed_object.domain == domain and parsed_object.obj_id in id_range for parsed_object in self.parsed_objects
        )
