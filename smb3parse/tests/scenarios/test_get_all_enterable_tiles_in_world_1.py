import pytest

from smb3parse.levels.world_map import WorldMap

world_1_positions = [
    (0, 2, 4),
    (0, 2, 8),
    (0, 2, 10),
    (0, 4, 10),
    (0, 4, 12),
    (0, 6, 6),
    (0, 6, 8),
    (0, 8, 6),
    (0, 8, 12),
    (0, 10, 4),
    (0, 10, 8),
]

world_8_positions = [
    (0, 3, 8),
    (0, 5, 6),
    (0, 9, 10),
    (0, 9, 11),
    (0, 9, 12),
    (1, 3, 10),
    (1, 5, 2),
    (1, 5, 8),
    (1, 7, 6),
    (1, 7, 7),
    (1, 7, 8),
    (1, 7, 9),
    (1, 7, 10),
    (1, 7, 12),
    (2, 5, 2),
    (2, 5, 6),
    (2, 7, 4),
    (2, 7, 8),
    (2, 7, 12),
    (2, 9, 2),
    (2, 9, 4),
    (2, 9, 12),
    (3, 7, 2),
    (3, 7, 12),
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
