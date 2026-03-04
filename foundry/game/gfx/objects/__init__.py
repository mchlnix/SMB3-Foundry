from typing import TypeVar

from foundry.game.gfx.objects.in_level.in_level_object import (
    InLevelObject as _InLevelObject,
)
from foundry.game.gfx.objects.in_level.level_object import LevelObject
from foundry.game.ObjectDefinitions import GeneratorType

Iconifiable = TypeVar("Iconifiable", None, _InLevelObject)


def get_minimal_icon_object(level_object: Iconifiable) -> Iconifiable:
    """
    Returns the object with a length, so that every block is rendered. E.g. clouds with length 0 don't have a face.
    """
    if not isinstance(level_object, LevelObject):
        return level_object

    level_object.ground_level = 3

    if level_object.generator_type == GeneratorType.WOODEN_PLATFORM:
        level_object.length = 1

        level_object.render()

    while (
        any(block not in level_object.rendered_blocks for block in level_object.blocks) and level_object.length < 0x10
    ):
        level_object.length += 1

        if level_object.is_4byte:
            level_object.secondary_length += 1

        level_object.render()

    return level_object
