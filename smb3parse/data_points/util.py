"""Shared helpers for ROM-backed data point objects.

This module gathers the small abstractions that multiple
``smb3parse.data_points`` implementations rely on while translating ROM bytes
into editable Python objects. ``Position`` normalizes map and level
coordinates, ``DataPoint`` defines the load and save lifecycle for
ROM-extracted records, and the mixins add common position- and
index-management behavior for subclasses whose addresses are derived from
lookup tables or tile coordinates.

Concrete data point classes usually subclass :class:`DataPoint` together with
``_PositionMixin`` and/or ``_IndexedMixin``. Read those concrete classes next
to see which ROM addresses they calculate and how they write modified values
back into :class:`~smb3parse.util.rom.Rom`.

See Also
--------
smb3parse.levels
    Screen-width and row-offset constants used when translating between
    world-map tile indices and editable coordinates.
smb3parse.util.rom.Rom
    Byte-oriented ROM access layer consumed by :class:`DataPoint`
    implementations.
"""

from builtins import NotImplementedError
from dataclasses import dataclass
from typing import overload

from smb3parse.levels import (
    FIRST_VALID_ROW,
    WORLD_MAP_SCREEN_SIZE,
    WORLD_MAP_SCREEN_WIDTH,
)
from smb3parse.util.rom import Rom


@dataclass
class Position:
    """Represent a tile-oriented position in a level or on a world map.

    The coordinate model keeps ``x`` and ``y`` local to a 16-tile-wide screen
    and stores the screen number separately. That matches the SMB3 data-point
    workflows that frequently read or rewrite object coordinates from split ROM
    fields while still needing a flattened ``x`` coordinate for editing logic.

    Attributes
    ----------
    x : int
        Column within one 16-tile screen.
    y : int
        Row within one screen or map layout. World-map rows include the
        border rows used by the underlying tile data.
    screen : int
        Zero-based 16-tile screen index. The same split is used by both level
        objects and world-map tile data.

    See Also
    --------
    DataPoint
        Base class for ROM-backed records that commonly expose or consume
        ``Position`` instances.
    _PositionMixin
        Mixin that stores position fields on mutable data-point instances.
    """

    x: int
    y: int
    """Local row, including world-map border rows when used for map tiles."""

    screen: int
    """Zero-based 16-tile screen index for map tiles or level objects."""

    @property
    def tile_data_index(self):
        """Map this position onto the flattened world-map tile buffer.

        The index matches the one-dimensional tile buffers used by world-map
        readers and writers, so callers can move between editable coordinates
        and ROM-backed tile arrays without re-deriving screen math.

        Returns
        -------
        int
            Index into the contiguous world-map tile-data array addressed by
            this screen, row, and column.

        Notes
        -----
        ``FIRST_VALID_ROW`` skips the non-editable border rows that appear
        above the playable map tiles in the stored layout.
        """
        return self.screen * WORLD_MAP_SCREEN_SIZE + (self.row - FIRST_VALID_ROW) * WORLD_MAP_SCREEN_WIDTH + self.column

    @property
    def row(self):
        """Expose ``y`` through the row-oriented map and level vocabulary.

        Data-point classes use this property when ROM field names or editor
        widgets talk about rows instead of raw ``y`` storage.

        Returns
        -------
        int
            Row coordinate stored in ``y``.
        """
        return self.y

    @row.setter
    def row(self, value):
        """Store ``y`` through the row-oriented map and level vocabulary.

        Parameters
        ----------
        value : int
            Row value to store as ``y``.
        """
        self.y = int(value)

    @property
    def column(self):
        """Expose ``x`` through the column-oriented map and level vocabulary.

        Data-point classes use this property when ROM field names or editor
        widgets talk about columns instead of raw ``x`` storage.

        Returns
        -------
        int
            Column coordinate stored in ``x``.
        """
        return self.x

    @column.setter
    def column(self, value):
        """Store ``x`` through the column-oriented map and level vocabulary.

        Parameters
        ----------
        value : int
            Column value to store as ``x``.
        """
        self.x = int(value)

    @property
    def xy(self):
        """Expose the position as an absolute ``x`` coordinate and row.

        Callers use this form when screen-local storage needs to become a
        single horizontal coordinate for editing or arithmetic.

        Returns
        -------
        tuple[int, int]
            Absolute ``x`` coordinate across screens and the row coordinate.
        """
        return self.screen * WORLD_MAP_SCREEN_WIDTH + self.x, self.y

    def copy(self):
        """Duplicate the position for mutation without aliasing the original.

        Data-point code uses copies when it needs to compare, offset, or stage
        coordinates without mutating the original position in place.

        Returns
        -------
        Position
            New instance with the same screen-local coordinates.
        """
        return Position.from_xy(*self.xy)

    @staticmethod
    def from_xy(x, y):
        """Build a position from an absolute ``x`` coordinate and row.

        This is the inverse of :attr:`xy` and is used when editor code has
        already flattened screen-local coordinates.

        Parameters
        ----------
        x : int
            Absolute column across all 16-tile screens.
        y : int
            Row value to store on the position.

        Returns
        -------
        Position
            Position whose ``screen`` and local ``x`` are derived from the
            flattened column.
        """
        screen = x // WORLD_MAP_SCREEN_WIDTH
        x = x % WORLD_MAP_SCREEN_WIDTH

        return Position(int(x), int(y), int(screen))

    @staticmethod
    def from_tuple(tup):
        """Build a position from a 2- or 3-value coordinate tuple.

        The helper accepts both the flattened editor form and the explicit
        ``(x, y, screen)`` form used by lower-level callers.

        Parameters
        ----------
        tup : tuple[int, int] | tuple[int, int, int]
            Either ``(x, y)`` with an absolute ``x`` coordinate or
            ``(x, y, screen)`` with screen-local coordinates.

        Returns
        -------
        Position
            Parsed position instance.

        Raises
        ------
        ValueError
            Raised when ``tup`` does not contain two or three values.
        """
        if len(tup) == 2:
            return Position.from_xy(*tup)
        elif len(tup) == 3:
            return Position(*tup)
        else:
            raise ValueError(f"Expected 2 or 3 values, got {len(tup)}")

    @staticmethod
    def from_tile_data_index(index: int):
        """Reconstruct a world-map position from a flattened tile-data index.

        This is the inverse of :attr:`tile_data_index` for world-map tile
        buffers extracted from ROM, which lets data-point readers convert table
        offsets back into editable screen, row, and column fields before later
        editing or write-back logic reasons about the tile location. World-map
        decoders typically call it at the boundary where sequential ROM tile
        data becomes a coordinate-bearing object model.

        Parameters
        ----------
        index : int
            Index into the contiguous world-map tile-data array.

        Returns
        -------
        Position
            Position whose screen, row, and column address the indexed tile.
        """
        screen = index // WORLD_MAP_SCREEN_SIZE
        index %= WORLD_MAP_SCREEN_SIZE

        row = index // WORLD_MAP_SCREEN_WIDTH
        index %= WORLD_MAP_SCREEN_WIDTH

        column = index

        return Position(column, row + FIRST_VALID_ROW, screen)

    def __repr__(self):
        """Format the position for debugging output.

        The representation keeps the screen-local split visible so debugging
        output still matches the coordinate layout used by SMB3 data tables.

        Returns
        -------
        str
            String that includes the local coordinates, screen, and instance
            identity.
        """
        return f"Position({self.x}, {self.y} | {self.screen}) @ {id(self)}"

    def __add__(self, other):
        """Add two positions using their flattened coordinates.

        Arithmetic is performed in flattened editor space and then converted
        back into screen-local storage so callers can compose offsets without
        manually handling screen boundaries.

        Parameters
        ----------
        other : Position
            Position whose flattened coordinates are added to this one.

        Returns
        -------
        Position
            New position created from the summed absolute coordinates.
        """
        x, y = self.xy
        o_x, o_y = other.xy

        return Position.from_xy(x + o_x, y + o_y)

    def __neg__(self):
        """Negate the flattened coordinates of this position.

        This supports difference-style arithmetic while preserving the same
        screen-splitting rules used by :meth:`from_xy`.

        Returns
        -------
        Position
            New position whose absolute ``x`` and ``y`` are negated.
        """
        x, y = self.xy
        return Position.from_xy(-x, -y)

    def __sub__(self, other):
        """Subtract another position from this one.

        The operation reuses :meth:`__add__` and :meth:`__neg__` so every
        coordinate delta follows the same flatten-then-split conversion path.

        Parameters
        ----------
        other : Position
            Position whose flattened coordinates are subtracted.

        Returns
        -------
        Position
            New position created from the coordinate difference.
        """
        return self + -other


class DataPoint:
    """Base class for mutable records extracted from a ROM.

    Subclasses represent one logical unit of ROM-backed data together with the
    addresses used to read and rewrite it. Construction always follows the same
    lifecycle: keep a reference to the source :class:`~smb3parse.util.rom.Rom`,
    calculate any direct or indirect addresses, then load decoded values
    from those addresses into Python attributes.

    Attributes
    ----------
    _rom : Rom
        ROM instance that supplies bytes during construction and acts as the
        default write-back target.

    Parameters
    ----------
    rom : Rom
        ROM instance that owns the bytes for the record and remains available
        for later write-back operations.

    Notes
    -----
    ``calculate_addresses`` runs before ``read_values`` during initialization.
    Subclasses that derive addresses from indexes, lookup tables, or screen
    positions must preserve that ordering when recalculating their internal
    state.

    See Also
    --------
    _PositionMixin
        Adds shared coordinate storage for data points whose addresses or
        payloads depend on a screen, row, and column.
    _IndexedMixin
        Adds shared index-management behavior for data points backed by lookup
        tables.
    """

    def __init__(self, rom: Rom):
        """Load one ROM-backed record into editable Python state.

        Construction captures the ROM handle, resolves all addresses needed by
        the concrete record, and then decodes ROM bytes into mutable
        Python attributes.

        Parameters
        ----------
        rom : Rom
            ROM instance that owns the bytes for this data point.
        """
        self._rom: Rom = rom

        self.calculate_addresses()
        self.read_values()

    def calculate_addresses(self):
        """Resolve the ROM addresses used by this data point.

        Subclasses override this hook when their values live behind lookup
        tables, pointer tables, or other derived addressing schemes. The
        resolved addresses then become the source of truth for the rest of the
        record lifecycle. :meth:`__init__` always calls this hook before any
        decode step runs, and subclasses typically call it again after an
        editor changes the index, screen, or other selector that controls
        where the record lives in ROM. Implementations are expected to store
        every derived address on the instance so :meth:`read_values` and
        :meth:`write_back` both operate on one synchronized address map
        instead of re-deriving locations independently.

        Raises
        ------
        NotImplementedError
            Raised by the base implementation because concrete data-point
            classes must provide the address calculation.
        """
        raise NotImplementedError

    def read_values(self):
        """Decode this record's bytes from ROM into Python attributes.

        Concrete implementations decode bytes from the addresses established by
        :meth:`calculate_addresses` into editable attributes on the instance so
        later editor code and :meth:`write_back` operate on staged Python
        values instead of raw ROM bytes. This hook is the transition point
        between address resolution and the mutable object state consumed by the
        rest of the parser or editor pipeline.

        Raises
        ------
        NotImplementedError
            Raised by the base implementation because concrete data-point
            classes must define how their fields are decoded.
        """
        raise NotImplementedError

    def write_back(self, rom: Rom | None = None):
        """Encode the staged Python attributes back into ROM.

        Concrete implementations invert :meth:`read_values` by encoding the
        staged Python attributes back into ROM bytes at the data point's
        resolved addresses, either in the source ROM or in an alternate output
        ROM passed by the caller. This hook closes the lifecycle by pushing the
        in-memory edits gathered after construction back through the same
        address map that powered decoding.

        Parameters
        ----------
        rom : Rom | None, optional
            Alternate ROM target. When omitted, subclasses typically write back
            into ``self._rom``.

        Raises
        ------
        NotImplementedError
            Raised by the base implementation because concrete data-point
            classes must encode their fields.
        """
        raise NotImplementedError


# TODO change to using position? in the back end or front?
class _PositionMixin:
    """Add mutable position fields to a data-point class.

    The mixin keeps screen, column, and row values as ordinary attributes so
    subclasses can bind them to ROM addresses while still exposing a
    :class:`Position` view for higher-level editing workflows.

    Attributes
    ----------
    screen_address : int
        ROM address for the stored screen field, if applicable.
    screen : int
        Stored screen index.
    x_address : int
        ROM address for the stored column field, if applicable.
    x : int
        Stored column within the screen.
    y_address : int
        ROM address for the stored row field, if applicable.
    y : int
        Stored row within the screen.

    Parameters
    ----------
    *args
        Positional arguments forwarded to the next class in the MRO.
    **kwargs
        Keyword arguments forwarded to the next class in the MRO.

    See Also
    --------
    Position
        Immutable-ish value object used for tuple-style position exchange.
    """

    def __init__(self, *args, **kwargs):
        """Initialize coordinate fields before the concrete data point loads.

        The mixin seeds address and coordinate attributes early so later
        ``calculate_addresses`` and ``read_values`` calls can mutate them
        without needing to special-case missing storage.

        Parameters
        ----------
        *args
            Positional arguments forwarded to the next class in the MRO.
        **kwargs
            Keyword arguments forwarded to the next class in the MRO.
        """
        self.screen_address = 0x0
        self.screen = 0

        self.x_address = 0x0
        self.x = 0

        self.y_address = 0x0
        self.y = 0

        super(_PositionMixin, self).__init__(*args, **kwargs)

    @property
    def pos(self):
        """Package the stored coordinates as a ``Position`` object.

        This gives higher-level code a single value object without changing how
        subclasses store screen, row, and column fields internally or how ROM
        decoding keeps those fields split across multiple bytes.

        Returns
        -------
        Position
            Snapshot of the stored screen, column, and row values.
        """
        return Position(self.x, self.y, self.screen)

    @pos.setter
    def pos(self, value):
        """Copy coordinates from a ``Position`` into the mixin fields.

        Parameters
        ----------
        value : Position
            Position whose fields replace the stored coordinates.
        """
        self.x = value.x
        self.y = value.y
        self.screen = value.screen

    @property
    def row(self):
        """Expose ``y`` through row-oriented data-point terminology.

        This keeps world-map and level editors aligned with the vocabulary used
        by ROM metadata and user-facing coordinate displays.

        Returns
        -------
        int
            Stored row coordinate.
        """
        return self.y

    @row.setter
    def row(self, value):
        """Store ``y`` through row-oriented data-point terminology.

        Parameters
        ----------
        value : int
            Row coordinate to store.
        """
        self.y = value

    @property
    def column(self):
        """Expose ``x`` through column-oriented data-point terminology.

        This keeps callers in column-oriented workflows from depending on the
        mixin's stored ``x`` field name.

        Returns
        -------
        int
            Stored column coordinate.
        """
        return self.x

    @column.setter
    def column(self, value):
        """Store ``x`` through column-oriented data-point terminology.

        Parameters
        ----------
        value : int
            Column coordinate to store.
        """
        self.x = value

    @overload
    def is_at(self, position: Position) -> bool:
        """Compare the stored coordinates against a ``Position``.

        Parameters
        ----------
        position : Position
            Position to compare against the mixin's stored screen, row, and
            column.

        """

    @overload
    def is_at(self, screen: int, row: int, column: int) -> bool:
        """Compare the stored coordinates against explicit components.

        This overload keeps call sites that already have split ROM-style
        coordinates from allocating an intermediate :class:`Position`.

        Parameters
        ----------
        screen : int
            Screen index to compare.
        row : int
            Row value to compare.
        column : int
            Column value to compare.

        """

    def is_at(self, *args):
        """Compare the stored coordinates against another position.

        The overloads let callers stay in either ``Position`` space or raw
        coordinate space without duplicating comparison logic. Warning and edit
        workflows use this helper as a single predicate when matching a
        data-point record to map or level coordinates.

        Parameters
        ----------
        *args : Position | int
            Either one :class:`Position` instance or three integers in
            ``(screen, row, column)`` order.

        Returns
        -------
        bool
            ``True`` when all three coordinate components match.

        Raises
        ------
        ValueError
            Raised when the arguments do not describe exactly one valid
            position.
        """
        pos = self._pos_from_args(*args)

        return self.screen == pos.screen and self.column == pos.column and self.row == pos.row

    @overload
    def set_pos(self, position: "Position") -> None:
        """Update the mixin from a ``Position``.

        Parameters
        ----------
        position : Position
            Position whose screen, row, and column replace the stored values.
        """

    @overload
    def set_pos(self, screen: int, row: int, column: int) -> None:
        """Update the mixin from explicit screen, row, and column values.

        This overload supports callers that already operate on split ROM-style
        coordinates and need to update the record without building a
        :class:`Position` first.

        Parameters
        ----------
        screen : int
            Screen index to store.
        row : int
            Row value to store.
        column : int
            Column value to store.
        """

    def set_pos(self, *args):
        """Update the stored coordinates in place.

        This keeps callers from unpacking :class:`Position` instances just to
        feed the mixin's stored fields. Concrete data points use it when
        edits arrive from higher-level tools that may already have either a
        structured ``Position`` or split coordinate components and the record
        needs one mutation path before address-dependent write-back logic runs.

        Parameters
        ----------
        *args : Position | int
            Either one :class:`Position` instance or three integers in
            ``(screen, row, column)`` order.

        Raises
        ------
        ValueError
            Raised when the arguments do not describe exactly one valid
            position.
        AssertionError
            Raised when a provided argument has the wrong runtime type.
        """
        if len(args) == 1:
            position = args[0]
            assert isinstance(position, Position), position

            self.screen = position.screen
            self.column = position.column
            self.row = position.row

        elif len(args) == 3:
            assert all(isinstance(coord, int) for coord in args)
            self.screen, self.row, self.column = args

        else:
            raise ValueError("Method takes one Position object or three integers as screen, row, column.")

    @staticmethod
    def _pos_from_args(*args):
        """Normalize overloaded position arguments into a ``Position``.

        The helper gives ``is_at`` and ``set_pos`` one parsing path for both
        accepted call styles before comparison or mutation logic runs, so both
        public helpers apply identical validation and coordinate ordering.

        Parameters
        ----------
        *args : Position | int
            Either one :class:`Position` instance or three integers in
            ``(screen, row, column)`` order.

        Returns
        -------
        Position
            Parsed position object.

        Raises
        ------
        ValueError
            Raised when the arguments do not describe exactly one valid
            position.
        AssertionError
            Raised when a provided argument has the wrong runtime type.
        """
        if len(args) == 1:
            position = args[0]
            assert isinstance(position, Position), position

            return position

        elif len(args) == 3:
            assert all(isinstance(coord, int) for coord in args), args

            screen, row, column = args

            return Position(column, row, screen)

        else:
            raise ValueError("Method takes one Position object or three integers as screen, row, column.")


class _IndexedMixin:
    """Add index-driven address recalculation to a data-point class.

    Many ROM tables are addressed indirectly by an entry index rather than by a
    fixed absolute address. This mixin centralizes the common pattern of
    updating that index and then recalculating any dependent addresses before
    the caller reads or writes additional fields. Concrete data-point classes
    use it to preserve the same selection pipeline across construction and
    later edits: choose one logical table entry, resolve the ROM addresses that
    belong to that entry, then let decode or write-back operate against those
    refreshed addresses rather than stale offsets from a previous selection.

    Attributes
    ----------
    index : int
        Stored lookup-table or list index for the data point.
    """

    index: int

    def change_index(self, index: int):
        """Store a new index and refresh derived addresses.

        Concrete data points call this helper when an editor or parser selects
        a different table entry and every dependent address must be recomputed
        before the next read or write.

        Parameters
        ----------
        index : int
            New lookup-table index for the data point.
        """
        self.index = index

        self.calculate_addresses()

    def calculate_addresses(self):
        """Resolve addresses affected by the stored index.

        ``change_index`` calls this hook immediately after storing a new table
        position so dependent address fields stay in sync with the selected ROM
        record before any later decode or write-back step uses them.

        Raises
        ------
        NotImplementedError
            Raised by the mixin because subclasses must define how index
            changes affect their ROM addresses.
        """
        raise NotImplementedError
