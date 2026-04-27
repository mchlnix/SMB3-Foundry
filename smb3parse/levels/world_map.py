"""Decode, query, and persist SMB3 overworld map data.

This module collects the helpers that locate each world map in the ROM,
interpret overworld tile and pointer tables, and expose the data through
``WorldMap``. ``WorldMap`` bridges raw ``WorldMapData`` records with lookup
operations that the editor needs when it asks "what tile, level, or sprite is
at this position?" and with write-back operations that push modified pointer or
sprite records back into the ROM-backed data objects.

The main entry points are ``list_world_map_addresses()``,
``get_all_world_maps()``, and ``WorldMap.from_world_number()``. Readers who
need the lower-level storage model should continue into
``smb3parse.data_points.WorldMapData`` and ``LevelPointerData``.

See Also
--------
smb3parse.data_points.WorldMapData
    Backing storage object for tile, sprite, and level-pointer tables.
smb3parse.data_points.LevelPointerData
    Mutable record used for overworld level lookup and save-back.
smb3parse.levels.WorldMapPosition
    Position helper used when iterating visible overworld coordinates.
"""

from typing import Generator
from warnings import warn

from smb3parse.constants import (
    OFFSET_SIZE,
    SPRITE_COUNT,
    TILE_LEVEL_1,
    TILE_LEVEL_10,
    TILE_NAMES,
    WORLD_MAP_OBJECT_SET,
    Constants,
)
from smb3parse.data_points import LevelPointerData, Position, SpriteData, WorldMapData
from smb3parse.levels import (
    COMPLETABLE_LIST_END_MARKER,
    FIRST_VALID_ROW,
    SPECIAL_ENTERABLE_TILE_AMOUNT,
    VALID_COLUMNS,
    VALID_ROWS,
    WORLD_COUNT,
    WORLD_MAP_BASE_OFFSET,
    WORLD_MAP_HEIGHT,
    WORLD_MAP_SCREEN_SIZE,
    WORLD_MAP_SCREEN_WIDTH,
    LevelBase,
)
from smb3parse.levels.WorldMapPosition import WorldMapPosition
from smb3parse.objects.object_set import ObjectSet
from smb3parse.util.rom import Rom


def list_world_map_addresses(rom: Rom) -> list[int]:
    """Return the ROM addresses of every overworld layout.

    Parameters
    ----------
    rom : Rom
        ROM image that contains the world-map layout pointer table.

    Returns
    -------
    list of int
        Absolute ROM addresses for each world map layout, ordered by world
        number.
    """
    addresses = [
        WORLD_MAP_BASE_OFFSET + rom.little_endian(Constants.LAYOUT_LIST_OFFSET + OFFSET_SIZE * world)
        for world in range(WORLD_COUNT)
    ]

    return addresses


def get_all_world_maps(rom: Rom) -> list["WorldMap"]:
    """Instantiate every overworld map present in ``rom``.

    Parameters
    ----------
    rom : Rom
        ROM image that provides the world-map pointer table and map data.

    Returns
    -------
    list of WorldMap
        Parsed world maps in world-number order.
    """
    world_map_addresses = list_world_map_addresses(rom)

    return [WorldMap(address, rom) for address in world_map_addresses]


def level_name(data: LevelPointerData | None) -> str:
    """Derive a human-readable level label from a level pointer.

    Parameters
    ----------
    data : LevelPointerData or None
        Level pointer associated with an overworld tile. ``None`` produces an
        empty label.

    Returns
    -------
    str
        Editor-facing level name based on the owning world and the tile that
        indexes the pointer list.
    """
    if data is None:
        return ""

    tile = data.world.tile_data[data.pos.tile_data_index]

    if not tile_is_enterable(tile, data._rom):
        return "Untitled Level"

    if tile in range(TILE_LEVEL_1, TILE_LEVEL_10 + 1):
        return f"Level {data.world.index + 1}-{tile - TILE_LEVEL_1 + 1}"

    return f"Level {data.world.index + 1}-{TILE_NAMES[tile]}"


def _get_normal_enterable_tiles(rom: Rom) -> bytes:
    """Read the per-quadrant minimum enterable-tile values."""
    return rom.read(Constants.TILE_ATTRIBUTES_TS0_OFFSET, 4)


def _get_special_enterable_tiles(rom: Rom) -> bytes:
    """Read the explicit list of special enterable overworld tiles."""
    return rom.read(Constants.SPECIAL_ENTERABLE_TILES_LIST, SPECIAL_ENTERABLE_TILE_AMOUNT)


def _get_completable_tiles(rom: Rom) -> bytearray:
    """Read the list of tiles that the game treats as completable nodes."""
    completable_tile_amount = (
        rom.find(
            COMPLETABLE_LIST_END_MARKER.to_bytes(1, byteorder="big"),
            Constants.COMPLETABLE_TILES_LIST,
        )
        - Constants.COMPLETABLE_TILES_LIST
    )

    return rom.read(Constants.COMPLETABLE_TILES_LIST, completable_tile_amount)


def tile_is_enterable(tile_index: int, rom: Rom) -> bool:
    """Determine whether the SMB3 overworld logic allows a tile to be entered.

    Parameters
    ----------
    tile_index : int
        Raw overworld tile value to test.
    rom : Rom
        ROM image that stores the enterable and completable tile tables.

    Returns
    -------
    bool
        ``True`` when the tile can host player entry according to the ROM's
        attribute tables.
    """
    quadrant_index = tile_index >> 6

    return (
        tile_index >= _get_normal_enterable_tiles(rom)[quadrant_index]
        or tile_index in _get_completable_tiles(rom)
        or tile_index in _get_special_enterable_tiles(rom)
    )


class WorldMap(LevelBase):
    """Represent one SMB3 overworld and its editable lookup tables.

    ``WorldMap`` wraps ``WorldMapData`` with editor-oriented queries. It
    decodes the tile layout, sprite table, and level-pointer list for one
    world, lets callers look up records by map position, and delegates writes
    back to the underlying data-point objects after edits.

    Parameters
    ----------
    layout_address : int
        Absolute ROM address of the world's layout byte stream.
    rom : Rom
        ROM image that contains the layout, sprite, start-position, and
        level-pointer tables for this world.

    Raises
    ------
    ValueError
        Raised when ``layout_address`` does not correspond to a known world map
        or when the layout length is not a whole-number multiple of a world-map
        screen.

    Attributes
    ----------
    rom : Rom
        ROM image used for all lookups and write-back operations.
    number : int
        One-based world number derived from the layout-address table.
    data : WorldMapData
        Backing data object that stores tile bytes, pointers, sprites, and the
        map start position.

    Notes
    -----
    The class does not write the entire map back in one batch. Instead, lookup
    methods return mutable data-point objects such as ``LevelPointerData`` and
    ``SpriteData``; callers update those records and invoke their ``write_back``
    methods to persist specific edits. A typical editor flow is: decode one
    world from the layout table, resolve positions to tiles or pointer records,
    mutate the returned record objects, and write those edits back through the
    record-level persistence hooks. That decode -> position lookup ->
    record-level mutation -> write-back lifecycle is the main value of the
    wrapper: it keeps callers in world-map coordinates until they need one
    concrete ROM-backed record, then hands them the exact data-point object
    that owns persistence for that edit.
    """

    def __init__(self, layout_address: int, rom: Rom):
        """Initialize a world map wrapper for an existing ROM layout.

        The constructor resolves the one-based world number from the shared
        layout table, then binds ``WorldMapData`` for that zero-based world
        index. Every later lookup in this wrapper flows through that shared
        backing object, so tile reads, sprite queries, start-position access,
        and level-pointer edits all observe and mutate the same decoded ROM
        state.

        Parameters
        ----------
        layout_address : int
            Absolute ROM address of the world-map layout bytes.
        rom : Rom
            ROM image that owns the world-map pointer tables and payload data.

        Raises
        ------
        ValueError
            Raised when the address is not present in the world-map table or
            when the layout data length is not divisible by the screen size.
        """
        super(WorldMap, self).__init__(ObjectSet(rom, WORLD_MAP_OBJECT_SET), layout_address)

        self.rom = rom

        memory_addresses = list_world_map_addresses(rom)

        try:
            self.number = memory_addresses.index(layout_address) + 1
        except ValueError:
            raise ValueError(f"World map was not found at given memory address {layout_address:x}.")

        self.data = WorldMapData(self.rom, self.world_index)

        if len(self.layout_bytes) % WORLD_MAP_SCREEN_SIZE != 0:
            raise ValueError(
                f"Invalid length of layout bytes for world map ({self.layout_bytes}). "
                f"Should be divisible by {WORLD_MAP_SCREEN_SIZE}."
            )

    @property
    def screen_count(self):
        """Expose how many 16x9 screens this world layout spans.

        Editor coordinate validation and whole-map iteration use this derived
        count to decide which screen numbers are valid.

        Returns
        -------
        int
            Number of layout screens implied by the stored tile bytes.
        """
        return len(self.layout_bytes) // WORLD_MAP_SCREEN_SIZE

    @property
    def width(self):
        """Expose the horizontal tile span of the full world layout.

        Callers that flatten the map into one coordinate space use this derived
        width together with ``height`` and ``gen_positions()`` to translate
        screen-local SMB3 coordinates into one whole-world iteration range.

        Returns
        -------
        int
            Horizontal tile count across the complete map layout.
        """
        return int(self.screen_count * WORLD_MAP_SCREEN_WIDTH)

    @property
    def height(self):
        """Expose the visible SMB3 overworld height.

        The value stays constant across worlds and lets coordinate-aware callers
        pair the per-world screen count with the fixed vertical bounds.

        Returns
        -------
        int
            Number of visible tile rows in each world-map screen.
        """
        return WORLD_MAP_HEIGHT

    @property
    def layout_bytes(self):
        """Expose the raw tile-layout byte stream for this world.

        Position-based tile lookups ultimately index into this buffer after
        validating screen, row, and column coordinates.

        Returns
        -------
        bytes
            Tile bytes for every screen in display order as stored by
            ``WorldMapData``.
        """
        return self.data.tile_data

    @layout_bytes.setter
    def layout_bytes(self, value):
        """Replace the tile-layout byte stream stored by ``WorldMapData``.

        Parameters
        ----------
        value : bytes
            New tile bytes for the full world-map layout.
        """
        self.data.tile_data = value

    @property
    def world_index(self):
        """Expose the zero-based world index used by backing records.

        ``WorldMapData`` and related pointer tables are keyed by this value even
        though the editor usually presents one-based world numbers. The
        constructor resolves ``number`` once, and the rest of the wrapper uses
        ``world_index`` whenever it needs to reopen or persist world-specific
        ROM tables through ``WorldMapData``. It is therefore the shared key
        that connects this high-level wrapper to every underlying table read
        and write for the world.

        Returns
        -------
        int
            Zero-based index derived from ``number`` for ROM table access.

        Notes
        -----
        This value is consumed immediately by ``WorldMapData`` and related
        data-point wrappers whenever the world wrapper reopens, decodes, or
        writes back world-specific ROM tables. It is therefore the shared key
        that keeps editor-facing world numbers aligned with the zero-based ROM
        indexing scheme used underneath. The workflow is: accept a one-based
        world number from higher-level code, translate it once here, then pass
        the zero-based key through every lower-level world-table read or write.
        """
        return self.number - 1

    @property
    def level_count(self):
        """Expose how many level pointers this world currently stores.

        Bulk pointer tools use this count to reason about how much pointer data
        the backing tables currently describe before they iterate
        ``level_pointers`` or decide whether a replace or clear pass will touch
        any level records at all. That keeps whole-world editing code from
        probing the pointer table blindly when it needs to size list views,
        validate indexes, or decide whether lookup work is necessary.

        Returns
        -------
        int
            Count reported by the backing world-map data tables.

        Notes
        -----
        The count is typically consumed before iterating :attr:`level_pointers`
        or rebuilding level-oriented editor views. That makes it the cheap
        world-level summary that gates later pointer-table scans and list-size
        decisions. In other words, callers ask for this count first, then use
        it to size list views, validate indexes, or decide whether a deeper
        pointer-table walk is necessary at all. The usual data-flow is:
        consult ``level_count`` as the lightweight summary, then transition
        into :attr:`level_pointers` or position-based lookup only when that
        count says the world actually owns level records worth scanning. The
        property itself does not mutate world state; its role is to gate later
        traversal work by exposing the count that ``WorldMapData`` already
        decoded from the backing ROM tables.
        """
        return self.data.level_count

    def level_for_position(self, pos: Position) -> LevelPointerData | None:
        """Look up the level pointer stored at an overworld position.

        This mirrors the editor's high-level view of the game's overworld
        lookup path: resolve the pointer record that occupies ``pos`` and warn
        when its level-layout offset falls outside the expected SMB3 bank
        window.

        Parameters
        ----------
        pos : Position
            Screen, row, and column within this world map.

        Returns
        -------
        LevelPointerData or None
            Matching level pointer for ``pos``, or ``None`` when the tile does
            not own a level record.

        Notes
        -----
        Callers typically use this as the first step in an edit flow: resolve
        the pointer, mutate its addresses or object set, then persist the
        change with ``write_back()``. That keeps positional lookup separate from
        record mutation while still following the same decode-to-save path.

        Warns
        -----
        UserWarning
            Emitted when a matching pointer references a level-layout offset
            outside the expected ``0xA000`` to ``0xC000`` window.
        """
        if (level_pointer := self.level_at(pos)) is None:
            return None

        if not 0xA000 <= level_pointer.level_offset < 0xC000:
            # suppose that level layouts are only in this range?
            warn(f"Level in {self}@{pos.screen=}, {pos.row=}, {pos.column=} has offset {level_pointer.level_offset}")

        return level_pointer

    def replace_level_at_position(self, level_info, position: "WorldMapPosition"):
        """Replace the level pointer stored at an overworld position.

        This is the write-side companion to ``level_for_position()``. It
        resolves the existing pointer record, updates its three ROM-facing
        fields, and immediately persists the record back through
        ``LevelPointerData.write_back()`` so the edit leaves the wrapper, the
        backing data object, and the ROM tables in the same state.

        Parameters
        ----------
        level_info : tuple[int, int, int]
            Replacement ``(level_address, enemy_address, object_set_number)``
            tuple.
        position : WorldMapPosition
            Tile location whose existing level pointer should be updated.

        Raises
        ------
        LookupError
            Raised when ``position`` does not currently map to a level pointer.

        Notes
        -----
        The method mutates the matching ``LevelPointerData`` record and calls
        ``write_back()`` immediately, so the ROM-backed tables stay in sync with
        the in-memory edit rather than relying on a later world-level flush.
        """
        level_address, enemy_address, object_set_number = level_info

        level_pointer = self.level_for_position(position)

        if level_pointer is None:
            raise LookupError("No existing level at position.")

        level_pointer.object_set = object_set_number
        level_pointer.level_address = level_address
        level_pointer.enemy_address = enemy_address

        level_pointer.write_back()

    def level_name_for_position(self, pos: Position) -> str:
        """Translate the level pointer at ``pos`` into an editor label.

        This keeps lookup code that only needs a display name out of the
        pointer-mutation path by reusing the same tile-to-name logic as
        overworld inspection views after positional pointer resolution. In
        practice the flow is: resolve the pointer record with ``level_at()``,
        inspect the owning tile byte, and derive the same user-facing label the
        editor shows in map-selection surfaces, without forcing callers to
        understand pointer bytes or tile naming rules themselves.

        Parameters
        ----------
        pos : Position
            Overworld position to inspect.

        Returns
        -------
        str
            Human-readable label derived from the level pointer and the tile at
            ``pos``. Returns an empty string when no level pointer exists.

        Notes
        -----
        This method sits on the display side of the pointer lookup workflow:
        resolve the pointer record at one position, inspect the tile byte that
        qualifies it, then collapse that ROM-backed state into the label shown
        by editor-facing selection and inspection surfaces.
        """
        return level_name(self.level_at(pos))

    def gen_sprites(self) -> Generator[SpriteData, None, None]:
        """Iterate over every overworld sprite slot for this world.

        The generator yields wrapper objects instead of raw bytes so callers can
        inspect, clear, move, and save individual sprite records without
        decoding the sprite table themselves.

        Yields
        ------
        SpriteData
            Sprite records in table order, including cleared slots.
        """
        for index in range(SPRITE_COUNT):
            yield SpriteData(self.data, index)

    def clear_sprites(self):
        """Clear every sprite slot and write the cleared records back."""
        for sprite in self.gen_sprites():
            sprite.clear()
            sprite.write_back()

    def sprite_at(self, pos: Position) -> SpriteData | None:
        """Find the overworld sprite record stored at ``pos``.

        This is the sprite-table counterpart to ``level_at()``. It answers
        positional queries for editor tools that need to inspect or mutate the
        separate sprite record associated with a tile before writing the record
        back, so callers can stay in position space until they have identified
        the exact ROM-backed sprite record to edit.

        Parameters
        ----------
        pos : Position
            Overworld position to inspect.

        Returns
        -------
        SpriteData or None
            Matching sprite record, or ``None`` when the tile has no sprite.

        Notes
        -----
        This scans the fixed-size sprite table rather than the tile layout,
        because overworld sprites are stored as separate records in SMB3. The
        returned record can then move through the normal edit flow: inspect,
        mutate, and call ``write_back()`` on that specific sprite slot.
        In other words, the method keeps callers in position space until they
        have identified the one ROM-backed sprite record that later edit code
        will mutate and persist. The usual workflow is: start from a tile
        position, locate the matching sprite slot here, then hand that record
        to later edit or save code.
        """
        for sprite_data in self.gen_sprites():
            if sprite_data.is_at(pos):
                return sprite_data
        else:
            return None

    @property
    def level_pointers(self):
        """Expose the mutable level-pointer table for this world.

        Position-based lookup helpers scan this collection, and edit commands
        mutate the returned records before asking them to persist themselves.
        That makes this property the handoff point between whole-map queries in
        ``WorldMap`` and record-level persistence in ``LevelPointerData``. Any
        caller that needs direct table access after world decode starts from
        this property rather than re-reading pointer bytes from the ROM.

        Returns
        -------
        list of LevelPointerData
            Parsed level-pointer records owned by this world's backing data.

        Notes
        -----
        ``WorldMap`` itself uses this collection as the shared source for
        positional scans, replacement flows, and bulk-clear operations. Callers
        that step down from world-level queries into record-level mutations
        cross that boundary through this property.
        """
        return self.data.level_pointers

    def clear_level_pointers(self):
        """Clear every stored level pointer and persist each cleared record.

        Notes
        -----
        This only clears the individual pointer records. The surrounding world
        metadata that reports how many pointers are present is left unchanged.
        """
        # todo doesn't remove them from the world list, though. need to change amount on screen as well
        for level_pointer in self.level_pointers:
            level_pointer.clear()
            level_pointer.write_back()

    def level_at(self, pos: Position) -> LevelPointerData | None:
        """Find the level-pointer record stored at ``pos``.

        This positional scan is the low-level lookup primitive used by
        ``level_for_position()``, name generation, and pointer replacement
        workflows, all of which begin by resolving a tile position to a record.

        Parameters
        ----------
        pos : Position
            Overworld position to inspect.

        Returns
        -------
        LevelPointerData or None
            Matching level pointer, or ``None`` when the tile has no level
            record.
        """
        for level_pointer in self.level_pointers:
            if level_pointer.is_at(pos):
                return level_pointer
        else:
            return None

    def tile_at(self, pos: Position) -> int:
        """Read the raw overworld tile byte stored at ``pos``.

        The bounds checks translate editor-facing positions into the valid SMB3
        overworld coordinate window before the method indexes the packed layout
        byte stream that drives level and sprite interpretation.

        Parameters
        ----------
        pos : Position
            Overworld position to inspect. Rows are validated against the
            visible tile rows below the border.

        Returns
        -------
        int
            Tile byte stored at ``pos``.

        Raises
        ------
        ValueError
            Raised when the screen, row, or column is outside the valid bounds
            for this world map.
        """
        if pos.row not in VALID_ROWS:
            raise ValueError(
                f"Given row {pos.row} is outside the valid range for world maps. Allowed are: {VALID_ROWS}."
            )

        if pos.column not in VALID_COLUMNS:
            raise ValueError(
                f"Given column {pos.column} is outside the valid range for world maps. Allowed are {VALID_COLUMNS}"
            )

        if pos.screen not in range(self.screen_count):
            raise ValueError(f"World {self.number} has {self.screen_count} screens. Given number {pos.screen} invalid.")

        return self.layout_bytes[pos.tile_data_index]

    def is_enterable(self, tile_index: int) -> bool:
        """Report whether SMB3 treats ``tile_index`` as an enterable tile.

        This delegates to the ROM-backed helper so world-specific callers can
        apply the same tile-entry rules the game uses before attempting
        position-to-level lookup. The method is typically part of a larger
        traversal where callers inspect tile bytes first and only ask for level
        pointers on positions whose tiles can actually host entry, keeping the
        expensive pointer-resolution path aligned with the game's own
        enterability rules.

        Parameters
        ----------
        tile_index : int
            Raw overworld tile value to test.

        Returns
        -------
        bool
            ``True`` when the tile passes the ROM-backed enterable-tile rules.

        Notes
        -----
        Callers usually use this as the cheap gate before they ask for more
        expensive pointer or sprite lookups. It therefore sits early in the
        world traversal flow, filtering raw tile bytes into the subset of
        positions that can legitimately participate in level-entry workflows.
        """
        return tile_is_enterable(tile_index, self.rom)

    @property
    def start_pos(self) -> Position:
        """Expose the player's world-map start tile.

        The returned coordinate is reconstructed from the start-position fields
        stored inside ``WorldMapData`` for this decoded world. That keeps
        whole-map consumers in the same coordinate model they use for tile,
        sprite, and level-pointer queries instead of forcing them to interpret
        the raw packed start-position bytes themselves.

        Returns
        -------
        Position
            Start position decoded from the backing world-map data.
        """
        return Position(0x20 >> 4, self.data.map_start_y >> 4, 0)

    def gen_positions(self) -> Generator["WorldMapPosition", None, None]:
        """Iterate over every visible tile position in screen-major order.

        This gives callers a stable traversal order for whole-map inspection,
        such as collecting enterable tiles or searching for positions that host
        levels and sprites before performing targeted record edits. The
        generator is also the bridge between this wrapper's whole-world view
        and ``WorldMapPosition``, which packages each yielded coordinate with
        the world map that owns it.

        Yields
        ------
        WorldMapPosition
            Positions spanning each screen, then row, then column.

        Notes
        -----
        The generated rows begin at ``FIRST_VALID_ROW`` so the iterator lines up
        with the visible world-map tile area rather than the top border.
        """
        for screen in range(self.screen_count):
            for row in range(WORLD_MAP_HEIGHT):
                for column in range(WORLD_MAP_SCREEN_WIDTH):
                    yield WorldMapPosition(self, screen, row + FIRST_VALID_ROW, column)

    def save_to_rom(self):
        """Persist world-map changes to the ROM.

        Notes
        -----
        This hook is currently unimplemented. Callers persist edits through the
        individual data-point ``write_back()`` methods instead.
        """
        pass

    @staticmethod
    def from_world_number(rom: Rom, world_number: int) -> "WorldMap":
        """Construct a world map by one-based SMB3 world number.

        This is the public lookup entry point when callers know the SMB3 world
        number but not the underlying layout address, letting them enter the
        normal decode and edit workflow from game-facing numbering.

        Parameters
        ----------
        rom : Rom
            ROM image that contains the world-map layout pointer table.
        world_number : int
            One-based world number in the range supported by SMB3.

        Returns
        -------
        WorldMap
            Parsed world map for ``world_number``.

        Raises
        ------
        ValueError
            Raised when ``world_number`` falls outside the supported range.
        """
        if world_number - 1 not in range(WORLD_COUNT):
            raise ValueError(f"World number {world_number - 1} must be between 1 and {WORLD_COUNT}, including.")

        memory_address = list_world_map_addresses(rom)[world_number - 1]

        return WorldMap(memory_address, rom)

    def __repr__(self):
        """Expose the concise debug label used in warnings and logs.

        Warnings emitted during level lookup include this representation so
        out-of-range pointer offsets can still be traced back to a world. The
        same short label is also safe to embed in broader traversal or save
        diagnostics without dumping full ROM addresses.

        Returns
        -------
        str
            One-based world label suitable for terse diagnostics.
        """
        return f"World {self.number}"
