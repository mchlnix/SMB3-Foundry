import pytest

from smb3parse.levels.world_map import (
    WORLD_MAP_HEIGHT,
    WORLD_MAP_SCREEN_WIDTH,
    WorldMap,
    get_all_world_maps,
    list_world_map_addresses,
)
from smb3parse.objects.object_set import WORLD_MAP_OBJECT_SET

world_map_addresses = [0x185BA, 0x1864B, 0x1876C, 0x1891D, 0x18A3E, 0x18B5F, 0x18D10, 0x18E31, 0x19072]
world_map_screen_counts = [1, 2, 3, 2, 2, 3, 2, 4, 1]
world_1_addresses = [
    0x1FB9B,
    0x20F43,
    0x1EE22,
    0x2351A,
    0x1AA5A,
    0x233C1,
    0x2A976,
    0x2EDD0,
    0x1FCAC,
    0x1FA62,
    0x27A43,
    0x1FE61,
    0x2788D,
    0x1FD81,
    0x2AA43,
    0x2FA1B,
    0x21404,
    0x2141E,
    0x2A850,
    0x2EC42,
    0x2FC2E,
    0x2FCD1,
]


def test_list_world_map_addresses(rom):
    assert world_map_addresses == list_world_map_addresses(rom)


def test_list_all_world_maps_address(rom):
    for world_map, world_map_address in zip(get_all_world_maps(rom), world_map_addresses):
        assert world_map.memory_address == world_map_address


def test_list_all_world_maps_object_set(rom):
    for world_map in get_all_world_maps(rom):
        assert world_map.object_set.number == WORLD_MAP_OBJECT_SET


def test_list_all_world_maps_height(rom):
    for world_map in get_all_world_maps(rom):
        assert world_map.height == WORLD_MAP_HEIGHT


def test_list_all_world_maps_screen_counts(rom):
    for world_map, screen_count in zip(get_all_world_maps(rom), world_map_screen_counts):
        assert world_map.screen_count == screen_count


def test_list_all_world_maps_width(rom):
    for world_map, screen_count in zip(get_all_world_maps(rom), world_map_screen_counts):
        assert world_map.width == screen_count * WORLD_MAP_SCREEN_WIDTH


@pytest.mark.parametrize(
    "row, column, level_address, enemy_address, object_set",
    [
        (0, 4, 0x1FB9B, 0xC538, 0x1),
        (0, 8, 0x20F43, 0xC6BB, 0x3),
        (0, 10, 0x1EE22, 0xC2FF, 0x01),
        (2, 10, 0x2351A, 0xCC44, 0x4),
        (8, 4, 0x1AA5A, 0xC93C, 0xE),
    ],
)
def test_get_level_at_position(rom, row, column, level_address, enemy_address, object_set):
    world_1 = WorldMap(world_map_addresses[0], rom)

    level_tile = world_1.level_for_position(1, row, column)

    assert level_tile == (level_address, enemy_address, object_set)


def test_tile_not_enterable(rom):
    world_1 = WorldMap.from_world_number(rom, 1)

    tile_at_0_0 = world_1._map_tile_for_position(1, 0, 0)

    assert not world_1._is_enterable(tile_at_0_0)


def test_tile_is_enterable(rom):
    world_1 = WorldMap.from_world_number(rom, 1)

    tile_at_0_4 = world_1._map_tile_for_position(1, 0, 4)

    assert world_1._is_enterable(tile_at_0_4)


def test_level_count_world_1(rom):
    world_1 = WorldMap.from_world_number(rom, 1)

    assert world_1.level_count_s1 == 0x15
    assert world_1.level_count_s2 == 0x00
    assert world_1.level_count_s3 == 0x00
    assert world_1.level_count_s4 == 0x00


def test_level_count_world_8(rom):
    world_1 = WorldMap.from_world_number(rom, 8)

    assert world_1.level_count_s1 == 0x08
    assert world_1.level_count_s2 == 0x0A
    assert world_1.level_count_s3 == 0x11
    assert world_1.level_count_s4 == 0x06


def test_get_tile(rom):
    level_1_tile, level_2_tile, level_3_tile, level_4_tile = range(0x03, 0x03 + 4)

    world_1 = WorldMap.from_world_number(rom, 1)

    assert world_1._map_tile_for_position(1, 0, 4) == level_1_tile
    assert world_1._map_tile_for_position(1, 0, 8) == level_2_tile
    assert world_1._map_tile_for_position(1, 0, 10) == level_3_tile
    assert world_1._map_tile_for_position(1, 2, 10) == level_4_tile
