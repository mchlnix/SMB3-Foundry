from smb3parse.levels import WORLD_COUNT
from smb3parse.levels.world_map import WorldMap
from smb3parse.tests.conftest import TILE_CASTLE_BOTTOM


def test_get_castle_map_positions(rom):
    stock_castle_locations = [
        (1, 1, 6, 12),
        (2, 2, 4, 2),
        (3, 3, 6, 9),
        (4, 1, 4, 8),
        (5, 2, 8, 2),
        (6, 3, 4, 12),
        (7, 2, 7, 8),
    ]

    found_castle_locations = []

    for world_number in range(1, WORLD_COUNT + 1):
        world = WorldMap.from_world_number(rom, world_number)

        for world_map_position in world.gen_positions():
            if world_map_position.tile() == TILE_CASTLE_BOTTOM:
                found_castle_locations.append(world_map_position)
                break
        else:
            found_castle_locations.append(None)

    for stock_location, found_location in zip(stock_castle_locations, found_castle_locations):
        assert found_location.tuple() == stock_location, f"Failed at {found_location.world}"
