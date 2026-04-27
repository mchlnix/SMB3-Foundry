"""Model world-map level pointer records stored in SMB3 ROM tables.

This module exposes :class:`LevelPointerData`, the data-point object that binds
an overworld tile position to the level-header offset, enemy-data offset, and
object-set selector needed to open a playable stage from a world map node.
`WorldMapData` discovers the shared pointer-table starts for one world,
``LevelPointerData`` resolves one entry inside those tables, editors mutate the
decoded coordinates and offsets in memory, and level-loading code later
consumes the resolved addresses to decode the stage behind the map tile.
Maintainers usually read this file together with
``smb3parse.data_points.world_map_data`` for the owning table layout and
``smb3parse.levels.level`` for the decoded level data that these addresses
eventually feed.

See Also
--------
smb3parse.data_points.world_map_data
    Owns the pointer tables and screen-position tables that this record indexes.
smb3parse.levels.level.Level
    Consumes the resolved header and enemy addresses after a pointer is decoded.
"""

from typing import TYPE_CHECKING

from smb3parse.constants import BASE_OFFSET, OFFSET_SIZE, Constants
from smb3parse.data_points.util import DataPoint, _IndexedMixin, _PositionMixin
from smb3parse.levels import (
    FIRST_VALID_ROW,
    WORLD_MAP_BASE_OFFSET,
    WORLD_MAP_SCREEN_SIZE,
    WORLD_MAP_SCREEN_WIDTH,
)
from smb3parse.util.rom import PRG_BANK_SIZE, Rom

if TYPE_CHECKING:
    from smb3parse.data_points.world_map_data import WorldMapData


class LevelPointerData(_PositionMixin, _IndexedMixin, DataPoint):
    """Represent one world-map pointer entry that opens a level.

    A level pointer record ties one overworld tile to four pieces of ROM state:
    the screen and tile position on the map, the level-header offset, the enemy
    data offset, and the object set required to decode the level-object stream.
    ``WorldMapData`` supplies the owning table addresses, while this class keeps
    the per-entry offsets synchronized with nibble-based map coordinates and the
    PRG-bank indirection used for level headers.

    Parameters
    ----------
    world_map_data : WorldMapData
        Owning world-map table wrapper. It provides the ROM handle and the base
        addresses for the position, level-offset, and enemy-offset lists that
        this entry indexes into.
    index : int
        Zero-based slot inside the owning world-map pointer tables.

    Attributes
    ----------
    SIZE : int
        Serialized footprint of one entry across the level-offset, enemy-offset,
        and nibble-packed position tables.
    world : WorldMapData
        Owning world-map data structure that supplies the pointer-table layout
        and ROM accessors.
    index : int
        Zero-based entry index within the owning pointer tables.
    _rom : Rom
        ROM wrapper inherited from :class:`~smb3parse.data_points.util.DataPoint`
        and used to read nibble-packed coordinates plus little-endian offsets.
    object_set_address : int
        ROM address of the nibble that stores the object-set selector beside
        the map row.
    object_set : int
        Object-set identifier used to translate ``level_offset`` into an actual
        header address and to decode level objects later.
    level_offset_address : int
        ROM address of the 16-bit little-endian level-header offset entry.
    level_offset : int
        Bank-relative level-header offset loaded from the world-map pointer
        table.
    enemy_offset_address : int
        ROM address of the 16-bit little-endian enemy-data offset entry.
    enemy_offset : int
        Bank-relative enemy-data offset loaded from the world-map pointer table.
    screen_address : int
        ROM address of the nibble-packed byte that stores the screen index and
        x coordinate for this map tile.
    x_address : int
        Alias of :attr:`screen_address` used by the shared position mixin when
        it reads or writes the x nibble.
    y_address : int
        ROM address of the nibble-packed byte that stores the row and object
        set for this map tile.
    screen : int
        Overworld screen index containing the pointer tile.
    x : int
        Column inside :attr:`screen`.
    y : int
        Row inside :attr:`screen`.
    pos : tuple[int, int, int]
        Flattened ``(screen, x, y)`` location exposed by the shared position
        mixin for comparisons and editor-facing table views.

    Notes
    -----
    SMB3 stores the header offset indirectly. The pointer table only supplies an
    offset within the PRG bank selected by the object set. ``object_set_offset``
    resolves that bank switch so :attr:`level_address` can expose a concrete ROM
    address.
    """

    SIZE = 2 * OFFSET_SIZE + 2  # object offset, enemy offset, 2 bytes for position in map

    def __init__(self, world_map_data: "WorldMapData", index: int):
        """Initialize an entry wrapper for one world-map level pointer slot.

        The constructor binds this object to one slot in the owning
        :class:`WorldMapData` tables and enters the shared
        :class:`~smb3parse.data_points.util.DataPoint` load lifecycle. That
        lifecycle calculates all per-entry ROM addresses and then loads the
        nibble-packed coordinates plus the two pointer offsets, so callers
        receive a fully decoded pointer record instead of a partially staged
        shell.

        Parameters
        ----------
        world_map_data : WorldMapData
            Owning world-map table wrapper that provides the ROM, pointer-table
            base addresses, and coordinate tables for this entry.
        index : int
            Zero-based slot within the world's position and pointer arrays.

        Notes
        -----
        Construction seeds per-entry fields with neutral defaults, records
        which world-map table slot this object owns, and then delegates to
        :class:`~smb3parse.data_points.util.DataPoint`. That base-class
        lifecycle immediately calls :meth:`calculate_addresses` and
        :meth:`read_values`, so by the time construction returns this object is
        already synchronized with one concrete pointer record inside the owning
        world-map tables.
        """
        self.world = world_map_data
        self.index = index

        self.object_set_address = 0x0
        self.object_set = 0

        self.level_offset_address = 0x0
        self.level_offset = 0

        self.enemy_offset_address = 0x0
        self.enemy_offset = 0

        super(LevelPointerData, self).__init__(self.world._rom)

    def calculate_addresses(self):
        """Resolve the ROM addresses for this pointer-table entry.

        Notes
        -----
        ``WorldMapData`` stores the screen/x nibble list, y/object-set nibble
        list, and the two offset tables separately. This method converts the
        shared table starts plus :attr:`index` into concrete per-entry addresses
        so :meth:`read_values` and :meth:`write_back` can move data between the
        ROM and this object.
        """
        self.x_address = self.screen_address = self.world.x_pos_list_start + self.index
        self.y_address = self.object_set_address = self.world.y_pos_list_start + self.index

        self.level_offset_address = (
            WORLD_MAP_BASE_OFFSET
            + self._rom.little_endian(self.world.level_offset_list_offset_address)
            + OFFSET_SIZE * self.index
        )
        self.enemy_offset_address = (
            WORLD_MAP_BASE_OFFSET
            + self._rom.little_endian(self.world.enemy_offset_list_offset_address)
            + OFFSET_SIZE * self.index
        )

    @property
    def level_address(self):
        """Expose the header address that level-loading code will open.

        This property converts the serialized world-map pointer state into the
        absolute ROM address that downstream level decoders actually need.
        It is the read-side boundary between the world-map editing model and
        the later level-loading workflow.

        Returns
        -------
        int
            Absolute ROM address produced by combining the bank selected by
            :attr:`object_set` with the bank-relative :attr:`level_offset`.

        Notes
        -----
        This property is the handoff from world-map pointer decoding to the
        later stage-loading workflow. Callers use it when they need the concrete
        header address instead of the serialized bank-relative offset, such as
        when building a :class:`~smb3parse.levels.level.Level` from a world-map
        tile selection or when retargeting a pointer after an editor moves the
        entry to a different object set.
        """
        return BASE_OFFSET + self.object_set_offset + self.level_offset

    @level_address.setter
    def level_address(self, value):
        """Store a resolved level-header address back as a bank-relative offset.

        Parameters
        ----------
        value : int
            Absolute ROM address of the level header.

        Notes
        -----
        World-map pointer tables do not store absolute addresses. The setter
        strips the common ROM base and the object-set bank offset so the
        serialized field matches the format expected by SMB3.
        """
        self.level_offset = (value - BASE_OFFSET - self.object_set_offset) & 0xFFFF

    @property
    def enemy_address(self):
        """Expose the enemy-data address paired with this map-tile entry.

        This property translates the serialized enemy pointer into the absolute
        ROM address consumed by later enemy and item decoders. Keeping that
        translation here lets world-map editing code work in ROM-space
        addresses without duplicating the table-relative storage rule.

        Returns
        -------
        int
            Absolute ROM address of the enemy and item data referenced by this
            overworld pointer.

        Notes
        -----
        Level-loading tools use this property after pointer decoding so the
        enemy stream stays synchronized with the header selected by
        :attr:`level_address` when one world-map tile is turned into a playable
        stage. Editors also use it as the stable external address while the
        serialized table continues storing only the bank-relative offset.
        """
        return BASE_OFFSET + self.enemy_offset

    @enemy_address.setter
    def enemy_address(self, value):
        """Store an absolute enemy-data address as a table-relative offset.

        Parameters
        ----------
        value : int
            Absolute ROM address of the enemy and item data stream.
        """
        self.enemy_offset = value - BASE_OFFSET

    @property
    def object_set_offset(self):
        """Resolve the bank contribution encoded by :attr:`object_set`.

        SMB3 stores a level-header offset relative to the PRG bank selected by
        the object set rather than as one global address. This property is the
        place where that encoded selector becomes the concrete bank contribution
        used by :attr:`level_address` and the wider level-loading pipeline.

        Returns
        -------
        int
            Offset added to :attr:`level_offset` to resolve the real level
            header address inside the ROM.

        Notes
        -----
        SMB3 selects a PRG bank per object set and maps that bank into CPU
        space at ``0xA000``. This property reverses that mapping so
        :attr:`level_address` can expose a stable ROM-space address and so the
        level-pointer editing workflow can switch object sets without manually
        recomputing header banks. It is the boundary between the serialized
        object-set nibble and the absolute header addresses consumed by later
        parsing code.
        """
        return self._rom.int(Constants.OFFSET_BY_OBJECT_SET_A000 + self.object_set) * PRG_BANK_SIZE - 0xA000

    def read_values(self):
        """Load the pointer record fields from the owning ROM tables.

        Notes
        -----
        The position and object-set tables are nibble-packed, while the level
        and enemy offsets are stored as little-endian words. This method reads
        both representations and normalizes them into the instance attributes
        used by editors and serializers.
        """
        self.screen, self.x = self._rom.nibbles(self.screen_address)

        self.y, self.object_set = self._rom.nibbles(self.y_address)

        self.level_offset = self._rom.little_endian(self.level_offset_address)
        self.enemy_offset = self._rom.little_endian(self.enemy_offset_address)

    def clear(self):
        """Reset the entry to a safe default pointer state.

        Notes
        -----
        Clearing preserves a valid map row and the default plains object set so
        later writes do not leave the ROM with an impossible row or an unset
        object-set bank.
        """
        self.screen = 0
        self.x = 0
        self.y = FIRST_VALID_ROW

        self.object_set = 1
        self.level_offset = 0x0
        self.enemy_offset = 0x0

    def write_back(self, rom: Rom | None = None):
        """Write the normalized entry fields back into ROM tables.

        Parameters
        ----------
        rom : Rom, optional
            Target ROM wrapper. When omitted, the entry writes back into the ROM
            that originally loaded it.

        Notes
        -----
        This method mirrors :meth:`read_values`: coordinates and object-set data
        are packed into nibbles, while level and enemy offsets are written as
        little-endian words. Callers use the optional ROM parameter to stage
        edits into a copy without rebinding the data point.
        """
        if rom is None:
            rom = self._rom

        rom.write_nibbles(self.screen_address, self.screen, self.x)
        rom.write_nibbles(self.y_address, self.y, self.object_set)

        rom.write_little_endian(self.level_offset_address, self.level_offset)
        rom.write_little_endian(self.enemy_offset_address, self.enemy_offset)

    def __eq__(self, other):
        """Compare two pointer entries by serialized location and contents.

        Equality is intentionally stricter than comparing only the decoded
        addresses. Two entries count as equal only when they describe the same
        overworld tile and still point at the same backing ROM slots, which
        keeps undo, diff, and table-rewrite code from confusing moved entries
        with unchanged ones.

        Parameters
        ----------
        other : object
            Candidate value to compare against.

        Returns
        -------
        bool or NotImplemented
            ``True`` when both entries describe the same map position and point
            at the same serialized ROM addresses and offsets.
        """
        if not isinstance(other, LevelPointerData):
            return NotImplemented

        if self.pos != other.pos:
            return False

        if self.level_offset != other.level_offset:
            return False

        if self.enemy_offset != other.enemy_offset:
            return False

        if self.object_set != other.object_set:
            return False

        if self.screen_address != other.screen_address:
            return False

        if self.y_address != other.y_address:
            return False

        if self.level_offset_address != other.level_offset_address:
            return False

        if self.enemy_offset_address != other.enemy_offset_address:
            return False

        return True

    def __lt__(self, other):
        """Order entries by overworld screen, row, and column position.

        Sorting by the flattened map position lets editor views and search
        results present pointer entries in traversal order instead of raw table
        order, which is easier to line up with what a maintainer sees on the
        world map. In practice this comparison is the ordering hook used when
        table-backed pointer records are regrouped into UI lists, diffs, or
        other workflows that care about visible map traversal more than ROM
        storage order.

        Parameters
        ----------
        other : LevelPointerData
            Pointer entry to compare against.

        Returns
        -------
        bool
            ``True`` when this entry appears earlier in overworld traversal
            order than ``other``.

        Notes
        -----
        The ordering flattens screen, row, and column into one sortable value
        so editor views can present pointers in the same order players encounter
        them on the world map, which keeps drag, diff, and list-based editing
        views aligned with the visible map traversal order instead of the raw
        pointer-table index order used in ROM storage.
        """
        self_result = self.screen * WORLD_MAP_SCREEN_SIZE + self.y * WORLD_MAP_SCREEN_WIDTH + self.x
        other_result = other.screen * WORLD_MAP_SCREEN_SIZE + other.y * WORLD_MAP_SCREEN_WIDTH + other.x

        return self_result < other_result
