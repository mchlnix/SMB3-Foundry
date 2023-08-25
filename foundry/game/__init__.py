from typing import TYPE_CHECKING

from smb3parse.constants import (
    OBJ_CHEST_EXIT,
    OBJ_CHEST_ITEM_SETTER,
    OBJ_PIPE_EXITS,
    OBJ_WHITE_MUSHROOM_HOUSE,
)

SKY = 0
GROUND = 27

EXPANDS_NOT = 0b00
EXPANDS_HORIZ = 0b01
EXPANDS_VERT = 0b10
EXPANDS_BOTH = EXPANDS_HORIZ | EXPANDS_VERT

if TYPE_CHECKING:
    from foundry.game.gfx.objects import EnemyItem, Jump, LevelObject


_EXCLUDED_ENEMY_ITEMS_IDS = [
    OBJ_PIPE_EXITS,
    OBJ_CHEST_EXIT,
    OBJ_WHITE_MUSHROOM_HOUSE,
    OBJ_CHEST_ITEM_SETTER,
]

_EXCLUDED_LEVEL_OBJECT_NAMES = ["MSG_NOTHING", "MSG_CRASH"]
_EXCLUDED_ENEMY_ITEMS_NAMES = ["MSG_NOTHING", "MSG_CRASH"]


def should_be_placeable(object_or_enemy_item: "LevelObject | Jump | EnemyItem") -> bool:
    """
    Returns whether the user should be able to place this object into a level manually. Is false for objects, that would
    crash the game, or determine properties, that can be better set using settings dialogues.
    """
    from foundry.game.gfx.objects import EnemyItem, Jump, LevelObject

    if isinstance(object_or_enemy_item, Jump):
        return False

    if isinstance(object_or_enemy_item, LevelObject):
        if object_or_enemy_item.name in _EXCLUDED_LEVEL_OBJECT_NAMES:
            return False

        elif "smas only" in object_or_enemy_item.name.lower():
            return False

    if isinstance(object_or_enemy_item, EnemyItem):
        if object_or_enemy_item.name in _EXCLUDED_ENEMY_ITEMS_NAMES:
            return False

        if object_or_enemy_item.obj_index in _EXCLUDED_ENEMY_ITEMS_IDS:
            return False

    return True
