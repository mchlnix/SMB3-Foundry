from game.Data import Mario3Level


def _load_level_offsets():
    offsets = [0]
    world_indexes = [0]

    with open("data/levels.dat", "r") as level_data:
        for line_no, line in enumerate(level_data.readlines()):
            data = line.rstrip("\n").split(",")

            numbers = [int(_hex, 16) for _hex in data[0:5]]
            level_name = data[5]

            offsets.append(Mario3Level(*numbers, level_name))

            world_index, level_index = numbers[0], numbers[1]

            if world_index > 0 and level_index == 1:
                world_indexes.append(line_no)

    return offsets, world_indexes
