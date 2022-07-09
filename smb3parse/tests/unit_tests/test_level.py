from smb3parse.levels.level import Level
from smb3parse.levels.world_map import WorldMapPosition


def test_level_1_1(rom, world_1):
    position_of_1_1 = WorldMapPosition(world_1, 0, 2, 4)

    level_1_1_from_map = Level.from_world_map(rom, position_of_1_1)
    level_1_1_from_memory = Level.from_memory(rom, 0x1, 0x1FB92, 0xC537)

    assert level_1_1_from_map == level_1_1_from_memory
