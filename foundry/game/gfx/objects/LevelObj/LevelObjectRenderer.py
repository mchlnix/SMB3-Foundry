from typing import List

from PySide2.QtCore import QRect
from PySide2.QtGui import QImage, QPainter

from foundry.game.ObjectSet import ObjectSet
from foundry.game.ObjectDefinitions import GeneratorType, EndType
from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx.Palette import PaletteGroup

from foundry.game.gfx.objects.ObjectLike import ObjectLike, EXPANDS_HORIZ, EXPANDS_VERT
from foundry.game.gfx.objects.LevelObj.AbstractLevelObject import AbstractLevelObject
from foundry.game.gfx.objects.LevelObj.LevelObject import LevelObject
from foundry.game.gfx.objects.LevelObj.BlockGroupRenderer import BlockGroupRenderer
from foundry.game.gfx.objects.LevelObj.render import render


class LevelObjectRenderer(AbstractLevelObject):
    """
    A LevelObject that handles drawing the object to the screen
    """

    SKY = 0
    GROUND = 27

    def __init__(
        self,
        level_object: LevelObject,
        palette_group: PaletteGroup,
        graphics_set: GraphicsSet,
        objects_ref: List[ObjectLike],
        index_into_level: int,
        is_vertical: bool,
        size_minimal: bool = False,
    ):
        self.level_object = level_object  # Intentionally miss super init as our LevelObject is already initialized
        self.palette_group = palette_group
        self.graphics_set = graphics_set
        self.objects_ref = objects_ref
        self.index_in_level = index_into_level
        self.is_vertical = is_vertical
        self.selected = False
        self.size_minimal = size_minimal
        if self.size_minimal:
            self.ground_level = 0
        else:
            self.ground_level = self.GROUND
        self.has_updated = True
        self._block_group_renderer = BlockGroupRenderer(
            self.rect, [], self.palette_group, self.graphics_set, self.object_set.number
        )
        self._blocks = None

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}({self.level_object}, {self.palette_group}, {self.graphics_set},"
            f"{self.objects_ref}, {self.index_in_level}, {self.is_vertical}, {self.size_minimal})"
        )

    @property
    def selected(self) -> bool:
        return self._selected

    @selected.setter
    def selected(self, selected: bool) -> None:
        self._selected = selected
        self.has_updated = True

    @property
    def object_set(self) -> ObjectSet:
        return self.level_object.object_set

    @object_set.setter
    def object_set(self, object_set: ObjectSet) -> None:
        self.level_object.object_set = object_set
        self.has_updated = True

    @property
    def domain(self) -> int:
        return self.level_object.domain

    @domain.setter
    def domain(self, domain: int) -> None:
        self.level_object.domain = domain
        self.has_updated = True

    @property
    def index(self) -> int:
        return self.level_object.index

    @index.setter
    def index(self, index: int) -> None:
        self.level_object.index = index
        self.has_updated = True

    @property
    def width(self) -> int:
        return self.level_object.width

    @width.setter
    def width(self, width: int) -> None:
        self.level_object.width = width
        self.has_updated = True

    @property
    def height(self) -> int:
        return self.level_object.height

    @height.setter
    def height(self, height):
        self.level_object.height = height
        self.has_updated = True

    @property
    def x(self) -> int:
        return self.level_object.x

    @x.setter
    def x(self, x: int) -> None:
        self.level_object.x = x
        self.has_updated = True

    @property
    def y(self) -> int:
        return self.level_object.y

    @y.setter
    def y(self, y: int) -> None:
        self.level_object.y = y
        self.has_updated = True

    @property
    def bytes(self) -> int:
        return self.level_object.bytes

    @property
    def expansion(self):
        return self.level_object.expansion

    @property
    def index_expansion(self):
        return self.level_object.index_expansion

    def to_bytes(self) -> bytearray:
        return self.level_object.to_bytes(self.is_vertical)

    @property
    def block_group_renderer(self) -> BlockGroupRenderer:
        """
        The object in charge of rendering the actual generator
        """
        if self.has_updated:
            self._blocks = None  # Flush the blocks in the event that the generator changed
            self.update_block_group_renderer()
        self.has_updated = False
        return self._block_group_renderer

    @property
    def blocks(self) -> List[int]:
        """
        The blocks specified by the generator
        """
        if self._blocks is None:  # Try to avoid recreating list unless needed
            self._blocks = [int(block) for block in self.object_set.get_definition_of(self.type).rom_object_design]
        return self._blocks

    def draw(self, painter: QPainter, block_length, transparent):
        """
        Draws the LevelObject onto the screen according with the BlockGroupRenderer
        :param painter: The painter to draw
        :param block_length: The size of a given block in units of 16
        :param transparent: If the block is transparent
        """
        self.block_group_renderer.draw(painter, block_length, transparent)

    def as_image(self) -> QImage:
        """
        Makes a picture of the LevelObject according with the BlockGroupRenderer
        :return: a QImage of the LevelObject
        """
        return self.block_group_renderer.as_image()

    def update_block_group_renderer(self):
        """
        Updates the BlockGroupRenderer to utilize the new blocks and rect determined by the render function
        """
        primary_len = self.index & 0x0F
        if self.index <= 0x0F:
            primary_len, secondary_len = 1, 0  # Single Block
        if self.bytes == 4 and self.index_expansion == EXPANDS_HORIZ:
            secondary_len, primary_len = self.height, self.width
        elif self.bytes == 4 and self.index_expansion == EXPANDS_VERT:
            secondary_len, primary_len = self.height, self.width
        elif self.index_expansion == EXPANDS_VERT:
            secondary_len, primary_len = self.width, self.height
        else:
            secondary_len = 0

        rect: QRect
        rect, blocks = render(
            self.object_set.get_definition_of(self.type).description,
            self.object_set,
            self.objects_ref,
            self.domain,
            self.index,
            EndType(self.object_set.get_definition_of(self.type).ending),
            self.index <= 0x0F,
            self.bytes == 4,
            self.index_in_level,
            GeneratorType(self.orientation),
            self.x,
            self.y,
            primary_len,
            secondary_len,
            self.object_set.get_definition_of(self.type).bmp_width,
            self.object_set.get_definition_of(self.type).bmp_height,
            self.ground_level,
            -1,
            self.blocks,
        )

        self._block_group_renderer.selected = self.selected  # Update if selected
        self._block_group_renderer.rect = ((rect.x(), rect.y()), (rect.width(), rect.height()))
        self._block_group_renderer.blocks = blocks
