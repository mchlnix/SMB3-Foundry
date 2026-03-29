from typing import TYPE_CHECKING

from PySide6.QtGui import QColor, QPainter, Qt

from foundry.game.File import ROM
from foundry.game.gfx.drawable import MASK_COLOR, apply_selection_overlay
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx.Palette import PaletteGroup, load_palette_group
from foundry.game.ObjectDefinitions import (
    enemy_handle_x,
    enemy_handle_x2,
    enemy_handle_y,
)
from smb3parse.constants import WORLD_MAP_OBJECT_SET

if TYPE_CHECKING:
    from foundry.game.gfx.objects.in_level.enemy_item import EnemyItem
    from foundry.game.gfx.objects.in_level.level_object import LevelObject

ANIMATION_FRAME_COUNT = 4

BlockId = int
GraphicsSetNo = int
ObjectSetNo = int
PaletteGroupNo = int
AnimationFrame = int

BlockCacheKey = tuple[BlockId, ObjectSetNo, PaletteGroupNo, GraphicsSetNo, AnimationFrame]


# not all objects provide a block index for a blank block
BLANK_BLOCK_ID: BlockId = -1


# TODO animated sprites in level view doesn't work
# TODO what to do about tiles? Can they be separated from QT code?
class BlockCache:
    _block_cache: dict[BlockCacheKey, "Block"] = {}
    _palette_group_cache: dict[tuple[ObjectSetNo, PaletteGroupNo], "PaletteGroup"] = {}
    _graphics_set_cache: dict[GraphicsSetNo, "GraphicsSet"] = {}
    _tsa_data_cache: dict[ObjectSetNo, bytes] = {}

    animation_frame: int = 0

    initialized = False

    @classmethod
    def clear_cache(cls):
        cls._block_cache.clear()
        cls._palette_group_cache.clear()
        cls._graphics_set_cache.clear()
        cls._tsa_data_cache.clear()

    @classmethod
    def update(cls):
        if not ROM.is_loaded():
            cls.initialized = False
            return

    @classmethod
    def next_frame(cls):
        cls.animation_frame += 1
        cls.animation_frame %= ANIMATION_FRAME_COUNT

    @classmethod
    def block(
        cls,
        block_id: BlockId,
        object_set_no: ObjectSetNo,
        palette_group_no: PaletteGroupNo,
        graphics_set_no: GraphicsSetNo,
        animated=False,
    ) -> "Block":
        if animated:
            frame = cls.animation_frame
        else:
            frame = 0

        key = (block_id, object_set_no, palette_group_no, graphics_set_no, frame)

        if key not in cls._block_cache:
            cls._block_cache[key] = get_block(
                block_id,
                cls._pg(object_set_no, palette_group_no),
                cls._gs(graphics_set_no),
                cls._tsa(object_set_no),
                frame,
            )

        return cls._block_cache[key]

    @classmethod
    def _pg(cls, object_set_no: ObjectSetNo, palette_group_no: PaletteGroupNo) -> "PaletteGroup":
        key = (object_set_no, palette_group_no)

        if key not in cls._palette_group_cache:
            cls._palette_group_cache[key] = load_palette_group(object_set_no, palette_group_no)

        return cls._palette_group_cache[key]

    @classmethod
    def _gs(cls, graphics_set_no: GraphicsSetNo) -> "GraphicsSet":
        if graphics_set_no not in cls._graphics_set_cache:
            cls._graphics_set_cache[graphics_set_no] = GraphicsSet.from_number(graphics_set_no)

        return cls._graphics_set_cache[graphics_set_no]

    @classmethod
    def _tsa(cls, object_set_no: ObjectSetNo) -> bytes:
        if object_set_no not in cls._tsa_data_cache:
            cls._tsa_data_cache[object_set_no] = ROM.get_tsa_data(object_set_no)

        return cls._tsa_data_cache[object_set_no]


def draw_level_object(obj: "LevelObject", painter: QPainter, block_length: int, transparent: bool, animated: bool):
    for index, block_index in enumerate(obj.rendered_blocks):
        if block_index == BLANK_BLOCK_ID:
            continue

        x = obj.rendered_base_x + index % obj.rendered_width
        y = obj.rendered_base_y + index // obj.rendered_width

        draw_block(
            painter,
            block_index,
            obj.object_set.number,
            obj.palette_group.index,
            obj.graphics_set.number,
            x,
            y,
            block_length,
            transparent,
            obj.selected,
            animated,
        )


def draw_enemy_item(enemy_item: "EnemyItem", painter: QPainter, block_length: int, use_offsets: bool = True):
    """

    :param enemy_item:
    :param painter:
    :param block_length:
    :param bool use_offsets: Whether to use the additional offsets. Necessary when drawing in level, but not when
        rendering in the object toolbar, or in the object dropdown.
    """
    for i, image in enumerate(enemy_item.blocks):
        x = enemy_item.x_position + (i % enemy_item.width)
        y = enemy_item.y_position + (i // enemy_item.width)

        if use_offsets:
            x_offset = enemy_handle_x[enemy_item.obj_index]
            y_offset = enemy_handle_y[enemy_item.obj_index]
        else:
            x_offset = enemy_handle_x2[enemy_item.obj_index]
            y_offset = 0

        x += x_offset
        y += y_offset

        block = image.copy()

        mask = block.createMaskFromColor(QColor(*MASK_COLOR).rgb(), Qt.MaskMode.MaskOutColor)
        block.setAlphaChannel(mask)

        if enemy_item.selected:
            apply_selection_overlay(block, mask)

        if block_length != Block.SIDE_LENGTH:
            block = block.scaled(block_length, block_length)

        painter.drawImage(x * block_length, y * block_length, block)


def draw_block(
    painter: QPainter,
    block_index: BlockId,
    object_set_no: ObjectSetNo,
    palette_group_no: PaletteGroupNo,
    graphics_set_no: GraphicsSetNo,
    x: int,
    y: int,
    block_length: int,
    transparent: bool,
    selected: bool,
    animated=False,
):
    block = BlockCache.block(block_index, object_set_no, palette_group_no, graphics_set_no, animated)

    block.draw(
        painter,
        x * block_length,
        y * block_length,
        block_length=block_length,
        selected=selected,
        transparent=transparent,
    )


# TODO Can I get rid of this as a public function?
def get_block(
    block_index: BlockId,
    palette_group: "PaletteGroup",
    graphics_set: "GraphicsSet",
    tsa_data: bytes,
    frame: int = 0,
) -> "Block":
    block = Block(block_index, palette_group, graphics_set, tsa_data, frame)

    return block


def get_worldmap_tile(block_index: int, palette_index=0, animated=False) -> "Block":
    return BlockCache.block(block_index, WORLD_MAP_OBJECT_SET, palette_index, 0, animated)
