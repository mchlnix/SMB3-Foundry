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
        # make sure that when we don't want to render the level-filling, 0-length object that both lengths are the same
        # WOODEN_PLATFORM objects take the normal length or the 4-byte length, but seemingly never both
        if level_object.length == 0:
            level_object.length = 1

        if level_object.secondary_length == 0:
            level_object.secondary_length = 1

        if level_object.length > 0:
            level_object.secondary_length = level_object.length

        level_object.length = level_object.secondary_length

        # update the byte data
        level_object.data = level_object.to_bytes()
        level_object.render()

    while (
        any(block not in level_object.rendered_blocks for block in level_object.blocks) and level_object.length < 0x10
    ):
        level_object.length += 1

        if level_object.is_4byte:
            level_object.secondary_length += 1

        level_object.render()

    return level_object
