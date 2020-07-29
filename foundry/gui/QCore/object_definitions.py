"""
Prefabs for object definitions
"""


from foundry.game.gfx.objects.objects.LevelObjectDefinition import Animation, SpriteGraphic
from foundry.game.Size import Size


DEFAULT_SPRITE_GRAPHIC = SpriteGraphic(1)
DEFAULT_ANIMATION = Animation(
    0, Size(1, 1), 0, [DEFAULT_SPRITE_GRAPHIC]
)