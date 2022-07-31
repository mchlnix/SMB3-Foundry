from smb3parse.constants import (
    FortressFX_MapLocation,
    FortressFX_MapLocationRow,
    FortressFX_MapTileReplace,
    FortressFX_Patterns,
)
from smb3parse.data_points.util import DataPoint, _IndexedMixin, _PositionMixin
from smb3parse.util.rom import Rom


class FortressFXData(_PositionMixin, _IndexedMixin, DataPoint):
    def __init__(self, rom: Rom, index: int):
        self.index = index

        self.row_address = 0x0
        self.col_and_screen_address = 0x0

        self.tile_indexes = [0x00, 0x00, 0x00, 0x00]
        self.tile_indexes_address = 0x0

        self.replacement_block_index = 0
        self.replacement_block_address = 0x0

        super(FortressFXData, self).__init__(rom)

    def calculate_addresses(self):
        self.row_address = FortressFX_MapLocationRow + self.index
        self.col_and_screen_address = FortressFX_MapLocation + self.index

        self.tile_indexes_address = FortressFX_Patterns + self.index * 4  # tiles in block
        self.replacement_block_address = FortressFX_MapTileReplace + self.index

    def read_values(self):
        self.row, _ = self._rom.nibbles(self.row_address)
        self.column, self.screen = self._rom.nibbles(self.col_and_screen_address)

        self.tile_indexes = self._rom.read(self.tile_indexes_address, 4)
        self.replacement_block_index = self._rom.int(self.replacement_block_address)

    def write_back(self, rom: Rom = None):
        if rom is None:
            rom = self._rom

        rom.write_nibbles(self.row_address, self.row)
        rom.write_nibbles(self.col_and_screen_address, self.column, self.screen)

        rom.write(self.tile_indexes_address, self.tile_indexes)
        rom.write(self.replacement_block_address, self.replacement_block_index)

    def __eq__(self, other):
        if self.index != other.index:
            return False

        if self.pos != other.pos:
            return False

        if self.replacement_block_index != other.replacement_block_index:
            return False

        return True
