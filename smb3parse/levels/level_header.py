"""Decode SMB3 level headers into editor-facing layout and jump metadata.

This module unpacks the raw nine-byte SMB3 level header into the fields the
parser, editor, and ROM-rewrite path actually consume: level dimensions,
palette and music indexes, Mario start metadata, and the jump destinations for
linked areas. ``LevelHeader`` is the point where packed header bytes stop
being treated as bitfields and start being treated as named parser state.

Mario start positions need a second translation step because the header stores
lookup-table indexes instead of tile coordinates. ``LevelHeader`` keeps both
representations available so callers can move between ROM encoding, editor
coordinates, and rewritten header bytes without reimplementing the table math.

See Also
--------
smb3parse.objects.object_set.ObjectSet
    Resolves the object-set-relative level pointer stored by the header.
smb3parse.util.rom.Rom
    ROM access wrapper passed through to object-set resolution.
"""

from enum import IntEnum
from itertools import product

from smb3parse.levels import (
    DEFAULT_HORIZONTAL_HEIGHT,
    DEFAULT_VERTICAL_WIDTH,
    ENEMY_BASE_OFFSET,
    HEADER_LENGTH,
    LEVEL_LENGTH_INTERVAL,
    LEVEL_MIN_LENGTH,
)
from smb3parse.objects.object_set import ObjectSet
from smb3parse.util.rom import Rom

MARIO_X_POSITIONS = [0x18, 0x70, 0xD8, 0x80]  # 0x10249
MARIO_Y_POSITIONS = [
    0x17,
    0x04,
    0x00,
    0x14,
    0x07,
    0x0B,
    0x0F,
    0x18,
]  # 0x3D7A0 + 0x3D7A8


class MarioStartAction(IntEnum):
    """Enumerate the start action encoded in the level header.

    SMB3 stores Mario's entry behavior in the high three bits of header byte
    seven, alongside the graphic-set index that occupies the low five bits.
    ``LevelHeader`` decodes that compact field into this enum so parser,
    editor, and rendering code can share named values while the underlying
    integer values remain identical to the ROM encoding.

    The enum exists as a round-trip boundary rather than a behavior model:
    :class:`LevelHeader` reads ``data[7]`` into ``start_action``, callers may
    inspect or replace that value during header editing, and the surrounding
    level write-back path can pack the same integer value back into the header
    without maintaining a separate translation table. Keep the member values in
    encoded order so UI dropdown indexes, sprite-strip selection, and header
    serialization continue to agree.

    Attributes
    ----------
    Stand
        Mario begins in the default standing state.
    Sliding
        Mario begins in a sliding state.
    FromPipeUpwards
        Mario emerges upward from a pipe.
    FromPipeDownwards
        Mario emerges downward from a pipe.
    FromPipeRight
        Mario emerges from a pipe facing right.
    FromPipeLeft
        Mario emerges from a pipe facing left.
    ShipTransition
        Mario begins during an airship transition sequence.
    ShipAutoScrolling
        Mario begins in an auto-scrolling airship sequence.

    See Also
    --------
    LevelHeader
        Decodes the packed header byte that selects one of these actions and
        keeps it paired with the adjacent graphic-set field.
    smb3parse.levels.level_header.MARIO_X_POSITIONS
        Start-position lookup table used by the neighboring Mario start
        fields.
    smb3parse.levels.level_header.MARIO_Y_POSITIONS
        Start-position lookup table used by the neighboring Mario start
        fields.
    """

    Stand = 0
    Sliding = 1
    FromPipeUpwards = 2
    FromPipeDownwards = 3
    FromPipeRight = 4
    FromPipeLeft = 5
    ShipTransition = 6
    ShipAutoScrolling = 7


class LevelHeader:
    """Decode one SMB3 level header and expose its editor-relevant fields.

    The class keeps the original header bytes while decoding commonly used
    fields into editor-friendly attributes. It also exposes helpers for
    translating Mario's encoded start indexes to the tile coordinates used by
    the UI and for converting jump offsets into absolute ROM addresses.

    Parameters
    ----------
    rom : Rom
        ROM wrapper used when resolving object-set-relative level addresses.
    header_bytes : bytearray
        Raw header bytes. The value must be exactly
        :data:`smb3parse.levels.HEADER_LENGTH` bytes long.

    Raises
    ------
    ValueError
        Raised when ``header_bytes`` does not contain exactly one full header.

    Attributes
    ----------
    data : bytearray
        Original header bytes retained for callers that still need raw access.
    start_x_index : int
        Encoded index into :data:`MARIO_X_POSITIONS`.
    start_y_index : int
        Encoded index into :data:`MARIO_Y_POSITIONS`.
    screens : int
        Number of screen intervals encoded by the header length nibble.
    length : int
        Tile length derived from ``screens``.
    width : int
        Horizontal tile span presented to the editor.
    height : int
        Vertical tile span presented to the editor.
    enemy_palette_index : int
        Enemy palette selection nibble.
    object_palette_index : int
        Object palette selection nibble.
    pipe_ends_level : bool
        Whether entering the pipe ends the level.
    scroll_type_index : int
        Encoded scroll behavior selection.
    is_vertical : bool
        Whether the level uses the vertical layout interpretation.
    start_action : MarioStartAction
        Starting animation or transition state for Mario.
    graphic_set_index : int
        Encoded graphic set selection.
    time_index : int
        Encoded timer selection.
    music_index : int
        Encoded music selection.
    jump_level_offset : int
        Object-set-relative offset for the destination level data.
    jump_enemy_offset : int
        Offset for the destination enemy data relative to
        :data:`smb3parse.levels.ENEMY_BASE_OFFSET`.

    See Also
    --------
    MarioStartAction
        Enum used for the encoded Mario entry-state field.
    ObjectSet
        Resolves the object-set-relative jump destination stored by the
        header.
    """

    def __init__(self, rom: Rom, header_bytes: bytearray):
        """Decode a raw level header.

        The constructor performs the full header decode in the same order the
        parser later consumes it. It first validates that the caller supplied
        exactly one header, then keeps those bytes as ``data`` for any code
        that still needs the packed representation. From there it unpacks the
        start-position indexes, layout and palette flags, vertical-level
        geometry adjustments, jump object-set state, and the level/enemy jump
        offsets. The result is a header object that preserves the original ROM
        bytes while also exposing editor-facing fields that can be inspected,
        mutated, and written back through the surrounding level workflow.

        Parameters
        ----------
        rom : Rom
            ROM wrapper used when resolving object-set metadata.
        header_bytes : bytearray
            Raw header bytes to decode.

        Raises
        ------
        ValueError
            Raised when ``header_bytes`` is not exactly one SMB3 header long.
        """

        if len(header_bytes) != HEADER_LENGTH:
            raise ValueError(f"A level header is made up of {HEADER_LENGTH} bytes, but {len(header_bytes)} were given.")

        self._rom = rom

        self.data = header_bytes

        self.start_y_index = (self.data[4] & 0b1110_0000) >> 5

        self.screens = self.data[4] & 0b0000_1111
        self.length = LEVEL_MIN_LENGTH + self.screens * LEVEL_LENGTH_INTERVAL
        self.width = self.length
        self.height = DEFAULT_HORIZONTAL_HEIGHT

        self.start_x_index = (self.data[5] & 0b0110_0000) >> 5

        self.enemy_palette_index = (self.data[5] & 0b0001_1000) >> 3
        self.object_palette_index = self.data[5] & 0b0000_0111

        self.pipe_ends_level = not (self.data[6] & 0b1000_0000)
        self.scroll_type_index = (self.data[6] & 0b0110_0000) >> 5
        self.is_vertical = bool(self.data[6] & 0b0001_0000)

        if self.is_vertical:
            self.height = self.length
            self.width = DEFAULT_VERTICAL_WIDTH

        self._jump_object_set_number = self.data[6] & 0b0000_1111  # for indexing purposes
        self._jump_object_set = ObjectSet(rom, self.jump_object_set_number)

        self.start_action = MarioStartAction((self.data[7] & 0b1110_0000) >> 5)

        self.graphic_set_index = self.data[7] & 0b0001_1111

        self.time_index = (self.data[8] & 0b1100_0000) >> 6

        self.music_index = self.data[8] & 0b0000_1111

        self.jump_level_offset = (self.data[1] << 8) + self.data[0]
        self.jump_enemy_offset = (self.data[3] << 8) + self.data[2]

    def position_from_start_index(self, start_x_index: int, start_y_index: int):
        """Translate encoded Mario start indexes into tile coordinates.

        The header stores indexes into fixed ROM lookup tables. This helper
        resolves those indexes into the tile coordinates used by editing and
        inspection code.

        Parameters
        ----------
        start_x_index : int
            Index into :data:`MARIO_X_POSITIONS`.
        start_y_index : int
            Index into :data:`MARIO_Y_POSITIONS`.

        Returns
        -------
        tuple[int, int]
            Mario's start position in tile coordinates as ``(x, y)``.

        Notes
        -----
        Vertical levels add ``(screens - 1) * 15`` tiles to the decoded Y
        position. This matches the parser's current editor-facing coordinate
        convention and keeps round-tripping consistent with
        :meth:`start_indexes_from_position`.
        """

        x = MARIO_X_POSITIONS[start_x_index] >> 4
        y = MARIO_Y_POSITIONS[start_y_index]

        if self.is_vertical:
            y += (self.screens - 1) * 15  # TODO: Why?

        return x, y

    def start_indexes_from_position(self, x, y):
        """Encode a tile-space Mario start position back into header indexes.

        This is the inverse of :meth:`position_from_start_index`. It is useful
        when an editor control chooses a concrete tile position and the header
        must be rewritten using the limited start-position tables available in
        the ROM. The method first matches the X table entry, then normalizes Y
        back into the header's vertical-level frame of reference before
        searching the Y table. Callers use the returned pair when replacing
        ``start_x_index`` and ``start_y_index`` after an editor action picks a
        new visible Mario start tile.

        Parameters
        ----------
        x : int
            Mario's X position in tiles.
        y : int
            Mario's Y position in tiles.

        Returns
        -------
        tuple[int, int]
            Encoded ``(start_x_index, start_y_index)`` pair for the header.

        Raises
        ------
        ValueError
            Raised when ``x`` or ``y`` cannot be represented by the header's
            fixed Mario-start lookup tables.

        Notes
        -----
        Editor code uses this method on the write path after a visible Mario
        start tile has already been chosen. The returned indexes are therefore
        the exact header-side values that must replace ``start_x_index`` and
        ``start_y_index`` before the decoded position can round-trip back into
        ROM bytes. The surrounding workflow is therefore: choose a tile-space
        start in editor coordinates, translate it through this lookup, then
        persist the resulting indexes back into the packed header fields.
        """

        for index, default_x in enumerate(MARIO_X_POSITIONS):
            if default_x >> 4 == x:
                start_x_index = index
                break
        else:
            raise ValueError(f"No possible start indexes for {x} and {y}.")

        if self.is_vertical:
            y -= (self.screens - 1) * 15

        try:
            start_y_index = MARIO_Y_POSITIONS.index(y)
        except ValueError:
            raise ValueError(f"No possible start indexes for {x} and {y}.")

        return start_x_index, start_y_index

    def gen_mario_start_positions(self):
        """Yield every Mario start position representable by the header.

        Callers can use this generator to populate UI choices or validate a
        candidate position against the finite start-position tables.

        Yields
        ------
        tuple[int, int]
            Tile coordinates for one valid Mario start position.
        """

        for x_index, y_index in product(range(len(MARIO_X_POSITIONS)), range(len(MARIO_Y_POSITIONS))):
            yield self.position_from_start_index(x_index, y_index)

    def mario_position(self):
        """Resolve the tile position selected by the stored header indexes.

        This convenience helper resolves :attr:`start_x_index` and
        :attr:`start_y_index` using the same translation rules used elsewhere
        in the parser.

        Returns
        -------
        tuple[int, int]
            Tile coordinates for the header's current Mario start indexes.
        """

        return self.position_from_start_index(self.start_x_index, self.start_y_index)

    @property
    def mario_start_indexes(self):
        """Expose the stored Mario start indexes without coordinate conversion.

        Callers that need the raw header encoding can use this property instead
        of re-reading the packed bit fields from :attr:`data`.

        Returns
        -------
        tuple[int, int]
            Encoded ``(start_x_index, start_y_index)`` pair preserved in the
            raw header fields.
        """

        return self.start_x_index, self.start_y_index

    @property
    def jump_level_address(self):
        """Resolve the absolute ROM address for the jump level data.

        The header stores this destination as an object-set-relative offset.
        This property resolves that offset against the object set identified by
        :attr:`jump_object_set_number`, which is the form callers need when
        following a jump from one decoded header to the next level payload or
        when comparing a rewritten jump target against ROM addresses elsewhere
        in the parser.

        Returns
        -------
        int
            Absolute ROM address for the destination level data.

        Notes
        -----
        This property is the read-side bridge between two representations of
        the same jump target: the header stores an object-set-relative offset,
        while downstream parser and editor code follow or compare absolute ROM
        addresses. Callers use this property when they move from decoded header
        metadata into loading, validation, or rewrite flows for the destination
        level. A typical read path is: inspect the decoded header, dereference
        this property to recover an absolute destination, then hand that
        address to the next level-load or comparison step.
        """

        return self.jump_object_set.level_offset + self.jump_level_offset

    @jump_level_address.setter
    def jump_level_address(self, value):
        """Store a jump destination as an object-set-relative level offset.

        The setter accepts the absolute ROM address used by higher-level
        parsing and editing code, then converts it back into the relative value
        that the header actually stores for the selected jump object
        set.

        Parameters
        ----------
        value : int
            Absolute ROM address for the level data destination.
        """

        self.jump_level_offset = value - self.jump_object_set.level_offset

    @property
    def jump_enemy_address(self):
        """Resolve the absolute ROM address for the jump enemy data.

        The header stores the enemy target relative to
        :data:`smb3parse.levels.ENEMY_BASE_OFFSET`. This property resolves the
        absolute address expected by callers that inspect or rewrite the enemy
        payload paired with the jump destination, so the surrounding parser can
        move between packed header bytes and absolute ROM enemy pointers
        without repeating the base-offset calculation.

        Returns
        -------
        int
            Absolute ROM address for the destination enemy data.

        Notes
        -----
        This property performs the same representation bridge for enemy data
        that :attr:`jump_level_address` performs for level data. Parser flows
        use the resolved address after header decode when they need to inspect,
        compare, or rewrite the enemy payload paired with the jump target. In
        practice the lifecycle is: decode the header, resolve this property
        into an absolute ROM address, then pass that address into the next
        enemy-stream load, validation, or rewrite step for the jump target.
        """

        return self.jump_enemy_offset + ENEMY_BASE_OFFSET

    @jump_enemy_address.setter
    def jump_enemy_address(self, value):
        """Store a jump destination as an enemy-data-relative offset.

        The setter converts the absolute enemy-data address used by higher
        layers back into the offset that the header stores relative to
        :data:`smb3parse.levels.ENEMY_BASE_OFFSET`.

        Parameters
        ----------
        value : int
            Absolute ROM address for the enemy data destination.
        """

        self.jump_enemy_offset = value - ENEMY_BASE_OFFSET

    @property
    def jump_object_set_number(self):
        """Expose the encoded object set number used for jump resolution.

        Callers can inspect this property before changing object-set-relative
        level pointers or when mirroring the original header encoding in a UI.
        The value is the boundary between the raw header nibble and the
        :class:`~smb3parse.objects.object_set.ObjectSet` metadata needed to
        resolve jump-level addresses.

        Returns
        -------
        int
            Object set number that determines how
            :attr:`jump_level_offset` maps to an absolute ROM address.
        """

        return self._jump_object_set_number

    @jump_object_set_number.setter
    def jump_object_set_number(self, value):
        """Update the encoded object set number used for jump resolution.

        Callers update this property before storing a new jump level address
        when the destination level belongs to a different object set. The
        header keeps only the numeric object-set selector, so later reads of
        :attr:`jump_object_set` and :attr:`jump_level_address` will rebuild
        their view from this value.

        Parameters
        ----------
        value : int
            Object set number stored in the header.
        """

        self._jump_object_set_number = value

    @property
    def jump_object_set(self):
        """Build the object set implied by :attr:`jump_object_set_number`.

        The property constructs an
        :class:`~smb3parse.objects.object_set.ObjectSet` on demand so address
        resolution always reflects the encoded object set number currently
        stored on the header. This keeps the parsed metadata synchronized with
        callers that mutate :attr:`jump_object_set_number` before re-reading or
        rewriting the jump addresses, and it is the object callers dereference
        before converting :attr:`jump_level_offset` into an absolute target.

        Returns
        -------
        smb3parse.objects.object_set.ObjectSet
            Object-set metadata used to resolve jump level addresses.

        Notes
        -----
        The object set is rebuilt on each access so reads always reflect the
        latest encoded object-set number. That keeps later jump-address
        resolution synchronized with callers that update
        :attr:`jump_object_set_number` before re-reading or rewriting the jump
        target. The common lifecycle is: mutate the encoded selector, read this
        property again, then resolve :attr:`jump_level_address` against the new
        object-set metadata.
        """

        return ObjectSet(self._rom, self._jump_object_set_number)
