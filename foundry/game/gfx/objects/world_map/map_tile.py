"""World-map terrain tiles backed by decoded blocks and ROM positions.

This module wraps one decoded world-map ``Block`` together with its map
position so overworld terrain editing can use the same selection, drawing, and
type-change workflows as other world-map objects.

See Also
--------
foundry.game.gfx.drawable.Block
    Supplies the decoded block images drawn by ``MapTile``.
foundry.game.gfx.objects.world_map.map_object
    Defines the shared position and drawing contract for world-map objects.
"""

from foundry.game.gfx.block_cache import get_worldmap_tile
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects.world_map.map_object import MapObject
from smb3parse.constants import TILE_NAMES
from smb3parse.data_points import Position
from smb3parse.levels import WORLD_MAP_SCREEN_SIZE, WORLD_MAP_SCREEN_WIDTH


class MapTile(MapObject):
    """Model one editable world-map terrain tile.

    A map tile combines a world-map position with a decoded ``Block`` so the
    editor can draw, sort, replace, and serialize overworld terrain without
    juggling raw tile indexes and positions separately.

    Parameters
    ----------
    block : Block
        Block or block index being rendered or inspected.
    pos : Position
        World-map position for the tile.

    Attributes
    ----------
    block : Block
        Decoded block used for world-map drawing and type changes.
    name : str
        Display name derived from the tile index.
    pos : Position
        World-map position encoded in the tile data stream.
    type : int
        Tile index currently represented by ``block``.

    Notes
    -----
    The data flow is position plus block index -> decoded ``Block`` -> map tile
    object -> overworld drawing and sorting. Type changes rebuild the decoded
    block while preserving the map coordinate record.

    Examples
    --------
    Overworld editing usually treats this wrapper as decoded block plus ROM
    position -> ``MapTile`` -> shared draw, selection, and sorting tools::

        tile = MapTile(block, pos)
        tile.get_position()
        tile.type

    The important shape is that the tile keeps ``Position`` and the decoded
    ``Block`` together, so world-map code can redraw and reorder terrain
    without carrying separate coordinate and tile-id values through each tool.
    """

    def __init__(self, block: Block, pos: Position):
        """Wrap a decoded overworld block at a world-map position.

        The tile keeps the decoded ``Block`` and ROM-backed ``Position``
        together so edit-time drawing and type changes stay aligned with the
        same map coordinate record.

        Parameters
        ----------
        block : Block
            Decoded world-map block used for drawing and tile replacement.
        pos : Position
            ROM-backed map position for the tile.
        """
        super(MapTile, self).__init__()

        self.pos = pos

        # TODO MapTile should not save it's block and definitely not get one supplied from the outside.
        # TODO Use BlockCache for animation
        self.block = block
        self.type = self.block.index

    @property
    def name(self):
        """Editor-facing name for the decoded tile.

        The value comes from SMB3's known tile-name table when available and
        falls back to the raw tile id otherwise, so the label always matches
        the block presently being drawn and the world-map UI reads the same
        tile state used by draw and type-change workflows.

        Returns
        -------
        str
            Constant-backed tile name or the raw type in hexadecimal.
        """
        if self.type in TILE_NAMES:
            name = TILE_NAMES[self.type]
        else:
            name = hex(self.type)

        return name

    @name.setter
    def name(self, value):
        """Ignore external name assignments.

        Parameters
        ----------
        value : str
            Ignored because the name is derived from ``type``.
        """
        pass

    def copy(self):
        """Create a copy of the tile and its position.

        Copying preserves the decoded block reference while duplicating the map
        coordinate record for selection and clipboard workflows.

        Returns
        -------
        MapTile
            Tile with the same decoded block and a copied position.
        """
        return MapTile(self.block, self.pos.copy())

    def draw(self, dc, block_length, _=None, anim_frame=0):
        """Draw the tile's current block at its map position.

        The world-map renderer calls this after updating the frame so animated
        overworld tiles stay in sync with the editor preview.

        Parameters
        ----------
        dc : QPainter
            Painter receiving the tile image.
        block_length : int
            Pixel size of one world-map tile.
        _ : object, optional
            Unused compatibility argument for shared draw call sites.
        anim_frame : int, optional
            Animation frame forwarded to the cached block.
        """
        self.block.frame = anim_frame

        self.block.rerender()

        self.block.draw(
            dc,
            self.x_position * block_length,
            self.y_position * block_length,
            block_length=block_length,
            selected=self.selected,
            transparent=False,
        )

    def set_position(self, x, y):
        """Store a new world-map position for the tile.

        Replacing ``pos`` keeps the ROM-backed coordinate record aligned with
        drag and placement operations.

        Parameters
        ----------
        x : int
            Horizontal tile coordinate.
        y : int
            Vertical tile coordinate.
        """
        self.pos = Position.from_xy(x, y)

    def get_position(self) -> tuple[int, int]:
        """World-map position for the tile.

        Sorting and drawing read this tuple instead of reaching into
        ``Position`` directly.

        Returns
        -------
        tuple[int, int]
            Horizontal and vertical tile coordinates.
        """
        return self.pos.xy

    def change_type(self, new_type):
        """Replace the decoded tile block while keeping the same position.

        Parameters
        ----------
        new_type : int
            New world-map tile id.

        Examples
        --------
        Tile paint operations replace the decoded block but preserve the
        existing world-map coordinate::

            tile = MapTile(block, pos)
            old_position = tile.get_position()
            tile.change_type(new_type)
            tile.get_position() == old_position
        """
        self.block = get_worldmap_tile(new_type, self.block._palette_group.index)

        self.type = self.block.index

        if self.type in TILE_NAMES:
            self.name = TILE_NAMES[self.type]
        else:
            self.name = hex(self.type)

    def __lt__(self, other):
        """Check whether this tile sorts before another map object.

        Sorting follows SMB3's world-map screen order so editor lists and
        redraw passes match the underlying map layout.

        Parameters
        ----------
        other : MapObject
            Other map object being ordered for world-map workflows.

        Returns
        -------
        bool
            ``True`` when this tile comes earlier in screen and row order.
        """
        screen = self.x_position // WORLD_MAP_SCREEN_WIDTH
        x = self.x_position % WORLD_MAP_SCREEN_WIDTH
        y = self.y_position

        result = screen * WORLD_MAP_SCREEN_SIZE + y * WORLD_MAP_SCREEN_WIDTH + x

        screen = other.x_position // WORLD_MAP_SCREEN_WIDTH
        x = other.x_position % WORLD_MAP_SCREEN_WIDTH
        y = other.y_position

        other_result = screen * WORLD_MAP_SCREEN_SIZE + y * WORLD_MAP_SCREEN_WIDTH + x

        return result < other_result

    def __repr__(self):
        """Compact developer-facing tile description.

        The representation is used when debugging tile ordering, redraw order,
        and world-map edits, so it summarizes the same position and type state
        carried through the editing workflow.

        Returns
        -------
        str
            Tile type, name, and position.
        """
        return f"MapTile #{self.type:#x}: '{self.name}' at {self.x_position}, {self.y_position}"
