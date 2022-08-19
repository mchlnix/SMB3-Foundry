from smb3parse.constants import (
    FortressFX_MapCompIdx,
    FortressFX_MapLocation,
    FortressFX_MapLocationRow,
    FortressFX_MapTileReplace,
    FortressFX_Patterns,
    FortressFX_VAddrH,
    FortressFX_VAddrL,
)
from smb3parse.data_points.util import DataPoint, _IndexedMixin, _PositionMixin
from smb3parse.levels import FIRST_VALID_ROW
from smb3parse.util.rom import Rom


class FortressFXData(_PositionMixin, _IndexedMixin, DataPoint):
    def __init__(self, rom: Rom, index: int):
        self.index = index

        self.row_address = 0x0
        self.col_and_screen_address = 0x0

        self.tile_indexes = bytearray([0x00, 0x00, 0x00, 0x00])
        self.tile_indexes_address = 0x0

        self.replacement_block_index = 0
        self.replacement_block_address = 0x0

        self.map_completion_bit_index = 0x0
        self.map_completion_data_address = 0x0

        # these together give the offset into the memory with the map tiles, so the tile can be replaced in memory,
        # without loading the whole map again (probably the reason)
        self.v_addr_high = 0x0
        self.v_addr_high_address = 0x0

        self.v_addr_low = 0x0
        self.v_addr_low_address = 0x0

        super(FortressFXData, self).__init__(rom)

    def calculate_addresses(self):
        self.row_address = FortressFX_MapLocationRow + self.index
        self.col_and_screen_address = FortressFX_MapLocation + self.index

        self.tile_indexes_address = FortressFX_Patterns + self.index * 4  # tiles in block
        self.replacement_block_address = FortressFX_MapTileReplace + self.index

        # ignore the column value of the map completion data, because it is the same as the screen and column position
        self.map_completion_data_address = FortressFX_MapCompIdx + self.index * 2

        self.v_addr_high_address = FortressFX_VAddrH + self.index
        self.v_addr_low_address = FortressFX_VAddrL + self.index

    def read_values(self):
        self.row, _ = self._rom.nibbles(self.row_address)
        self.column, self.screen = self._rom.nibbles(self.col_and_screen_address)

        self.tile_indexes = self._rom.read(self.tile_indexes_address, 4)
        self.replacement_block_index = self._rom.int(self.replacement_block_address)

        # ignore the column value of the map completion data, because it is the same as the screen and column position
        self.map_completion_bit_index = self._rom.int(self.map_completion_data_address + 1)

        self.v_addr_high = self._rom.int(self.v_addr_high_address)
        self.v_addr_low = self._rom.int(self.v_addr_low_address)

    def write_back(self, rom: Rom = None):
        if rom is None:
            rom = self._rom

        rom.write_nibbles(self.row_address, self.row)
        rom.write_nibbles(self.col_and_screen_address, self.column, self.screen)

        rom.write(self.tile_indexes_address, self.tile_indexes)
        rom.write(self.replacement_block_address, self.replacement_block_index)

        rom.write_nibbles(self.map_completion_data_address, self.screen, self.column)

        # 8 is not a valid row for any level pointer, row 9 has its value
        self.map_completion_bit_index = 0x80 >> min(self.row - FIRST_VALID_ROW, 8)

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
