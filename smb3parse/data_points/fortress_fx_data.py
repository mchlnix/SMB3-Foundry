from typing import Optional

from smb3parse.constants import Constants
from smb3parse.data_points.util import DataPoint, _IndexedMixin, _PositionMixin
from smb3parse.levels import FIRST_VALID_ROW
from smb3parse.util.rom import Rom


class FortressFXData(_PositionMixin, _IndexedMixin, DataPoint):
    """
    Fortress FX data, describes the mechanism of replacing a Tile on the World Map with another, after collecting the
    Orb object, upon defeating a Fortress Boss.

    This is most commonly used to replace Locks with pathways and open Bridges with closed ones, allowing access to
    previously blocked off places on the Map.


    """

    def __init__(self, rom: Rom, index: int):
        self.index = index

        self.row_address = 0x0
        self.row = 0
        """
        The y position of the Tile to be replaced on the World Map, including the two upper border rows. Valid values
        are 2 - 10.
        """

        self.col_and_screen_address = 0x0
        self.column = 0
        """The x position of the Tile to be replaced on the World Map, within the screen. So 0 - 15."""

        self.screen = 0
        """The screen number the Tile to be replaced is on, starting from 0 to a maximum of 3."""

        self.tile_indexes_address = 0x0
        self.tile_indexes = bytearray([0x00, 0x00, 0x00, 0x00])
        """
        These 4 indexes point to 8x8 pixel tiles in the graphic memory. These will replace the MapTile currently at the
        given position and can be chosen freely. See also replacement_block_index.
        """

        self.replacement_block_address = 0x0
        self.replacement_block_index = 0
        """
        The index pointing to a block, described by the TSA data of the Overworld Object Set. The block is not used for
        its graphical appearance, see tile_indexes for that. The Block is used for its properties, meaning, can it be
        walked on, can you enter a level through it, etc.
        """

        self.map_completion_data_address = 0x0
        self.map_completion_bit_index = 0x0
        """
        The offset into the Map Completion List, which keeps track of which Levels and Fortress FX's have been completed
        yet. Depends on the row the Tile, that should be replaced, is located on.
        """

        self.v_addr_high_address = 0x0
        self.v_addr_high = 0x0
        """
        This together with v_addr_low give the offset into the graphics memory housing the World Map Data. This way the
        Tile graphic can be switched out, without having to reload the entire World Map (probably).
        """

        self.v_addr_low_address = 0x0
        self.v_addr_low = 0x0

        super(FortressFXData, self).__init__(rom)

    def calculate_addresses(self):
        self.row_address = Constants.FortressFX_MapLocationRow + self.index
        self.col_and_screen_address = Constants.FortressFX_MapLocation + self.index

        self.tile_indexes_address = Constants.FortressFX_Patterns + self.index * 4  # tiles in block
        self.replacement_block_address = Constants.FortressFX_MapTileReplace + self.index

        # ignore the column value of the map completion data, because it is the same as the screen and column position
        self.map_completion_data_address = Constants.FortressFX_MapCompIdx + self.index * 2

        self.v_addr_high_address = Constants.FortressFX_VAddrH + self.index
        self.v_addr_low_address = Constants.FortressFX_VAddrL + self.index

    def read_values(self):
        self.row, _ = self._rom.nibbles(self.row_address)
        self.column, self.screen = self._rom.nibbles(self.col_and_screen_address)

        self.tile_indexes = self._rom.read(self.tile_indexes_address, 4)
        self.replacement_block_index = self._rom.int(self.replacement_block_address)

        # ignore the column value of the map completion data, because it is the same as the screen and column position
        self.map_completion_bit_index = self._rom.int(self.map_completion_data_address + 1)

        self.v_addr_high = self._rom.int(self.v_addr_high_address)
        self.v_addr_low = self._rom.int(self.v_addr_low_address)

    def write_back(self, rom: Optional[Rom] = None):
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
        if self.index != other.index:
            return False

        if self.pos != other.pos:
            return False

        if self.replacement_block_index != other.replacement_block_index:
            return False

        return True
