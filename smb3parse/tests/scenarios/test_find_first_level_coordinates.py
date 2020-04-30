import pytest

from smb3parse.levels.world_map import WorldMap
from smb3parse.tests.conftest import TILE_LEVEL_1
from smb3parse.util.rom import Rom


def test_find_first_level_coordinates(rom: Rom):
    original_rom_data = rom._data.copy()

    # get world 1 date
    world_1 = WorldMap.from_world_number(rom, 1)

    # find position of level 1
    for coordinate in world_1.gen_positions():
        if coordinate.tile() == TILE_LEVEL_1:
            break
    else:
        pytest.fail("Didn't find Level 1 in this world.")
        return

    assert coordinate.level_info is not None

    object_set, level_address, enemy_address = coordinate.level_info

    world_1.replace_level_at_position((level_address, enemy_address, object_set), coordinate)

    for i in range(0, len(original_rom_data), 0x10):
        original_data = list(map(hex, original_rom_data[i : i + 0x10]))
        rom_data = list(map(hex, rom._data[i : i + 0x10]))

        if original_data != rom_data:
            assert original_data == rom_data
