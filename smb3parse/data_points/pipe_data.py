from smb3parse.constants import PipewayCtlr_MapScrlXHi, PipewayCtlr_MapX, PipewayCtlr_MapXHi, PipewayCtlr_MapY
from smb3parse.data_points import Position
from smb3parse.data_points.util import DataPoint, _IndexedMixin
from smb3parse.levels import WORLD_MAP_SCREEN_WIDTH
from smb3parse.util.rom import Rom


class PipeData(_IndexedMixin, DataPoint):
    def __init__(self, rom: Rom, index: int):
        self.index = index % 0x80

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

        super(PipeData, self).__init__(rom)

    def change_index(self, index: int):
        index %= 0x80
        super(PipeData, self).change_index(index)

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

    @property
    def _combined_left_x(self):
        return (self.x_high_left << 4) + self.x_low_left

    @_combined_left_x.setter
    def _combined_left_x(self, value):
        self.x_high_left = value >> 4
        self.x_low_left = value & 0x0F

    @property
    def _combined_right_x(self):
        return (self.x_high_right << 4) + self.x_low_right

    @_combined_right_x.setter
    def _combined_right_x(self, value):
        self.x_high_right = value >> 4
        self.x_low_right = value & 0x0F

    @property
    def screen_left(self):
        return self._combined_left_x // WORLD_MAP_SCREEN_WIDTH

    @screen_left.setter
    def screen_left(self, value):
        new_comb_x = self._combined_left_x % WORLD_MAP_SCREEN_WIDTH
        new_comb_x += value * WORLD_MAP_SCREEN_WIDTH

        self._combined_left_x = new_comb_x

        # FIXME: we disregard the possibility to scroll to half the screen here by setting 0x80
        self.scroll_x_high_left = value

    @property
    def x_left(self):
        return self._combined_left_x % WORLD_MAP_SCREEN_WIDTH

    @x_left.setter
    def x_left(self, value):
        self._combined_left_x = self.screen_left * WORLD_MAP_SCREEN_WIDTH + value

    @property
    def screen_right(self):
        return self._combined_right_x // WORLD_MAP_SCREEN_WIDTH

    @screen_right.setter
    def screen_right(self, value):
        new_comb_x = self._combined_right_x % WORLD_MAP_SCREEN_WIDTH
        new_comb_x += value * WORLD_MAP_SCREEN_WIDTH

        self._combined_right_x = new_comb_x

        # FIXME: we disregard the possibility to scroll to half the screen here by setting 0x08
        self.scroll_x_high_right = value

    @property
    def x_right(self):
        return self._combined_right_x % WORLD_MAP_SCREEN_WIDTH

    @x_right.setter
    def x_right(self, value):
        self._combined_right_x = self.screen_right * WORLD_MAP_SCREEN_WIDTH + value

    @property
    def left_pos(self):
        return Position(self.x_left, self.y_left, self.screen_left)

    @left_pos.setter
    def left_pos(self, value: Position):
        self.x_left = value.x
        self.y_left = value.y
        self.screen_left = value.screen

    @property
    def right_pos(self):
        return Position(self.x_right, self.y_right, self.screen_right)

    @right_pos.setter
    def right_pos(self, value: Position):
        self.x_right = value.x
        self.y_right = value.y
        self.screen_right = value.screen
