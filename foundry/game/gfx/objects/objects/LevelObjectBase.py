"""Provides the core element of an object in game"""

from typing import List
from PySide2.QtGui import QPainter

from foundry.game.Size import Size
from foundry.game.Position import Position
from foundry.game.Rect import Rect
from foundry.game.gfx.drawable.SpriteElement import SpriteElement
from foundry.game.gfx.objects.objects.LevelObjectDefinition import LevelObjectDefinition, Animation, SpriteGraphic, \
    ObjectOperation
from foundry.core.Observable import Observable


class LevelObject:
    """A level block generator that is editable and provides rendered blocks"""
    def __init__(
            self,
            definition: LevelObjectDefinition,
            palette_group: List[List[int]],
            animation_index: int = 0,
            sprite_index: int = 0
    ) -> None:
        self.definition = definition
        self.animation_index = animation_index
        self.sprite_index = sprite_index
        self.palette_group = palette_group

        # Makes a bunch of observers to send updates to various gui elements
        self.action_name = Observable(lambda value: value)
        self.action_page = Observable(lambda value: value)
        self.action_size = Observable(lambda value: value)
        self.action_palette = Observable(lambda value: value)
        self.action_graphic = Observable(lambda value: value)
        self.action_horizontal_mirror = Observable(lambda value: value)
        self.action_vertical_mirror = Observable(lambda value: value)
        self.action_operation = Observable(lambda value: value)
        self.action_hitbox = Observable(lambda value: value)
        self.action_bounding_box = Observable(lambda value: value)

    @property
    def name(self) -> str:
        """The name of the definition"""
        return self.definition.name

    @name.setter
    def name(self, name: str) -> None:
        self.definition.name = name
        self.action_name(name)

    @property
    def animations(self) -> List[Animation]:
        """Returns the animations of the definition"""
        return self.definition.animations

    @property
    def animation(self) -> Animation:
        """Returns the animation currently selected"""
        return self.animations[self.animation_index]

    @property
    def sprites(self) -> List[SpriteGraphic]:
        """Returns the sprites of the animation"""
        return self.animation.graphics

    @property
    def sprite(self) -> SpriteGraphic:
        """Returns the sprite graphic currently selected"""
        return self.sprites[self.sprite_index]

    @property
    def page(self) -> int:
        """Returns the current page of graphics inside the object"""
        return self.animation.page

    @page.setter
    def page(self, page: int) -> None:
        self.animation.page = page
        self.action_page(page)

    @property
    def size(self) -> Size:
        """Returns the current size of the object"""
        return self.animation.size

    @size.setter
    def size(self, size: Size) -> None:
        self.animation.size = size
        self.action_size(size)

    @property
    def palette(self) -> int:
        """Sets the sprite palette of the object"""
        return self.animation.palette

    @palette.setter
    def palette(self, palette: int) -> None:
        self.animation.palette = palette
        self.action_palette(palette)

    @property
    def graphic(self) -> int:
        """The graphic used for the sprite"""
        return self.sprite.graphic

    @graphic.setter
    def graphic(self, graphic: int) -> None:
        self.sprite.graphic = graphic
        self.action_graphic(graphic)

    @property
    def horizontal_mirror(self) -> bool:
        """Returns if the graphic is horizontally mirrored"""
        return self.sprite.horizontal_flip

    @horizontal_mirror.setter
    def horizontal_mirror(self, horizontal_mirror: bool) -> None:
        self.sprite.horizontal_flip = horizontal_mirror
        self.action_horizontal_mirror(horizontal_mirror)

    @property
    def vertical_mirror(self) -> bool:
        """Returns if the graphic is vertically mirrored"""
        return self.sprite.vertical_flip

    @vertical_mirror.setter
    def vertical_mirror(self, vertical_mirror: bool) -> None:
        self.sprite.vertical_flip = vertical_mirror
        self.action_vertical_mirror(vertical_mirror)

    @property
    def operation(self) -> ObjectOperation:
        """Returns the operation of the sprite"""
        return self.definition.operation

    @operation.setter
    def operation(self, operation: ObjectOperation) -> None:
        self.definition.operation = operation
        self.action_operation(operation)

    @property
    def hitbox(self) -> Rect:
        """Returns the hitbox of the object"""
        return self.definition.hitbox.object_detection_hitbox

    @hitbox.setter
    def hitbox(self, hitbox: Rect) -> None:
        self.definition.hitbox.object_detection_hitbox = hitbox
        self.action_hitbox(hitbox)

    @property
    def bounding_box(self) -> Rect:
        """Returns the bounding box of the object"""
        return self.definition.hitbox.block_detection_hitbox

    @bounding_box.setter
    def bounding_box(self, bounding_box: Rect) -> None:
        self.definition.hitbox.block_detection_hitbox = bounding_box
        self.action_bounding_box(bounding_box)

    def draw(
            self,
            painter: QPainter,
            pos: Position,
            size: Size,
            transparent: bool = False
    ) -> None:
        """
        Draws the Tile with a QPainter
        :param painter: The QPainter that will draw the image
        :param pos: The position to draw the image
        :param size: The size of the image to draw
        :param transparent: Masks out the background color
        :return: None
        """
        SpriteElement.from_animation(self.palette_group, self.animation).draw(painter, pos, size, transparent)




