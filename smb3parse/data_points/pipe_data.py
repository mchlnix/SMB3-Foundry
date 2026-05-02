"""Read and write world-map pipe exit pairs from SMB3 ROM data.

This module wraps the global pipe-exit tables that SMB3 uses for special
levels which send Mario from one world-map location to another. ``PipeData``
combines four ROM-backed nibble tables into two editable :class:`Position`
objects, one for the left pipe exit and one for the right pipe exit, then
pushes those changes back into the same global tables.

The class is usually reached from higher-level world-map editing code that
already knows which special-level object points at a pipe pair index. New
maintainers should read :mod:`smb3parse.data_points`, then the world-map level
models in :mod:`smb3parse.levels`, to see how these decoded positions are used.

See Also
--------
smb3parse.data_points.Position
    Tile and screen coordinate value object returned by the pipe accessors.
smb3parse.data_points.util.DataPoint
    Base ROM-backed data-point lifecycle used for address calculation and
    value loading.
"""

from smb3parse.constants import Constants
from smb3parse.data_points import Position
from smb3parse.data_points.util import DataPoint, _IndexedMixin
from smb3parse.levels import WORLD_MAP_SCREEN_WIDTH
from smb3parse.util.rom import Rom


class PipeData(_IndexedMixin, DataPoint):
    """Represent one ROM-backed world-map pipe exit pair.

    A special level can reference one entry in the global pipe table and use
    that entry to decide where the left and right pipes return Mario on the
    overworld. This class decodes the entry into editable left and right
    positions, keeps the split nibble fields synchronized while callers change
    screens or tile coordinates, and writes the updated fields back to ROM.

    Parameters
    ----------
    rom : Rom
        ROM image that owns the pipe-exit tables.
    index : int
        Pipe-pair slot to decode. Values wrap to the supported 7-bit range used
        by the SMB3 tables.

    Attributes
    ----------
    index : int
        Normalized table slot used to derive every backing ROM address.
    x_high_address : int
        ROM address of the nibble table that stores the high x bits for both
        exits in this slot.
    x_low_address : int
        ROM address of the nibble table that stores the low x bits for both
        exits in this slot.
    y_address : int
        ROM address of the nibble table that stores the y positions for both
        exits in this slot.
    scroll_and_x_high_address : int
        ROM address of the nibble table that stores the packed screen and
        scroll nibbles for both exits.
    x_high_left : int
        Decoded high x-position nibble for the left exit.
    x_high_right : int
        Decoded high x-position nibble for the right exit.
    x_low_left : int
        Decoded low x-position nibble for the left exit.
    x_low_right : int
        Decoded low x-position nibble for the right exit.
    y_left : int
        Decoded y tile position for the left exit.
    y_right : int
        Decoded y tile position for the right exit.
    scroll_and_x_high_left : int
        Packed left-exit screen nibble, including the unused half-screen scroll
        bit that the higher-level setters preserve only indirectly.
    scroll_and_x_high_right : int
        Packed right-exit screen nibble, including the unused half-screen
        scroll bit that the higher-level setters preserve only indirectly.
    screen_left : int
        Editable world-map screen index for the left exit, derived from the
        split x-position tables and mirrored back into the packed scroll table
        when callers retarget the exit.
    x_left : int
        Editable in-screen tile coordinate for the left exit.
    screen_right : int
        Editable world-map screen index for the right exit, derived from the
        split x-position tables and mirrored back into the packed scroll table
        when callers retarget the exit.
    x_right : int
        Editable in-screen tile coordinate for the right exit.
    left_pos : Position
        Computed view of the left exit as a single position value object.
    right_pos : Position
        Computed view of the right exit as a single position value object.

    Notes
    -----
    SMB3 stores pipe exits across several parallel nibble arrays instead of one
    packed record per pipe pair. ``PipeData`` exists to hide that layout from
    callers so they can work with coherent :class:`Position` values.

    The setter helpers preserve only the screen-number portion of the packed
    scroll nibble. The half-screen scroll bit is still present in the raw
    attributes, but the higher-level setters intentionally ignore it, matching
    the existing editor behavior.
    """

    def __init__(self, rom: Rom, index: int):
        """Decode one pipe-pair slot from the ROM-backed pipe tables.

        The constructor records the normalized index, prepares the field
        placeholders consumed by :class:`~smb3parse.data_points.util.DataPoint`,
        and then lets the base data-point lifecycle calculate addresses and
        load nibble values from the ROM.

        Parameters
        ----------
        rom : Rom
            ROM image that contains the global pipe-exit tables.
        index : int
            Requested pipe-pair index before it is wrapped into the ROM's
            7-bit slot range.
        """
        self.index = index % 0x80

        self.x_high_address = 0x0
        self.x_high_left = 0
        self.x_high_right = 0

        self.x_low_address = 0x0
        self.x_low_left = 0
        self.x_low_right = 0

        self.y_address = 0x0
        self.y_left = 0
        self.y_right = 0

        self.scroll_and_x_high_address = 0x0
        self.scroll_and_x_high_left = 0
        """Packed left-exit screen nibble copied from the ROM table."""

        self.scroll_and_x_high_right = 0
        """Packed right-exit screen nibble copied from the ROM table.

        Each nibble combines the exit screen number with the half-screen scroll
        flag used by SMB3's overworld pipe transitions.
        """

        super(PipeData, self).__init__(rom)

    def change_index(self, index: int):
        """Retarget this data point to a different pipe-pair slot.

        Parameters
        ----------
        index : int
            New pipe-pair slot. Values wrap to the ROM's supported 7-bit range
            before the base class recalculates addresses and reloads data.

        Notes
        -----
        The normalized index intentionally drops any higher bits that callers
        might pass, matching the fixed-size global table in SMB3.
        """
        index %= 0x80
        super(PipeData, self).change_index(index)

    def calculate_addresses(self):
        """ROM addresses for this instance's pipe-pair slot.

        The base data-point lifecycle calls this before ``read_values`` so the
        subsequent nibble reads come from the correct parallel tables.
        """
        self.x_high_address = Constants.PipewayCtlr_MapXHi + self.index
        self.x_low_address = Constants.PipewayCtlr_MapX + self.index

        self.y_address = Constants.PipewayCtlr_MapY + self.index

        self.scroll_and_x_high_address = Constants.PipewayCtlr_MapScrlXHi + self.index

    def read_values(self):
        """Load the left and right exit fields from the ROM tables.

        The four table reads reconstruct the editable state that the position
        properties expose later in the workflow.
        """
        self.x_high_left, self.x_high_right = self._rom.nibbles(self.x_high_address)
        self.x_low_left, self.x_low_right = self._rom.nibbles(self.x_low_address)

        self.y_left, self.y_right = self._rom.nibbles(self.y_address)

        self.scroll_and_x_high_left, self.scroll_and_x_high_right = self._rom.nibbles(self.scroll_and_x_high_address)

    def write_back(self, rom: Rom | None = None):
        """Persist the edited exit pair back into ROM.

        Parameters
        ----------
        rom : Rom | None, optional
            Alternate ROM target. When omitted, the instance writes back to the
            ROM it originally decoded from.
        """
        if rom is None:
            rom = self._rom

        rom.write_nibbles(self.x_high_address, self.x_high_left, self.x_high_right)
        rom.write_nibbles(self.x_low_address, self.x_low_left, self.x_low_right)

        rom.write_nibbles(self.y_address, self.y_left, self.y_right)

        rom.write_nibbles(
            self.scroll_and_x_high_address,
            self.scroll_and_x_high_left,
            self.scroll_and_x_high_right,
        )

    @property
    def _combined_left_x(self):
        """Decoded full x coordinate for the left exit.

        This property bridges the ROM's split x nibbles
        and the higher-level screen and tile setters that edit the left exit.

        Returns
        -------
        int
            Full left-exit x position measured in world-map tiles.
        """
        return (self.x_high_left << 4) + self.x_low_left

    @_combined_left_x.setter
    def _combined_left_x(self, value):
        """Split a left-exit x coordinate back into ROM nibble fields.

        Parameters
        ----------
        value : int
            Full left-exit x position measured in world-map tiles.
        """
        self.x_high_left = value >> 4
        self.x_low_left = value & 0x0F

    @property
    def _combined_right_x(self):
        """Expose the full right-exit x position as one decoded tile coordinate.

        This property lets the right-exit screen and tile accessors work
        against one reconstructed coordinate instead of repeating nibble math.

        Returns
        -------
        int
            Full right-exit x position measured in world-map tiles.
        """
        return (self.x_high_right << 4) + self.x_low_right

    @_combined_right_x.setter
    def _combined_right_x(self, value):
        """Split a right-exit x coordinate back into ROM nibble fields.

        Parameters
        ----------
        value : int
            Full right-exit x position measured in world-map tiles.
        """
        self.x_high_right = value >> 4
        self.x_low_right = value & 0x0F

    @property
    def screen_left(self):
        """World-map screen number for the left exit.

        The value is derived from the decoded x coordinate so callers can edit
        the left exit in screen-relative terms before the instance is written
        back to ROM.

        Returns
        -------
        int
            Screen index derived from the combined left-exit x position.
        """
        return self._combined_left_x // WORLD_MAP_SCREEN_WIDTH

    @screen_left.setter
    def screen_left(self, value):
        """Move the left exit to a different screen without changing tile offset.

        Parameters
        ----------
        value : int
            New world-map screen index for the left exit.

        Notes
        -----
        This setter updates both the split x fields and the packed scroll/screen
        nibble so later ``write_back`` calls preserve the new screen choice.
        """
        new_comb_x = self._combined_left_x % WORLD_MAP_SCREEN_WIDTH
        new_comb_x += value * WORLD_MAP_SCREEN_WIDTH

        self._combined_left_x = new_comb_x

        self.scroll_and_x_high_left = value

    @property
    def x_left(self):
        """Tile offset for the left exit inside its decoded screen.

        This separates the in-screen tile coordinate from the packed screen
        number so editors can adjust the left exit without recomputing nibble
        fields themselves.

        Returns
        -------
        int
            Tile coordinate inside the left exit's current screen.
        """
        return self._combined_left_x % WORLD_MAP_SCREEN_WIDTH

    @x_left.setter
    def x_left(self, value):
        """Change the left exit's tile offset within its current screen.

        Parameters
        ----------
        value : int
            New in-screen tile coordinate for the left exit.
        """
        self._combined_left_x = self.screen_left * WORLD_MAP_SCREEN_WIDTH + value

    @property
    def screen_right(self):
        """World-map screen number for the right exit.

        The value is derived from the decoded x coordinate so callers can edit
        the right exit in screen-relative terms before the instance is written
        back to ROM.

        Returns
        -------
        int
            Screen index derived from the combined right-exit x position.
        """
        return self._combined_right_x // WORLD_MAP_SCREEN_WIDTH

    @screen_right.setter
    def screen_right(self, value):
        """Move the right exit to a different screen without changing tile offset.

        Parameters
        ----------
        value : int
            New world-map screen index for the right exit.

        Notes
        -----
        As with ``screen_left``, this keeps the decomposed nibble fields and the
        packed scroll/screen table entry in sync for later ROM writes.
        """
        new_comb_x = self._combined_right_x % WORLD_MAP_SCREEN_WIDTH
        new_comb_x += value * WORLD_MAP_SCREEN_WIDTH

        self._combined_right_x = new_comb_x

        self.scroll_and_x_high_right = value

    @property
    def x_right(self):
        """Tile offset for the right exit inside its decoded screen.

        This separates the in-screen tile coordinate from the packed screen
        number so editors can adjust the right exit without recomputing nibble
        fields themselves.

        Returns
        -------
        int
            Tile coordinate inside the right exit's current screen.
        """
        return self._combined_right_x % WORLD_MAP_SCREEN_WIDTH

    @x_right.setter
    def x_right(self, value):
        """Change the right exit's tile offset within its current screen.

        Parameters
        ----------
        value : int
            New in-screen tile coordinate for the right exit.
        """
        self._combined_right_x = self.screen_right * WORLD_MAP_SCREEN_WIDTH + value

    @property
    def left_pos(self):
        """Build the editable world-map position for the left pipe exit.

        Callers typically use this accessor after ``read_values`` has decoded
        the nibble tables, pass the resulting :class:`Position` through editor
        workflows, and then let a later ``write_back`` persist any mutations.

        Returns
        -------
        Position
            Position object reconstructed from the left exit's x, y, and screen
            fields.
        """
        return Position(self.x_left, self.y_left, self.screen_left)

    @left_pos.setter
    def left_pos(self, value: Position):
        """Replace the decoded world-map position for the left pipe exit.

        Parameters
        ----------
        value : Position
            New position to decompose into the left exit's screen, x, and y
            fields before a later ``write_back`` call.
        """
        self.x_left = value.x
        self.y_left = value.y
        self.screen_left = value.screen

    @property
    def right_pos(self):
        """Build the editable world-map position for the right pipe exit.

        Callers typically use this accessor after ``read_values`` has decoded
        the nibble tables, pass the resulting :class:`Position` through editor
        workflows, and then let a later ``write_back`` persist any mutations.

        Returns
        -------
        Position
            Position object reconstructed from the right exit's x, y, and
            screen fields.
        """
        return Position(self.x_right, self.y_right, self.screen_right)

    @right_pos.setter
    def right_pos(self, value: Position):
        """Replace the decoded world-map position for the right pipe exit.

        Parameters
        ----------
        value : Position
            New position to decompose into the right exit's screen, x, and y
            fields before a later ``write_back`` call.
        """
        self.x_right = value.x
        self.y_right = value.y
        self.screen_right = value.screen
