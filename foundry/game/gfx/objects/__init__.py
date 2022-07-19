from typing import Optional, Union

from foundry.game.gfx.objects.in_level.enemy_item import EnemyItem
from foundry.game.gfx.objects.in_level.enemy_item_factory import EnemyItemFactory
from foundry.game.gfx.objects.in_level.jump import Jump
from foundry.game.gfx.objects.in_level.level_object import LevelObject
from foundry.game.gfx.objects.in_level.level_object_factory import LevelObjectFactory
from foundry.game.gfx.objects.object_like import ObjectLike
from foundry.game.gfx.objects.world_map.airship_point import AirshipTravelPoint
from foundry.game.gfx.objects.world_map.level_pointer import LevelPointer
from foundry.game.gfx.objects.world_map.locks import Lock
from foundry.game.gfx.objects.world_map.map_object import MapObject
from foundry.game.gfx.objects.world_map.map_tile import MapTile
from foundry.game.gfx.objects.world_map.sprite import Sprite


def get_minimal_icon_object(level_object: Union["LevelObject", EnemyItem]) -> Optional[Union["LevelObject", EnemyItem]]:
    """
    Returns the object with a length, so that every block is rendered. E. g. clouds with length 0, don't have a face.
    """

    if not isinstance(level_object, (LevelObject, EnemyItem)):
        return None

    if isinstance(level_object, EnemyItem):
        return level_object

    level_object.ground_level = 3

    while (
        any(block not in level_object.rendered_blocks for block in level_object.blocks) and level_object.length < 0x10
    ):
        level_object.length += 1

        if level_object.is_4byte:
            level_object.secondary_length += 1

        level_object.render()

    return level_object


__all__ = [
    "AirshipTravelPoint",
    "LevelPointer",
    "Lock",
    "MapTile",
    "Sprite",
    "MapObject",
    "EnemyItem",
    "EnemyItemFactory",
    "Jump",
    "LevelObject",
    "LevelObjectFactory",
    "ObjectLike",
    "get_minimal_icon_object",
]
