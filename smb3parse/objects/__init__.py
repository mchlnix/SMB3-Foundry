"""
Describes all objects, that are part of a level, i. e. platforms, enemies, items, jumps, auto scroll objects etc.
"""

from .enemy_item import EnemyItem
from .in_level_object import InLevelObject
from .level_object import LevelObject, goes_to_next_level
from .object_set import (
    ObjectSet,
    assert_valid_object_set_number,
    is_valid_object_set_number,
)

__all__ = [
    "ObjectSet",
    "assert_valid_object_set_number",
    "is_valid_object_set_number",
    "LevelObject",
    "goes_to_next_level",
    "InLevelObject",
    "EnemyItem",
]
