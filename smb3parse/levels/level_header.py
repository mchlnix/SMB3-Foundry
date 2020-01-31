from smb3parse.levels import (
    DEFAULT_HORIZONTAL_HEIGHT,
    DEFAULT_VERTICAL_WIDTH,
    ENEMY_BASE_OFFSET,
    HEADER_LENGTH,
    LEVEL_BASE_OFFSET,
    LEVEL_LENGTH_INTERVAL,
    LEVEL_MIN_LENGTH,
)
from smb3parse.objects.object_set import ObjectSet, assert_valid_object_set_number


class LevelHeader:
    def __init__(self, header_bytes: bytearray, object_set_number: int):
        if len(header_bytes) != HEADER_LENGTH:
            raise ValueError(f"A level header is made up of {HEADER_LENGTH} bytes, but {len(header_bytes)} were given.")

        assert_valid_object_set_number(object_set_number)

        self._object_set_number = object_set_number
        self._object_set = ObjectSet(self._object_set_number)

        self.data = header_bytes

        self.start_y_index = (self.data[4] & 0b1110_0000) >> 5

        self.length = LEVEL_MIN_LENGTH + (self.data[4] & 0b0000_1111) * LEVEL_LENGTH_INTERVAL
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
        self.jump_object_set = ObjectSet(self.jump_object_set_number)

        self.start_action = (self.data[7] & 0b1110_0000) >> 5

        self.graphic_set_index = self.data[7] & 0b0001_1111

        self.time_index = (self.data[8] & 0b1100_0000) >> 6

        self.music_index = self.data[8] & 0b0000_1111

        self.jump_level_address = (
            (self.data[1] << 8) + self.data[0] + LEVEL_BASE_OFFSET + self.jump_object_set.level_offset
        )
        self.jump_enemy_address = (self.data[3] << 8) + self.data[2] + ENEMY_BASE_OFFSET
