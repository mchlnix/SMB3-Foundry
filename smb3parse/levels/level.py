from smb3parse.levels import HEADER_LENGTH
from smb3parse.levels.world_map import WorldMap


class Level:
    def __init__(self, rom, world: WorldMap, screen: int, row: int, column: int):
        self.layout_address, self.enemy_address, self.object_set_index = world.level_for_position(screen, row, column)

        self._rom = rom

        self.header_address = self.layout_address - HEADER_LENGTH

        self.header_bytes = self._rom.read(self.header_address, HEADER_LENGTH)
