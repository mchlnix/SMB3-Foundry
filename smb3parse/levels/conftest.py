import pytest

from smb3parse.levels.world_map import WorldMap


@pytest.fixture
def world_1(rom):
    return WorldMap.from_world_number(rom, 1)


@pytest.fixture
def world_8(rom):
    return WorldMap.from_world_number(rom, 8)
