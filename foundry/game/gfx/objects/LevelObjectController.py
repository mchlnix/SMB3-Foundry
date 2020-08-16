from typing import List, Optional, Tuple, Union
from abc import ABC, abstractmethod

from PySide2.QtGui import QImage, QPainter
from foundry.game.File import ROM

from foundry.game.ObjectDefinitions import (
    DESERT_PIPE_BOX, DIAG_DOWN_LEFT, DIAG_DOWN_RIGHT, DIAG_UP_RIGHT, DIAG_WEIRD, ENDING, HORIZONTAL, HORIZONTAL_2,
    HORIZ_TO_GROUND, PYRAMID_2, PYRAMID_TO_GROUND, SINGLE_BLOCK_OBJECT, TO_THE_SKY, VERTICAL, UPWARD_PIPE,
    DOWNWARD_PIPE, RIGHTWARD_PIPE, LEFTWARD_PIPE, DIAG_DOWN_RIGHT_30, DIAG_DOWN_LEFT_30, HORIZONTAL_WITH_TOP,
    HORIZONTAL_WITH_SIDE, VERTICAL_WITH_TOP, VERTICAL_WITH_ALL_SIDES, HORIZTONAL_WITH_ALL_SIDES,
    VERTICAL_WITH_TOP_AND_BOTTOM, DIAG_DOWN_LEFT_60, DIAG_DOWN_RIGHT_60, HORIZONTAL_WITH_BOTTOM, DIAG_UP_LEFT,
    DIAG_UP_RIGHT_30, VERTICAL_WITH_DOUBLE_TOP, VERTICAL_WITH_BOTTOM, HORIZONTAL_FIVE_BYTE, HORIZONTAL_BACKGROUND_FILL,
    DIAG_UP_Left_30, HORIZ_TO_GROUND_PLAINS, BUSH_PREFAB, HORIZ_FLOATING_PLATFORM, FORTRESS_PILLARS
)

from foundry.game.ObjectSet import ObjectSet
from foundry.game.gfx.PatternTableHandler import PatternTableHandler as PatternTable
from foundry.game.gfx.objects.ObjectLike import ObjectLike
from foundry.game.gfx.objects.LevelObject import LevelObject, BlockGenerator
from foundry.game.gfx.objects.LevelObjects import (
    LevelObjectToSky, LevelObjectDesertPipeBox, LevelObjectDiagnalDownLeft45, LevelObjectDiagnalDownRight45,
    LevelObjectDiagnalUpRight45, LevelObjectDiagnalWeird45, LevelObjectPyramidToGround, LevelObjectEndingBackground,
    LevelObjectVertical, LevelObjectHorizontal, LevelObjectHorizontalToGround, LevelObjectHorizontalAlt,
    SingleBlock, LevelObjectUpwardPipe, LevelObjectDownwardPipe, LevelObjectRightwardPipe, LevelObjectLeftwardPipe,
    LevelObjectDiagnalDownRight30, LevelObjectDiagnalDownLeft30, LevelObjectHorizontalWithTop,
    LevelObjectHorizontalWithSides, LevelObjectVerticalWithTop, LevelObjectHorizontalWithAllSides,
    LevelObjectVerticalWithAllSides, LevelObjectVerticalWithTopAndBottom, LevelObjectDiagnalDownLeft60,
    LevelObjectDiagnalDownRight60, LevelObjectHorizontalWithBottom, LevelObjectDiagnalUpLeft45,
    LevelObjectDiagnalUpRight30, LevelObjectVerticalWithDoubleTop, LevelObjectVerticalWithBottom,
    LevelObjectHorizontal5Byte, LevelObjectFillBackgroundHorizontalLevel, LevelObjectDiagnalUpLeft30,
    LevelObjectPlainsPlatformToGround, LevelObjectBushPrefab, LevelObjectPlainsPlatformFloating,
    LevelObjectFortressPillars
)

from foundry.core.geometry.Size.Size import Size
from foundry.game.Position import Position


class LevelObjectController(ObjectLike):
    def __init__(
            self,
            object_set: ObjectSet,
            palette_group,
            pattern_table: PatternTable,
            objects_ref: List["LevelObjectController"],
            is_vertical: bool,
            domain: int,
            index: int,
            overflow: int,
            position: Position,
            size: Size,
            object_factory_idx: int,
            render: bool = True
    ):
        self.render = render
        self._object_set, self._palette_group = object_set, palette_group
        self._pattern_table, self._objects_ref, self._vertical_level = pattern_table, objects_ref, is_vertical
        self._domain, self._index, self._pos = domain, index, position
        self._size, self._overflow = size, overflow
        self._object_factory_idx = object_factory_idx

        self._selected = False

        self.level_object = self._level_object()

    @classmethod
    def from_data(cls, data: bytearray, object_set: ObjectSet, palette_group, pattern_table: PatternTable,
                  objects_ref: List["LevelObject"], is_vertical: bool, object_factory_idx=0, render: bool = True):
        bg = BlockGenerator.from_bytes(object_set, data, is_vertical)
        domain, index, position, size, overflow = bg.domain, bg.index, bg.pos, bg.size, bg.overflow
        return cls(
            object_set,
            palette_group,
            pattern_table,
            objects_ref,
            is_vertical,
            domain,
            index,
            overflow,
            position,
            size,
            object_factory_idx,
            render
        )

    def get_blocks_and_positions(self):
        return self.level_object.get_blocks_and_positions()

    def icon(self):
        return self.level_object.icon()

    def to_asm6(self):
        return self.level_object.to_asm6()

    @property
    def bytes(self):
        return self.level_object.bytes

    @property
    def overflow(self):
        return self.level_object.overflow

    @property
    def size(self):
        return self.level_object.size

    @property
    def index_in_level(self):
        return self.level_object.index_in_level

    @property
    def index(self):
        return self.level_object.index

    @property
    def obj_index(self):
        return self.level_object.index

    @property
    def domain(self):
        return self.level_object.domain

    @property
    def type(self):
        return self.level_object.type

    def properties(self):
        return self.level_object.properties()

    def change_type(self, new_type):
        if self._index <= 0x10 and not new_type:
            value = 1
        else:
            self._index = self._index // 0x10 * 0x10
            value = 0x10

        if not new_type:
            value *= -1

        new_type = self._index + value

        if 0 < new_type and 0 < self._domain:
            new_domain = self._domain - 1
            new_type = 0xF0
        elif 0xFF < new_type and 7 > self.domain:
            new_domain = self._domain + 1
            new_type = 0x00
        else:
            new_type = min(0xFF, new_type)
            new_type = max(0, new_type)

            new_domain = self._domain

        self._domain = new_domain
        self._level_object()

    def get_rect(self, block_length=1):
        """Scales the rect to the correct dimensions"""
        return self.level_object.get_rect(block_length)

    @property
    def palette_group(self):
        return self.level_object.palette_group

    @property
    def pattern_table(self):
        return self.level_object.pattern_table

    @property
    def objects_ref(self):
        return self.level_object.objects_ref

    @property
    def rendered_blocks(self):
        return self.level_object.rendered_blocks

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        self.level_object.selected = value
        self._selected = value

    @property
    def y_pos(self):
        return self.level_object.pos.y

    @y_pos.setter
    def y_pos(self, y: int):
        self.level_object.pos.y = y

    @property
    def x_pos(self):
        return self.level_object.pos.x

    @x_pos.setter
    def x_pos(self, x: int):
        self.level_object.pos.x = x

    @property
    def height_len(self):
        return self.level_object.size.height

    @height_len.setter
    def height_len(self, value):
        self.level_object.size.height = value

    @property
    def length(self):
        return self.level_object.size.width

    @length.setter
    def length(self, value):
        if not self.is_4byte and not self.is_single_block:
            self.level_object.index &= 0xF0
            self.level_object.index |= value & 0x0F
        self.level_object.size.width = value

    @property
    def is_4byte(self):
        """Returns if the object takes 4 bytes"""
        return self._is_4byte(self.level_object.object_set, self.type)

    @staticmethod
    def _is_4byte(object_set, type):
        """Returns if an object is 4 bytes from the object set from a given type"""
        return object_set.get_definition_of(type).is_4byte

    @property
    def is_single_block(self):
        """Returns if a block is a single block"""
        return self._is_single_block(self.index)

    @staticmethod
    def _is_single_block(index):
        """Returns if the index is in the range for single blocks"""
        return index <= 0x0F

    @property
    def index(self):
        return self.level_object.index

    @property
    def domain_offset(self):
        """Returns the offset for type of a domain"""
        return self._domain_offset(self.level_object.domain)

    @staticmethod
    def _domain_offset(domain):
        """Returns the correct offset for a type from a given domain"""
        return domain * 0x1F

    @property
    def type(self):
        """Returns the type of the block"""
        return self._type(self.level_object.index, self.level_object.domain)

    @staticmethod
    def _type(index, domain):
        """Returns the type of the block from a given index and domain
        For every domain there is 16 single-block types and 15 multi-block types
        Single-block objects exist at the beginning of every domain
        Multi-block objects exist in the remainder, being split into 16 block indexes
        """
        if LevelObjectController._is_single_block(index):
            return index + LevelObjectController._domain_offset(domain)
        else:
            return (index >> 4) + LevelObjectController._domain_offset(domain) + 15

    @property
    def block_cache(self):
        return self.level_object.block_cache

    @property
    def rendered_width(self):
        return self.level_object.rendered_size.width

    @rendered_width.setter
    def rendered_width(self, width):
        self.level_object.rendered_size.width = width

    @property
    def rendered_height(self):
        return self.level_object.rendered_size.height

    @rendered_height.setter
    def rendered_height(self, height):
        self.level_object.rendered_size.height = height

    @property
    def rendered_base_x(self):
        return self.level_object.rendered_position.x

    @rendered_base_x.setter
    def rendered_base_x(self, pos):
        self.level_object.rendered_position.x = pos

    @property
    def rendered_base_y(self):
        return self.level_object.rendered_position.y

    @rendered_base_y.setter
    def rendered_base_y(self, pos):
        self.level_object.rendered_position.y = pos

    @property
    def secondary_length(self):
        return self.level_object.height_len

    @secondary_length.setter
    def secondary_length(self, len):
        self.level_object.height_len = len

    @property
    def x_position(self):
        return self.level_object.x_pos

    @x_position.setter
    def x_position(self, pos):
        self.level_object.x_pos = pos

    @property
    def y_position(self):
        return self.level_object.y_pos

    @y_position.setter
    def y_position(self, pos):
        self.level_object.y_pos = pos

    @property
    def tsa_data(self):
        return ROM.get_tsa_data(self.level_object.object_set.object_set_number)

    @property
    def width(self):
        return self.level_object.bmp.size.width

    @property
    def height(self):
        return self.level_object.bmp.size.height

    @property
    def bmp(self):
        return self.level_object.object_set.get_definition_of(self.type).bmp

    @property
    def orientation(self):
        return self.level_object.object_set.get_definition_of(self.type).orientation

    @property
    def _orientation(self):
        # Get the hidden type, as the level object does not exist yet
        return self._object_set.get_definition_of(self._type(self._index, self._domain)).orientation

    @property
    def ending(self):
        return self.level_object.object_set.get_definition_of(self.type).ending

    @property
    def description(self):
        return self.level_object.object_set.get_definition_of(self.type).description

    @property
    def blocks(self):
        object_data = self.level_object.object_set.get_definition_of(self.type).rom_object_design
        return [int(block) for block in object_data]

    def render(self):
        self.level_object.render()

    def draw(self, painter: QPainter, block_length, transparent):
        self.level_object.draw(painter, block_length, transparent)

    def set_position(self, pos: Position):
        self.level_object.set_position(pos)

    def move_by(self, dx, dy):
        self.level_object.move_by(Position(dx, dy))

    def get_position(self):
        return self.level_object.get_position()

    def expands(self):
        return self.level_object.expands

    def primary_expansion(self):
        return self.level_object.primary_expansion

    def resize_x(self, x: int):
        self.level_object.resize_x(x)

    def resize_y(self, y: int):
        self.level_object.resize_y(y)

    def resize_by(self, dx: int, dy: int):
        self.level_object.resize_by(dx, dy)

    def increment_type(self):
        self.level_object.increment_type()

    def decrement_type(self):
        self.level_object.decrement_type()

    def __contains__(self, item: Tuple[int, int]) -> bool:
        return self.level_object.__contains__(item)

    def point_in(self, x: int, y: int) -> bool:
        return self.level_object.point_in(x, y)

    def get_status_info(self) -> List[tuple]:
        return self.level_object.get_status_info()

    def display_size(self, zoom_factor: int = 1):
        return self.level_object.display_size(zoom_factor)

    def as_image(self) -> QImage:
        return self.level_object.as_image()

    def to_bytes(self) -> bytearray:
        return self.level_object.to_bytes()

    def __repr__(self) -> str:
        return self.level_object.__repr__()

    def __eq__(self, other):
        return self.level_object.__eq__(other)

    def __lt__(self, other):
        return self.level_object.__lt__(other)

    LEVEL_OBJECTS = {
        TO_THE_SKY: LevelObjectToSky,
        DESERT_PIPE_BOX: LevelObjectDesertPipeBox,
        DIAG_DOWN_LEFT: LevelObjectDiagnalDownLeft45,
        DIAG_DOWN_RIGHT: LevelObjectDiagnalDownRight45,
        DIAG_UP_RIGHT: LevelObjectDiagnalUpRight45,
        DIAG_WEIRD: LevelObjectDiagnalWeird45,
        PYRAMID_TO_GROUND: LevelObjectPyramidToGround,
        PYRAMID_2: LevelObjectPyramidToGround,
        ENDING: LevelObjectEndingBackground,
        VERTICAL: LevelObjectVertical,
        HORIZONTAL: LevelObjectHorizontal,
        HORIZ_TO_GROUND: LevelObjectHorizontalToGround,
        HORIZONTAL_2: LevelObjectHorizontalAlt,
        SINGLE_BLOCK_OBJECT: SingleBlock,
        UPWARD_PIPE: LevelObjectUpwardPipe,
        DOWNWARD_PIPE: LevelObjectDownwardPipe,
        RIGHTWARD_PIPE: LevelObjectRightwardPipe,
        LEFTWARD_PIPE: LevelObjectLeftwardPipe,
        DIAG_DOWN_RIGHT_30: LevelObjectDiagnalDownRight30,
        DIAG_DOWN_LEFT_30: LevelObjectDiagnalDownLeft30,
        HORIZONTAL_WITH_TOP: LevelObjectHorizontalWithTop,
        HORIZONTAL_WITH_SIDE: LevelObjectHorizontalWithSides,
        VERTICAL_WITH_TOP: LevelObjectVerticalWithTop,
        VERTICAL_WITH_ALL_SIDES: LevelObjectVerticalWithAllSides,
        HORIZTONAL_WITH_ALL_SIDES: LevelObjectHorizontalWithAllSides,
        VERTICAL_WITH_TOP_AND_BOTTOM: LevelObjectVerticalWithTopAndBottom,
        DIAG_DOWN_LEFT_60: LevelObjectDiagnalDownLeft60,
        DIAG_DOWN_RIGHT_60: LevelObjectDiagnalDownRight60,
        HORIZONTAL_WITH_BOTTOM: LevelObjectHorizontalWithBottom,
        DIAG_UP_LEFT: LevelObjectDiagnalUpLeft45,
        DIAG_UP_RIGHT_30: LevelObjectDiagnalUpRight30,
        VERTICAL_WITH_DOUBLE_TOP: LevelObjectVerticalWithDoubleTop,
        VERTICAL_WITH_BOTTOM: LevelObjectVerticalWithBottom,
        HORIZONTAL_FIVE_BYTE: LevelObjectHorizontal5Byte,
        HORIZONTAL_BACKGROUND_FILL: LevelObjectFillBackgroundHorizontalLevel,
        DIAG_UP_Left_30: LevelObjectDiagnalUpLeft30,
        HORIZ_TO_GROUND_PLAINS: LevelObjectPlainsPlatformToGround,
        BUSH_PREFAB: LevelObjectBushPrefab,
        HORIZ_FLOATING_PLATFORM: LevelObjectPlainsPlatformFloating,
        FORTRESS_PILLARS: LevelObjectFortressPillars
    }

    def _level_object(self):
        """
        Make the level object that we are representing
        :return: A level object
        """
        level_kwargs = {
            "object_set": self._object_set,
            "palette_group": self._palette_group,
            "pattern_table": self._pattern_table,
            "objects_ref": self._objects_ref,
            "is_vertical": self._vertical_level,
            "domain": self._domain,
            "index": self._index,
            "overflow": self._overflow,
            "position": self._pos,
            "size": self._size,
            "object_factory_idx": self._object_factory_idx,
            "render": self.render
        }
        return self.LEVEL_OBJECTS[self._orientation](**level_kwargs)



