from dataclasses import dataclass

from smb3parse.util.parser.object import ParsedObject


@dataclass
class ParsedLevel:
    object_set_num: int
    graphics_set_num: int
    object_palette_num: int
    enemy_palette_num: int
    screen_memory: list[int]
    parsed_objects: list[ParsedObject]
