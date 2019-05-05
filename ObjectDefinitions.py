from Data import plains_level, ENEMY_OBJ_DEF

object_set_to_definition = {
    16: 0,
    0: 1,
    1: 1,
    7: 1,
    15: 1,
    3: 2,
    114: 2,
    4: 3,
    2: 4,
    10: 5,
    13: 6,
    9: 7,
    6: 8,
    8: 8,
    5: 9,
    11: 9,
    12: 10,
    14: 11,
}


def load_object_definition(object_set):
    object_definition = object_set_to_definition[object_set]

    with open(f"data/romobjs{object_definition}.dat", "rb") as f:
        data = f.read()

    assert len(data) > 0

    object_count = data[0]

    if object_definition != 0 and object_count < 0xF7:
        # first byte did not represent the object_count
        object_count = 0xFF
        position = 0
    else:
        position = 1

    for object_index in range(object_count):
        object_design_length = data[position]

        plains_level[object_definition][
            object_index
        ].object_design_length = object_design_length

        position += 1

        for i in range(object_design_length):
            block_index = data[position]

            if block_index == 0xFF:
                block_index = (
                    (data[position + 1] << 16)
                    + (data[position + 2] << 8)
                    + data[position + 3]
                )

                position += 3

            plains_level[object_definition][object_index].rom_object_design[
                i
            ] = block_index

            position += 1

    # read overlay data
    if position >= len(data):
        return

    for object_index in range(object_count):
        object_design_length = plains_level[object_definition][
            object_index
        ].object_design_length

        plains_level[object_definition][object_index].object_design2 = []

        for i in range(object_design_length):
            if i <= object_design_length:
                plains_level[object_definition][object_index].object_design2.append(
                    data[position]
                )
                position += 1

    return plains_level[object_definition]
