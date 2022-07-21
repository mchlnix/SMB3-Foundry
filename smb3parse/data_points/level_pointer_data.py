from typing import TYPE_CHECKING

from smb3parse.constants import (
    BASE_OFFSET,
    OFFSET_SIZE,
)
from smb3parse.data_points.util import DataPoint, _IndexedMixin, _PositionMixin
from smb3parse.levels import (
    FIRST_VALID_ROW,
    OFFSET_BY_OBJECT_SET_A000,
    WORLD_MAP_BASE_OFFSET,
    WORLD_MAP_SCREEN_SIZE,
    WORLD_MAP_SCREEN_WIDTH,
)

if TYPE_CHECKING:
    from smb3parse.data_points.world_map_data import WorldMapData


class LevelPointerData(_PositionMixin, _IndexedMixin, DataPoint):
    def __init__(self, world_map_data: "WorldMapData", index: int):
        self.world = world_map_data
        self.index = index

        self.object_set_address = 0x0
        self.object_set = 0

        self.level_offset_address = 0x0
        self.level_offset = 0

        self.enemy_offset_address = 0x0
        self.enemy_offset = 0

        super(LevelPointerData, self).__init__(self.world._rom)

    def calculate_addresses(self):
        self.x_address = self.screen_address = self.world.x_pos_list_start + self.index
        self.y_address = self.object_set_address = self.world.y_pos_list_start + self.index

        self.level_offset_address = (
            WORLD_MAP_BASE_OFFSET
            + self._rom.little_endian(self.world.level_offset_list_offset_address)
            + OFFSET_SIZE * self.index
        )
        self.enemy_offset_address = (
            WORLD_MAP_BASE_OFFSET
            + self._rom.little_endian(self.world.enemy_offset_list_offset_address)
            + OFFSET_SIZE * self.index
        )

    @property
    def level_address(self):
        object_set_offset = (self._rom.int(OFFSET_BY_OBJECT_SET_A000 + self.object_set) * OFFSET_SIZE - 10) * 0x1000

        return BASE_OFFSET + object_set_offset + self.level_offset

    @level_address.setter
    def level_address(self, value):
        object_set_offset = (self._rom.int(OFFSET_BY_OBJECT_SET_A000 + self.object_set) * OFFSET_SIZE - 10) * 0x1000

        self.level_offset = (value - BASE_OFFSET - object_set_offset) & 0xFFFF

    @property
    def enemy_address(self):
        return BASE_OFFSET + self.enemy_offset

    @enemy_address.setter
    def enemy_address(self, value):
        self.enemy_offset = value - BASE_OFFSET

    def read_values(self):
        self.screen, self.x = self._rom.nibbles(self.screen_address)

        self.y, self.object_set = self._rom.nibbles(self.y_address)

        self.level_offset = self._rom.little_endian(self.level_offset_address)
        self.enemy_offset = self._rom.little_endian(self.enemy_offset_address)

    def clear(self):
        self.screen = 0
        self.x = 0
        self.y = FIRST_VALID_ROW

        self.object_set = 1
        self.level_offset = 0x0
        self.enemy_offset = 0x0

    def write_back(self):
        self._rom.write_nibbles(self.screen_address, self.screen, self.x)
        self._rom.write_nibbles(self.y_address, self.y, self.object_set)

        self._rom.write_little_endian(self.level_offset_address, self.level_offset)
        self._rom.write_little_endian(self.enemy_offset_address, self.enemy_offset)

    def __eq__(self, other):
        if not isinstance(other, LevelPointerData):
            return NotImplemented

        if self.pos != other.pos:
            return False

        if self.level_offset != other.level_offset:
            return False

        if self.enemy_offset != other.enemy_offset:
            return False

        if self.object_set != other.object_set:
            return False

        if self.screen_address != other.screen_address:
            return False

        if self.y_address != other.y_address:
            return False

        if self.level_offset_address != other.level_offset_address:
            return False

        if self.enemy_offset_address != other.enemy_offset_address:
            return False

        return True

    def __lt__(self, other):
        self_result = self.screen * WORLD_MAP_SCREEN_SIZE + self.y * WORLD_MAP_SCREEN_WIDTH + self.x
        other_result = other.screen * WORLD_MAP_SCREEN_SIZE + other.y * WORLD_MAP_SCREEN_WIDTH + other.x

        return self_result < other_result
