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
MARIO_Y_POSITIONS = [0x17, 0x04, 0x00, 0x14, 0x07, 0x0B, 0x0F, 0x18]  # 0x3D7A0 + 0x3D7A8


class LevelHeader:
    def __init__(self, rom: Rom, header_bytes: bytearray, object_set_number: int):
        if len(header_bytes) != HEADER_LENGTH:
            raise ValueError(f"A level header is made up of {HEADER_LENGTH} bytes, but {len(header_bytes)} were given.")

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

        self.jump_object_set_number = self.data[6] & 0b0000_1111  # for indexing purposes
        self.jump_object_set = ObjectSet(rom, self.jump_object_set_number)

        self.start_action = (self.data[7] & 0b1110_0000) >> 5

        self.graphic_set_index = self.data[7] & 0b0001_1111

        self.time_index = (self.data[8] & 0b1100_0000) >> 6

        self.music_index = self.data[8] & 0b0000_1111

        self.jump_level_offset = (self.data[1] << 8) + self.data[0]
        self.jump_enemy_address = (self.data[3] << 8) + self.data[2] + ENEMY_BASE_OFFSET

    def mario_position(self):
        x = MARIO_X_POSITIONS[self.start_x_index] >> 4
        y = MARIO_Y_POSITIONS[self.start_y_index]

        if self.is_vertical:
            y += (self.screens - 1) * 15  # TODO: Why?

        return x, y

    @property
    def jump_level_address(self):
        return self.jump_object_set.level_offset + self.jump_level_offset

    @jump_level_address.setter
    def jump_level_address(self, value):
        self.jump_level_offset = value - self.jump_object_set.level_offset
