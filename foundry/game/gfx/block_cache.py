"""Cache and draw ROM-backed SMB3 blocks for level and world-map views.

This module owns the shared block-rendering cache that sits between ROM-backed
graphics inputs and Qt painters. ``BlockCache`` memoizes decoded
:class:`~foundry.game.gfx.drawable.Block.Block` instances by block id, object
set, palette group, graphics set, and animation frame so repeated draws do not
reload palette, CHR, or TSA data. The module-level drawing helpers consume
already-decoded level-object or enemy-item layouts and emit painted pixels
through :class:`PySide6.QtGui.QPainter`.

The main inputs are SMB3 block ids plus the object-set, palette-group, and
graphics-set numbers that identify the ROM tables needed to decode a block.
The main outputs are cached
:class:`~foundry.game.gfx.drawable.Block.Block` objects and the corresponding
paint operations for level objects, enemy previews, and world-map tiles. Start
here when tracing how editor views turn object metadata into rendered 16x16
blocks, then follow the collaborators below for palette, graphics, and block
pixel assembly details.

See Also
--------
foundry.game.gfx.drawable.Block.Block
    Builds and draws the 16x16 block images cached by this module.
foundry.game.gfx.GraphicsSet.GraphicsSet
    Loads the CHR-backed graphics data reused across cached block requests.
foundry.game.gfx.Palette.load_palette_group
    Resolves the palette-group inputs that complete each cached block lookup.

Examples
--------
After a ROM is loaded, repeated requests with the same rendering inputs return
the cached block instance instead of decoding it again::

    >>> from foundry.game.gfx.block_cache import BlockCache
    >>> BlockCache.animation_frame = 0
    >>> first = BlockCache.block(0x24, 1, 0, 3)
    >>> second = BlockCache.block(0x24, 1, 0, 3)
    >>> first is second
    True

Animated requests keep separate cache entries per shared animation frame::

    >>> BlockCache.animation_frame = 0
    >>> frame0 = BlockCache.block(0x24, 1, 0, 3, animated=True)
    >>> BlockCache.next_frame()
    >>> frame1 = BlockCache.block(0x24, 1, 0, 3, animated=True)
    >>> frame0 is frame1
    False
"""

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
    """Cache rendered SMB3 blocks and their ROM-backed inputs.

    Level and world-map drawing repeatedly request the same 16x16 blocks for a
    given object set, palette group, graphics set, and animation frame. This
    cache keeps the decoded ``Block`` objects and the underlying palette,
    graphics, and TSA data together so renderers do not reread ROM tables for
    every draw call.

    Attributes
    ----------
    _block_cache : dict[BlockCacheKey, 'Block']
        Decoded blocks keyed by block id and rendering inputs.
    _graphics_set_cache : dict[GraphicsSetNo, 'GraphicsSet']
        Graphics sets loaded from CHR ROM.
    _palette_group_cache : dict[tuple[ObjectSetNo, PaletteGroupNo], 'PaletteGroup']
        Palette groups selected by object set and level header palette index.
    _tsa_data_cache : dict[ObjectSetNo, bytes]
        TSA byte tables loaded per object set.
    animation_frame : int
        Current animation frame used when callers request animated blocks.
    initialized : bool
        Whether cache state is valid for a loaded ROM.

    Examples
    --------
    Animated and non-animated lookups reuse different cache keys::

        >>> from foundry.game.gfx.block_cache import BlockCache
        >>> BlockCache.animation_frame = 0
        >>> frame0 = BlockCache.block(0x24, 1, 0, 3, animated=True)
        >>> stable = BlockCache.block(0x24, 1, 0, 3, animated=False)
        >>> BlockCache.next_frame()
        >>> frame1 = BlockCache.block(0x24, 1, 0, 3, animated=True)
        >>> stable_again = BlockCache.block(0x24, 1, 0, 3, animated=False)
        >>> frame0 is frame1, stable is stable_again
        (False, True)
    """

    _block_cache: dict[BlockCacheKey, "Block"] = {}
    _palette_group_cache: dict[tuple[ObjectSetNo, PaletteGroupNo], "PaletteGroup"] = {}
    _graphics_set_cache: dict[GraphicsSetNo, "GraphicsSet"] = {}
    _tsa_data_cache: dict[ObjectSetNo, bytes] = {}

    animation_frame: int = 0

    initialized = False

    @classmethod
    def clear_cache(cls):
        """Clear all cached blocks and ROM-derived rendering inputs.

        This is called when loading a different ROM or restoring graphics so no
        stale palette, CHR, or TSA data is reused.
        """
        cls._block_cache.clear()
        cls._palette_group_cache.clear()
        cls._graphics_set_cache.clear()
        cls._tsa_data_cache.clear()

    @classmethod
    def update(cls):
        """Mark the cache uninitialized when no ROM is loaded.

        This method only invalidates the initialized flag for the
        no-ROM case.
        """
        if not ROM.is_loaded():
            cls.initialized = False
            return

    @classmethod
    def next_frame(cls):
        """Advance the shared animation frame for cached block lookups.

        Animation frames wrap through the four-frame cycle used by cached
        animated block requests.
        """
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
        """Resolve one block-rendering request through the shared cache.

        Non-animated requests always use frame 0. Animated requests use the
        cache animation frame, which lets level views advance animated
        tiles without rebuilding static blocks.

        Parameters
        ----------
        block_id : BlockId
            SMB3 16x16 block id.
        object_set_no : ObjectSetNo
            Object set whose TSA data should be used.
        palette_group_no : PaletteGroupNo
            Level-header palette group index.
        graphics_set_no : GraphicsSetNo
            Graphics set whose CHR data should be used.
        animated : bool, optional
            Whether to include the cache animation frame in the cache key.

        Returns
        -------
        'Block'
            Cached block image.

        Examples
        --------
        Stable block requests always resolve through frame ``0``, while
        animated requests follow :attr:`animation_frame`::

            >>> from foundry.game.gfx.block_cache import BlockCache
            >>> BlockCache.animation_frame = 0
            >>> still = BlockCache.block(0x24, 1, 0, 3, animated=False)
            >>> animated0 = BlockCache.block(0x24, 1, 0, 3, animated=True)
            >>> BlockCache.next_frame()
            >>> still_again = BlockCache.block(0x24, 1, 0, 3, animated=False)
            >>> animated1 = BlockCache.block(0x24, 1, 0, 3, animated=True)
            >>> still is still_again, animated0 is animated1
            (True, False)
        """
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
        """Load or reuse the cached palette group for one object-set/palette pairing.

        Block rendering reuses palette groups heavily, so this helper centralizes
        palette-group cache population for the block cache.


        Parameters
        ----------
        object_set_no : ObjectSetNo
            Object set whose palette table should be read.
        palette_group_no : PaletteGroupNo
            Level-header palette group index.

        Returns
        -------
        'PaletteGroup'
            Palette group used for the cached block.
        """
        key = (object_set_no, palette_group_no)

        if key not in cls._palette_group_cache:
            cls._palette_group_cache[key] = load_palette_group(object_set_no, palette_group_no)

        return cls._palette_group_cache[key]

    @classmethod
    def _gs(cls, graphics_set_no: GraphicsSetNo) -> "GraphicsSet":
        """Load or reuse the cached graphics set for block rendering.

        This keeps CHR decoding aligned with the block cache so repeated block
        requests reuse one graphics-set instance per graphics-set number.


        Parameters
        ----------
        graphics_set_no : GraphicsSetNo
            Graphics set number to load.

        Returns
        -------
        'GraphicsSet'
            Graphics set used for the cached block.
        """
        if graphics_set_no not in cls._graphics_set_cache:
            cls._graphics_set_cache[graphics_set_no] = GraphicsSet.from_number(graphics_set_no)

        return cls._graphics_set_cache[graphics_set_no]

    @classmethod
    def _tsa(cls, object_set_no: ObjectSetNo) -> bytes:
        """Load or reuse cached TSA data for an object set.

        TSA bytes are ROM-derived block-layout tables, so this helper is the
        block cache's bridge from object-set number to decoded tile layout data.


        Parameters
        ----------
        object_set_no : ObjectSetNo
            Object set whose TSA table should be read.

        Returns
        -------
        bytes
            Tile set array used for the cached block.
        """
        if object_set_no not in cls._tsa_data_cache:
            cls._tsa_data_cache[object_set_no] = ROM.get_tsa_data(object_set_no)

        return cls._tsa_data_cache[object_set_no]


def draw_level_object(obj: "LevelObject", painter: QPainter, block_length: int, transparent: bool, animated: bool):
    """Draw a level object from its rendered block ids.

    The object's renderer has already expanded its SMB3 object definition into a
    rectangular list of block ids. This function skips blank sentinels and draws
    each block through ``BlockCache`` using the object's palette and graphics
    context.

    Parameters
    ----------
    obj : 'LevelObject'
        Level object with rendered block metadata.
    painter : QPainter
        Painter used to render the object or view.
    block_length : int
        Rendered block size in pixels.
    transparent : bool
        Whether the object should be drawn transparently.
    animated : bool
        Whether animated block frames should be used.
    """
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
    """Draw an enemy or item with cached block images.

    This keeps enemy preview rendering consistent between in-level drawing, the object toolbar,
    and object dropdown previews.

    Parameters
    ----------
    enemy_item : 'EnemyItem'
        Enemy or item object to draw.
    painter : QPainter
        Painter used to render the object or view.
    block_length : int
        Rendered block size in pixels.
    use_offsets : bool, optional
        Whether to apply in-level enemy handle offsets while drawing.
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
    """Draw one cached block at a level-grid position.

    Coordinates are expressed in block units and scaled by ``block_length`` for
    the Qt painter.

    Parameters
    ----------
    painter : QPainter
        Painter used to render the object or view.
    block_index : BlockId
        Index of the block.
    object_set_no : ObjectSetNo
        Object set whose TSA data should be used.
    palette_group_no : PaletteGroupNo
        Level-header palette group index.
    graphics_set_no : GraphicsSetNo
        Graphics set whose CHR data should be used.
    x : int
        Horizontal coordinate.
    y : int
        Vertical coordinate.
    block_length : int
        Rendered block size in pixels.
    transparent : bool
        Whether the object should be drawn transparently.
    selected : bool
        Whether the object should be drawn as selected.
    animated : bool, optional
        Whether animated block frames should be used.
    """
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
    """Build a block from explicit palette, graphics, and TSA inputs.

    Parameters
    ----------
    block_index : BlockId
        SMB3 16x16 block id.
    palette_group : 'PaletteGroup'
        Palette group used for drawing the object.
    graphics_set : 'GraphicsSet'
        Graphics set used to draw object previews.
    tsa_data : bytes
        Object-set TSA data used to resolve the block's four tiles.
    frame : int, optional
        Animation frame to use for the graphics set.

    Returns
    -------
    'Block'
        Decoded block.
    """
    block = Block(block_index, palette_group, graphics_set, tsa_data, frame)

    return block


def get_worldmap_tile(block_index: int, palette_index=0, animated=False) -> "Block":
    """Return a world-map tile block.

    Parameters
    ----------
    block_index : int
        World-map block id.
    palette_index : int, optional
        World-map palette row index.
    animated : bool, optional
        Whether animated block frames should be used.

    Returns
    -------
    'Block'
        Cached world-map block.
    """
    return BlockCache.block(block_index, WORLD_MAP_OBJECT_SET, palette_index, 0, animated)
