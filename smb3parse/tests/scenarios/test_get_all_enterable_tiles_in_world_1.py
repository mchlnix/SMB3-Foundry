import pytest

from smb3parse.levels.world_map import WorldMap

world_1_positions = [
    (1, 0, 4),
    (1, 0, 8),
    (1, 0, 10),
    (1, 2, 10),
    (1, 2, 12),
    (1, 4, 6),
    (1, 4, 8),
    (1, 6, 6),
    (1, 6, 12),
    (1, 8, 4),
    (1, 8, 8),
]

world_8_positions = [
    (1, 1, 8),
    (1, 3, 6),
    (1, 7, 10),
    (1, 7, 11),
    (1, 7, 12),
    (2, 1, 10),
    (2, 3, 2),
    (2, 3, 8),
    (2, 5, 6),
    (2, 5, 7),
    (2, 5, 8),
    (2, 5, 9),
    (2, 5, 10),
    (2, 5, 12),
    (3, 3, 2),
    (3, 3, 6),
    (3, 5, 4),
    (3, 5, 8),
    (3, 5, 12),
    (3, 7, 2),
    (3, 7, 4),
    (3, 7, 12),
    (4, 5, 2),
    (4, 5, 12),
]


@pytest.mark.parametrize("world_number, stock_positions", [(1, world_1_positions), (8, world_8_positions)])
def test_get_all_level_locations_in_world(world_number, stock_positions, rom):
    world = WorldMap.from_world_number(rom, world_number)

    enterable_positions = []

    for world_map_position in world.gen_positions():
        if world_map_position.can_have_level():
            _, screen, row, column = world_map_position.tuple()
            enterable_positions.append((screen, row, column))

    for stock, found in zip(stock_positions, enterable_positions):
        assert found == stock

    assert len(stock_positions) == len(enterable_positions)
