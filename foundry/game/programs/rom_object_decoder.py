from foundry import data_dir
"""Decode rom objs into readable formats"""


def write_line(l: list):
    return ','.join(['{:x}'.format(i) for i in l])


def decode_file(file_path: str, output_path: str):
    with open(file_path, "rb") as obj_def:
        data = obj_def.read()

    object_count = data[0]
    if object_count < 0xF7:  # obj definition is 0 also skips this step
        # first byte did not represent the object_count
        object_count = 0xFF
        position = 0
    else:
        position = 1

    objs = []
    for object_index in range(object_count):
        object_design_length = data[position]
        position += 1

        d = []
        for i in range(object_design_length):
            block_index = data[position]

            if block_index == 0xFF:
                block_index = (data[position + 1] << 16) + (data[position + 2] << 8) + data[position + 3]
                position += 3

            d.append(block_index)
            position += 1
        objs.append(d)

    with open(output_path, "w+") as f:
        f.write('\n'.join([str(write_line(obj)) for obj in objs]))  # rendered_blocks


object_definition = 1
decode_file(data_dir.joinpath(f"romobjs{object_definition}.dat"), f"romobjs{object_definition}.dat")