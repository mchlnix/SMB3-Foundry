"""LevelObjectDefinitions provides the mechanisms to define each sprite and how it operates"""

from dataclasses import dataclass
from typing import List

from foundry.core.geometry.Size.Size import Size
from foundry.game.Rect import Rect


@dataclass
class ObjectOperation:
    """Provides the dataclass for the object operations"""
    init: int
    update: int
    hit: int
    pause_action: int
    kill_action: int
    ignores_stomping: bool
    shelled: bool
    can_squash: bool
    stomp_hurts: bool
    can_bump_into_shell: bool
    tail_immune: bool
    object_collision: bool
    weapon_immunity: bool
    fire_immunity: bool
    custom_collision: bool


@dataclass
class SpriteGraphic:
    """A sprite graphic for the ROM"""
    graphic: int
    horizontal_flip: bool = False
    vertical_flip: bool = False


@dataclass
class Animation:
    """An animation graphic"""
    page: int
    size: Size
    palette: int
    graphics: List[SpriteGraphic]


@dataclass
class Hitbox:
    """The hitbox information for the sprite"""
    block_detection_hitbox: Rect
    object_detection_hitbox: Rect


class LevelObjectDefinition:
    """The definition for an object"""
    name: str
    operation: ObjectOperation
    animations: List[Animation]
    hitbox: Hitbox

    def __init__(self, operation: ObjectOperation, animations: List[Animation], hitbox: Hitbox) -> None:
        self.operation = operation
        self.animations = animations
        self.hitbox = hitbox

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.operation}, {self.animations}, {self.hitbox})"
