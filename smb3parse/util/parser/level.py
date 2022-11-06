from dataclasses import dataclass, field

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
