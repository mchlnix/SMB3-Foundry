from smb3parse.levels.world_map import (
    list_world_map_addresses,
    get_all_world_maps,
    WORLD_MAP_HEIGHT,
    WORLD_MAP_SCREEN_WIDTH,
)
from smb3parse.objects.object_set import WORLD_MAP_OBJECT_SET

world_map_addresses = [0x185BA, 0x1864B, 0x1876C, 0x1891D, 0x18A3E, 0x18B5F, 0x18D10, 0x18E31, 0x19072]
world_map_screen_counts = [1, 2, 3, 2, 2, 3, 2, 4, 1]


def test_list_world_map_addresses(rom):
    assert world_map_addresses == list_world_map_addresses(rom.rom_data)


def test_list_all_world_maps_address(rom):
    for world_map, world_map_address in zip(get_all_world_maps(rom.rom_data), world_map_addresses):
        assert world_map.memory_address == world_map_address


def test_list_all_world_maps_object_set(rom):
    for world_map in get_all_world_maps(rom.rom_data):
        assert world_map.object_set.number == WORLD_MAP_OBJECT_SET


def test_list_all_world_maps_height(rom):
    for world_map in get_all_world_maps(rom.rom_data):
        assert world_map.height == WORLD_MAP_HEIGHT


def test_list_all_world_maps_screen_counts(rom):
    for world_map, screen_count in zip(get_all_world_maps(rom.rom_data), world_map_screen_counts):
        assert world_map.screen_count == screen_count


def test_list_all_world_maps_width(rom):
    for world_map, screen_count in zip(get_all_world_maps(rom.rom_data), world_map_screen_counts):
        assert world_map.width == screen_count * WORLD_MAP_SCREEN_WIDTH