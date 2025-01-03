from itertools import product

from smb3parse.levels import (
    DEFAULT_HORIZONTAL_HEIGHT,
    DEFAULT_VERTICAL_WIDTH,
    ENEMY_BASE_OFFSET,
    HEADER_LENGTH,
    LEVEL_LENGTH_INTERVAL,
    LEVEL_MIN_LENGTH,
)
from smb3parse.objects.object_set import ObjectSet, assert_valid_object_set_number
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


class LevelHeader:
    def __init__(self, rom: Rom, header_bytes: bytearray, object_set_number: int):
        if len(header_bytes) != HEADER_LENGTH:
            raise ValueError(f"A level header is made up of {HEADER_LENGTH} bytes, but {len(header_bytes)} were given.")

        self._rom = rom

        assert_valid_object_set_number(object_set_number)

        self._object_set_number = object_set_number
        self._object_set = ObjectSet(rom, self._object_set_number)

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
        self.is_vertical = self.data[6] & 0b0001_0000

        if self.is_vertical:
            self.height = self.length
            self.width = DEFAULT_VERTICAL_WIDTH

        self._jump_object_set_number = self.data[6] & 0b0000_1111  # for indexing purposes
        self._jump_object_set = ObjectSet(rom, self.jump_object_set_number)

        self.start_action = (self.data[7] & 0b1110_0000) >> 5

        self.graphic_set_index = self.data[7] & 0b0001_1111

        self.time_index = (self.data[8] & 0b1100_0000) >> 6

        self.music_index = self.data[8] & 0b0000_1111

        self.jump_level_offset = (self.data[1] << 8) + self.data[0]
        self.jump_enemy_offset = (self.data[3] << 8) + self.data[2]

    def position_from_start_index(self, start_x_index: int, start_y_index: int):
        x = MARIO_X_POSITIONS[start_x_index] >> 4
        y = MARIO_Y_POSITIONS[start_y_index]

        if self.is_vertical:
            y += (self.screens - 1) * 15  # TODO: Why?

        return x, y

    def start_indexes_from_position(self, x, y):
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
        for x_index, y_index in product(range(len(MARIO_X_POSITIONS)), range(len(MARIO_Y_POSITIONS))):
            yield self.position_from_start_index(x_index, y_index)

    def mario_position(self):
        return self.position_from_start_index(self.start_x_index, self.start_y_index)

    @property
    def mario_start_indexes(self):
        return self.start_x_index, self.start_y_index

    @property
    def jump_level_address(self):
        return self.jump_object_set.level_offset + self.jump_level_offset

    @jump_level_address.setter
    def jump_level_address(self, value):
        self.jump_level_offset = value - self.jump_object_set.level_offset

    @property
    def jump_enemy_address(self):
        return self.jump_enemy_offset + ENEMY_BASE_OFFSET

    @jump_enemy_address.setter
    def jump_enemy_address(self, value):
        self.jump_enemy_offset = value - ENEMY_BASE_OFFSET

    @property
    def jump_object_set_number(self):
        return self._jump_object_set_number

    @jump_object_set_number.setter
    def jump_object_set_number(self, value):
        self._jump_object_set_number = value

    @property
    def jump_object_set(self):
        return ObjectSet(self._rom, self._jump_object_set_number)
