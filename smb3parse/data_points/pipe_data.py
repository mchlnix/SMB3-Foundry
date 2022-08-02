from smb3parse.constants import PipewayCtlr_MapScrlXHi, PipewayCtlr_MapX, PipewayCtlr_MapXHi, PipewayCtlr_MapY
from smb3parse.data_points.util import DataPoint, _IndexedMixin
from smb3parse.util.rom import Rom


class PipeData(_IndexedMixin, DataPoint):
    def __init__(self, rom: Rom, index: int):
        super(PipeData, self).__init__(rom)

        self.index = index

        self.x_high_left = 0
        self.x_high_right = 0
        self.x_high_address = 0x0

        self.x_low_left = 0
        self.x_low_right = 0
        self.x_low_address = 0x0

        self.y_left = 0
        self.y_right = 0
        self.y_address = 0x0

        self.scroll_x_high_left = 0
        self.scroll_x_high_right = 0
        self.scroll_x_high_address = 0x0

    def calculate_addresses(self):
        self.x_high_address = PipewayCtlr_MapXHi + self.index
        self.x_low_address = PipewayCtlr_MapX + self.index

        self.y_address = PipewayCtlr_MapY + self.index

        self.scroll_x_high_address = PipewayCtlr_MapScrlXHi + self.index

    def read_values(self):
        self.x_high_left, self.x_high_right = self._rom.nibbles(self.x_high_address)
        self.x_low_left, self.x_low_right = self._rom.nibbles(self.x_low_address)

        self.y_left, self.y_right = self._rom.nibbles(self.y_address)

        self.scroll_x_high_left, self.scroll_x_high_right = self._rom.nibbles(self.scroll_x_high_address)

    def write_back(self, rom: Rom = None):
        if rom is None:
            rom = self._rom

        rom.write_nibbles(self.x_high_address, self.x_high_left, self.x_high_right)
        rom.write_nibbles(self.x_low_address, self.x_low_left, self.x_low_right)

        rom.write_nibbles(self.y_address, self.y_left, self.y_right)

        rom.write_nibbles(self.scroll_x_high_address, self.scroll_x_high_left, self.scroll_x_high_right)
