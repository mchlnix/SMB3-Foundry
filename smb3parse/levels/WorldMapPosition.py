"""Represent one coordinate on an SMB3 overworld map.

This module defines ``WorldMapPosition``, the position helper that binds the
generic ``Position`` coordinate record to a specific ``WorldMap`` instance.
The world-map parser and editor use it when they need one object that can
answer coordinate questions through the owning map: which level pointer, tile,
or sprite record lives at this location, and whether the location can host an
enterable level.

Readers who need the storage and lookup implementation behind these helpers
should continue into ``smb3parse.levels.world_map`` and
``smb3parse.data_points.LevelPointerData``.

See Also
--------
smb3parse.levels.world_map.WorldMap
    Owns the tile, pointer, and sprite tables that this coordinate queries.
smb3parse.data_points.Position
    Base coordinate record shared by other parsed SMB3 position helpers.
smb3parse.data_points.LevelPointerData
    Mutable pointer record returned when a coordinate resolves to a level.
"""

import typing

from smb3parse.data_points import LevelPointerData, Position

if typing.TYPE_CHECKING:
    from smb3parse.levels.world_map import WorldMap


class WorldMapPosition(Position):
    """Bind one overworld coordinate to a concrete ``WorldMap``.

    ``WorldMapPosition`` extends the generic ``Position`` record with the world
    context needed to resolve SMB3 overworld lookups. Callers hand instances of
    this class back to ``WorldMap`` query methods when they need to translate a
    screen, row, and column into level-pointer, sprite, or tile records.

    Parameters
    ----------
    world : smb3parse.levels.world_map.WorldMap
        Parsed overworld map that owns the tile, pointer, and sprite tables for
        this coordinate.
    screen : int
        Zero-based overworld screen index inside ``world``.
    row : int
        Tile row within ``screen``.
    column : int
        Tile column within ``screen``.

    Attributes
    ----------
    world : smb3parse.levels.world_map.WorldMap
        Owning world map used for all coordinate-to-record lookups.

    Notes
    -----
    The class does not cache map records. Each property-style helper delegates
    back into ``world`` so callers always observe the world map's current tile,
    pointer, and sprite tables after edits or reloads.
    """

    def __init__(self, world, screen: int, row: int, column: int):
        """Initialize a map-bound overworld coordinate.

        The constructor freezes the screen, row, and column values that
        ``WorldMap`` lookup methods expect, then stores the owning map so later
        helpers can resolve tile, sprite, and level-pointer records without the
        caller re-supplying world context.

        Parameters
        ----------
        world : smb3parse.levels.world_map.WorldMap
            Parsed world map that will answer subsequent tile, sprite, and
            level-pointer lookups for this coordinate.
        screen : int
            Zero-based overworld screen index inside ``world``.
        row : int
            Tile row within the selected screen.
        column : int
            Tile column within the selected screen.
        """
        super(WorldMapPosition, self).__init__(column, row, screen)
        self.world: "WorldMap" = world

    @property
    def level_pointer(self) -> LevelPointerData | None:
        """Resolve the level-pointer record for this coordinate.

        The property delegates to :meth:`smb3parse.levels.world_map.WorldMap.level_for_position`
        so callers can move from a coordinate helper to the mutable pointer
        record that the editor or serializer updates.

        Returns
        -------
        LevelPointerData or None
            Mutable level-pointer record for this overworld position, or
            ``None`` when the position does not index a level entry.
        """
        return self.world.level_for_position(self)

    def can_have_level(self):
        """Report whether this coordinate can host an enterable level.

        The method asks the owning ``WorldMap`` for the tile stored
        at this coordinate, then applies the world's enterability rules. The
        result is useful when editor code needs to distinguish decorative map
        tiles from coordinates that may legally resolve to a level pointer.

        Returns
        -------
        bool
            ``True`` when the tile stored at this coordinate is enterable.
        """
        return self.world.is_enterable(self.tile())

    def sprite(self):
        """Resolve the sprite record attached to this coordinate.

        The helper performs the same coordinate lookup that map-view and editor
        tools need when they want to inspect or edit the overworld sprite table
        through a position object rather than raw row and column integers.

        Returns
        -------
        SpriteData or None
            Sprite record stored at this position, or ``None`` when the map has
            no sprite here.
        """
        return self.world.sprite_at(self)

    def has_sprite(self):
        """Report whether the coordinate currently holds a sprite record.

        This boolean wrapper keeps callers from repeating the sprite lookup
        contract when they only need to branch on sprite presence.

        Returns
        -------
        bool
            ``True`` when :meth:`sprite` resolves to a sprite entry.
        """
        return bool(self.sprite())

    def tile(self):
        """Resolve the raw overworld tile byte at this coordinate.

        Callers use this helper when a workflow starts from a
        ``WorldMapPosition`` but needs the owning map's tile-table value for
        enterability checks, level-name derivation, or direct editing.

        Returns
        -------
        int
            Tile byte currently stored at this screen, row, and column.
        """
        return self.world.tile_at(self)

    def tuple(self):
        """Serialize the coordinate into a world-aware tuple.

        The tuple form is useful when code needs a stable, hashable summary of
        a position that still distinguishes the owning world from identical
        screen, row, and column values in a different map.

        Returns
        -------
        tuple of int
            ``(world_number, screen, row, column)`` for this coordinate.
        """
        return self.world.number, self.screen, self.row, self.column

    def __eq__(self, other):
        """Compare two coordinates by world and tile position.

        Equality includes the world number as well as the screen-local
        coordinate so comparisons stay stable across multiple parsed worlds.

        Parameters
        ----------
        other : object
            Candidate object to compare against this coordinate.

        Returns
        -------
        bool
            ``True`` when ``other`` is a ``WorldMapPosition`` for the same
            world number, screen, row, and column.
        """
        if not isinstance(other, WorldMapPosition):
            return False

        return (
            self.world.number == other.world.number
            and self.screen == other.screen
            and self.row == other.row
            and self.column == other.column
        )

    def __repr__(self):
        """Format the coordinate for debug and log output.

        The representation keeps the owning world visible so trace output can
        distinguish identical screen, row, and column values from different
        overworld maps.

        Returns
        -------
        str
            String form that includes the owning world plus screen, row, and
            column information.
        """
        return f"WorldMapPosition({self.world}, screen={self.screen}, row={self.row}, column={self.column})"
