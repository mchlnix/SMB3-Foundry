from typing import Optional

from smb3parse.levels import HEADER_LENGTH, LevelBase
from smb3parse.levels.level_header import LevelHeader
from smb3parse.levels.world_map import WorldMapPosition
from smb3parse.objects.object_set import ObjectSet, assert_valid_object_set_number
from smb3parse.util.rom import Rom


class Level(LevelBase):
    def __init__(self, rom: Rom, object_set_number: int, layout_address: int, enemy_address: int):
        super(Level, self).__init__(ObjectSet(rom, object_set_number), layout_address)

        self.enemy_address = enemy_address

        self.world_map_position: Optional[WorldMapPosition] = None

        self._rom = rom

        self.header_address = self.layout_address - HEADER_LENGTH

        self.header_bytes = self._rom.read(self.header_address, HEADER_LENGTH)

        self.header = LevelHeader(rom, self.header_bytes, self.object_set_number)

    def set_world_map_position(self, position: WorldMapPosition):
        self.world_map_position = position

    def __eq__(self, other):
        if not isinstance(other, Level):
            return False

        return (
            self.object_set_number == other.object_set_number
            and self.layout_address == other.layout_address
            and self.enemy_address == other.enemy_address
        )

    @staticmethod
    def from_world_map(rom: Rom, world_map_position: WorldMapPosition) -> Optional["Level"]:
        lp = world_map_position.level_pointer

        if lp is None:
            return None

        level = Level(rom, lp.object_set, lp.level_address, lp.enemy_address)

        level.set_world_map_position(world_map_position)

        return level

    @staticmethod
    def from_memory(rom: Rom, object_set_number: int, layout_address: int, enemy_address: int):
        assert_valid_object_set_number(object_set_number)

        level = Level(rom, object_set_number, layout_address, enemy_address)

        return level
