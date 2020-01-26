from typing import List, Tuple

from foundry import data_dir
from foundry.game.Data import Mario3Level

ObjectData = Tuple[int, bytearray]
EnemyItemData = Tuple[int, bytearray]
LevelByteData = Tuple[ObjectData, EnemyItemData]


def _load_level_offsets() -> Tuple[List[Mario3Level], List[int]]:
    offsets = [Mario3Level(0, 0, 0, 0, 0, "Placeholder")]
    world_indexes = [0]

    with open(data_dir.joinpath("levels.dat"), "r") as level_data:
        for line_no, line in enumerate(level_data.readlines()):
            data = line.rstrip("\n").split(",")

            numbers = [int(_hex, 16) for _hex in data[0:5]]
            level_name = data[5]

            game_world, level_in_world, rom_level_offset, enemy_offset, real_obj_set = numbers

            level = Mario3Level(game_world, level_in_world, rom_level_offset, enemy_offset, real_obj_set, level_name)

            offsets.append(level)

            if level.game_world > 0 and level.level_in_world == 1:
                world_indexes.append(line_no)

    return offsets, world_indexes
