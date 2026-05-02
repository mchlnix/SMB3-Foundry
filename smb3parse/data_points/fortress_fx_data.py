"""Parse fortress-triggered world-map tile replacements.

This module models the SMB3 tables that swap one overworld tile for another
after a fortress orb clears a gate, lock, or bridge. ``FortressFXData`` keeps
the row and column coordinates, replacement block metadata, completion-bit
index, and VRAM tile pointers synchronized so callers can inspect or rewrite a
single fortress effect entry as one unit.

See Also
--------
smb3parse.data_points.sprite_data : Reads the sprite pointer tables that drive
    other world-map progression data.
smb3parse.levels.world_map : Consumes the decoded world-map coordinates and
    tile behavior that these replacement entries modify.
"""

from smb3parse.constants import Constants
from smb3parse.data_points.util import DataPoint, _IndexedMixin, _PositionMixin
from smb3parse.levels import FIRST_VALID_ROW
from smb3parse.util.rom import Rom


class FortressFXData(_PositionMixin, _IndexedMixin, DataPoint):
    """Represent one fortress-cleared overworld replacement entry.

    The game keeps several parallel tables for fortress effects: map position,
    replacement graphics, replacement block behavior, completion-bit tracking,
    and VRAM addresses for the live tile swap. This class groups those tables
    so tooling can edit one fortress effect without recomputing each offset by
    hand.

    Parameters
    ----------
    rom : Rom
        ROM view that supplies the fortress-effect tables and receives any
        updates written back by :meth:`write_back`.
    index : int
        Zero-based entry index inside the fortress-effect tables.

    Attributes
    ----------
    index : int
        Zero-based index into every fortress-effect table.
    row_address : int
        ROM address of the nibble that stores the replacement tile row.
    row : int
        Map row of the tile to replace, including the two border rows used by
        the overworld layout tables.
    col_and_screen_address : int
        ROM address of the packed column and screen byte.
    column : int
        Column of the tile to replace within the selected screen.
    screen : int
        World-map screen that owns the replacement tile.
    tile_indexes_address : int
        ROM address of the four 8x8 pattern indexes used for the replacement
        tile graphic.
    tile_indexes : bytearray
        Four pattern-table indexes that redraw the tile after the fortress is
        cleared.
    replacement_block_address : int
        ROM address of the replacement block-behavior index.
    replacement_block_index : int
        Overworld TSA block index that controls collision and level-entry
        behavior after the swap.
    map_completion_data_address : int
        ROM address of the two-byte map-completion entry for this fortress
        effect.
    map_completion_bit_index : int
        Bit mask written into the map-completion byte so the game can mark the
        effect as consumed.
    v_addr_high_address : int
        ROM address of the high byte of the VRAM tile pointer used for the live
        map update.
    v_addr_high : int
        High byte of the VRAM tile pointer for the replacement tile graphic.
    v_addr_low_address : int
        ROM address of the low byte of the VRAM tile pointer used for the live
        map update.
    v_addr_low : int
        Low byte of the VRAM tile pointer for the replacement tile graphic.

    Notes
    -----
    Fortress effects replace both the visible 16x16 tile graphic and the
    underlying TSA block behavior. That split is why the entry stores both
    ``tile_indexes`` and ``replacement_block_index``.
    """

    def __init__(self, rom: Rom, index: int):
        """Decode one fortress-effect entry from the ROM tables.

        The constructor seeds placeholder fields for every parallel fortress
        table and then hands control to the shared :class:`DataPoint`
        initialization flow, which resolves addresses and fills those fields
        from ROM immediately.

        Parameters
        ----------
        rom : Rom
            ROM view that provides the fortress-effect tables.
        index : int
            Zero-based fortress-effect entry to decode.

        Notes
        -----
        The constructor seeds every decoded field, records the entry index, and
        then delegates to :class:`~smb3parse.data_points.util.DataPoint` so the
        shared data-point lifecycle can call :meth:`calculate_addresses` and
        :meth:`read_values`. Callers receive a fully decoded entry rather than a
        partially initialized wrapper around raw offsets.
        """
        self.index = index

        self.row_address = 0x0
        self.row = 0

        self.col_and_screen_address = 0x0
        self.column = 0

        self.screen = 0

        self.tile_indexes_address = 0x0
        self.tile_indexes = bytearray([0x00, 0x00, 0x00, 0x00])

        self.replacement_block_address = 0x0
        self.replacement_block_index = 0

        self.map_completion_data_address = 0x0
        self.map_completion_bit_index = 0x0

        self.v_addr_high_address = 0x0
        self.v_addr_high = 0x0

        self.v_addr_low_address = 0x0
        self.v_addr_low = 0x0

        super(FortressFXData, self).__init__(rom)

    def calculate_addresses(self):
        """Resolve the ROM addresses for this fortress-effect entry.

        Each fortress effect is spread across synchronized ROM tables. This
        method converts the entry index into concrete addresses so later read
        and write steps stay aligned to the same replacement effect. The method
        updates every ``*_address`` attribute in one batch, establishing the
        state that :meth:`read_values` consumes and :meth:`write_back` later
        reuses when persisting edits.

        Notes
        -----
        The fortress-effect tables are parallel arrays keyed by ``index``.
        This method converts that shared entry index into the row, packed
        position, pattern, TSA block, completion-bit, and VRAM-pointer
        addresses that :meth:`read_values` and :meth:`write_back` use.
        """
        self.row_address = Constants.FortressFX_MapLocationRow + self.index
        self.col_and_screen_address = Constants.FortressFX_MapLocation + self.index

        self.tile_indexes_address = Constants.FortressFX_Patterns + self.index * 4  # tiles in block
        self.replacement_block_address = Constants.FortressFX_MapTileReplace + self.index

        # ignore the column value of the map completion data, because it is the same as the screen and column position
        self.map_completion_data_address = Constants.FortressFX_MapCompIdx + self.index * 2

        self.v_addr_high_address = Constants.FortressFX_VAddrH + self.index
        self.v_addr_low_address = Constants.FortressFX_VAddrL + self.index

    def read_values(self):
        """Read the decoded fortress-effect values from the ROM tables.

        This is the decode step of the data-point lifecycle. After
        :meth:`calculate_addresses` pins every table offset, ``read_values``
        gathers the scattered bytes and nibbles into one editable world-map
        replacement record.

        Notes
        -----
        The row byte, packed column and screen byte, graphic tile indexes,
        replacement block, completion bit, and VRAM pointer bytes live in
        separate tables. This method pulls them back together into the instance
        fields used by editors and serializers.
        """
        self.row, _ = self._rom.nibbles(self.row_address)
        self.column, self.screen = self._rom.nibbles(self.col_and_screen_address)

        self.tile_indexes = self._rom.read(self.tile_indexes_address, 4)
        self.replacement_block_index = self._rom.int(self.replacement_block_address)

        # ignore the column value of the map completion data, because it is the same as the screen and column position
        self.map_completion_bit_index = self._rom.int(self.map_completion_data_address + 1)

        self.v_addr_high = self._rom.int(self.v_addr_high_address)
        self.v_addr_low = self._rom.int(self.v_addr_low_address)

    def write_back(self, rom: Rom | None = None):
        """Persist the edited fortress-effect entry back into ROM tables.

        This is the inverse of :meth:`read_values`: it takes the in-memory
        replacement record, recomputes the derived completion and VRAM fields,
        and pushes the synchronized values back into the ROM tables the game
        consumes.

        Parameters
        ----------
        rom : Rom or None, optional
            Alternate ROM target to receive the serialized fortress-effect
            entry. When omitted, the instance writes back into the ROM it was
            decoded from.

        Notes
        -----
        The write path mirrors :meth:`read_values`, but it also recomputes two
        derived values before storing them:

        - ``map_completion_bit_index`` is regenerated from ``row`` because the
          game derives the completion bit from the row band used by fortress
          exits.
        - ``v_addr_high`` and ``v_addr_low`` are regenerated from ``row`` and
          ``column`` so the live world-map renderer can patch the correct tile
          without reloading the whole map.
        """
        if rom is None:
            rom = self._rom

        rom.write_nibbles(self.row_address, self.row)
        rom.write_nibbles(self.col_and_screen_address, self.column, self.screen)

        rom.write(self.tile_indexes_address, self.tile_indexes)
        rom.write(self.replacement_block_address, self.replacement_block_index)

        rom.write_nibbles(self.map_completion_data_address, self.screen, self.column)

        # 8 is not a valid row for any level pointer, row 9 has its value
        self.map_completion_bit_index = 0x80 >> min(self.row - FIRST_VALID_ROW, 0x08)

        rom.write(self.map_completion_data_address + 1, self.map_completion_bit_index)

        # TODO find reasons for numbers; 32 * 4 screens * 8?
        v_addr_offset = 0x2800 + (self.row * 32 + self.column) * 2

        rom.write(self.v_addr_high_address, v_addr_offset >> 8)
        rom.write(self.v_addr_low_address, v_addr_offset & 0x00FF)

    def __eq__(self, other):
        """Compare the user-visible identity of two fortress-effect entries.

        Equality intentionally follows editor-relevant state rather than every
        cached address field. Two entries compare equal when they describe the
        same indexed replacement effect at the same map position with the same
        resulting block behavior.

        Parameters
        ----------
        other : object
            Candidate value to compare against this fortress-effect entry.

        Returns
        -------
        bool
            ``True`` when both entries point at the same indexed effect, world
            position, and replacement block behavior.
        """
        if self.index != other.index:
            return False

        if self.pos != other.pos:
            return False

        if self.replacement_block_index != other.replacement_block_index:
            return False

        return True
