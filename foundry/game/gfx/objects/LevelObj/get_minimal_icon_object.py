from typing import Optional, Union
from foundry.game.gfx.objects.EnemyItem import EnemyObject
from foundry.game.gfx.objects.LevelObj.ObjectLikeLevelObjectRendererAdapter import (
    ObjectLikeLevelObjectRendererAdapter as LevelObject,
)


def get_minimal_icon_object(
    level_object: Union["LevelObject", EnemyObject]
) -> Optional[Union["LevelObject", EnemyObject]]:
    """
    Returns the object with a length, so that every block is rendered. E. g. clouds with length 0, don't have a face.
    """

    if not isinstance(level_object, (LevelObject, EnemyObject)):
        return None

    if isinstance(level_object, EnemyObject):
        return level_object

    level_object.ground_level = 3

    max_count = 10
    while (
        any(
            block not in level_object.level_object_renderer.block_group_renderer.blocks for block in level_object.blocks
        )
        and level_object.level_object_renderer.width < 0x10
    ):
        level_object.level_object_renderer.width += 1
        level_object.level_object_renderer.height += 1

        level_object.render()

        # no infinite loop
        max_count += 1
        if max_count >= 10:
            break

    return level_object
