from typing import List

from foundry import data_dir

HORIZONTAL = 0
VERTICAL = 1  # vertical downward
DIAG_DOWN_LEFT = 2
DESERT_PIPE_BOX = 3
DIAG_DOWN_RIGHT = 4
DIAG_UP_RIGHT = 5
HORIZ_TO_GROUND = 6
HORIZONTAL_2 = 7  # special case of horizontal, floating boxes, ceilings
DIAG_WEIRD = 8  #
SINGLE_BLOCK_OBJECT = 9
CENTERED = 10  # like spinning platforms
PYRAMID_TO_GROUND = 11  # to the ground or next object
PYRAMID_2 = 12  # doesn't exist?
TO_THE_SKY = 13
ENDING = 14

UNIFORM = 0
END_ON_TOP_OR_LEFT = 1
END_ON_BOTTOM_OR_RIGHT = 2
TWO_ENDS = 3


ENEMY_OBJECT_DEFINITION = 12


class ObjectDefinition:
    def __init__(self, string):
        string = string.rstrip().replace("<", "").replace(">", "")

        (
            self.domain,
            self.min_value,
            self.max_value,
            self.bmp_width,
            self.bmp_height,
            *self.object_design,
            self.orientation,
            self.ending,
            self.is_4byte,
            self.description,
        ) = string.split(",")

        self.bmp_width = int(self.bmp_width)
        self.bmp_height = int(self.bmp_height)
        self.orientation = int(self.orientation)
        self.ending = int(self.ending)
        self.is_4byte = self.is_4byte == "1"
        self.description = self.description.replace(";;", ",")

        self.object_design2 = []
        self.rom_object_design = []

        for index, item in enumerate(self.object_design):
            self.object_design[index] = int(item)  # original data
            self.object_design2.append(0)  # data after trimming through romobjset*.dat file?
            self.rom_object_design.append(self.object_design[index])
            self.object_design_length = index + 1  # todo necessary when we have len()?

        self.description = self.description.split("|")[0]


object_metadata: List[List[ObjectDefinition]] = [[]]
enemy_handle_x = []
enemy_handle_x2 = []
enemy_handle_y = []

with open(data_dir.joinpath("data.dat"), "r") as f:
    first_index = 0  # todo what are they symbolizing? object tables?
    second_index = 0

    for line in f.readlines():
        if line.startswith(";"):  # is a comment
            continue

        if line.rstrip() == "":
            object_metadata.append([])

            first_index += 1
            second_index = 0
            continue

        object_metadata[first_index].append(ObjectDefinition(line))

        if first_index == ENEMY_OBJECT_DEFINITION and second_index <= 236:
            if line.find("|") >= 0:
                x, y, x2 = line.split("|")[1].split(" ")
            else:
                x, y, x2 = "0 0 0".split(" ")

            enemy_handle_x.append(x)
            enemy_handle_x2.append(x2)
            enemy_handle_y.append(y)

        second_index += 1


object_set_to_definition = {
    0: 0,
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
    16: 12,
}


def load_object_definitions(object_set):
    global object_metadata

    object_definition = object_set_to_definition[object_set]

    if object_definition == ENEMY_OBJECT_DEFINITION:
        return object_metadata[object_definition]

    with open(data_dir.joinpath(f"romobjs{object_definition}.dat"), "rb") as obj_def:
        data = obj_def.read()

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

        object_metadata[object_definition][object_index].object_design_length = object_design_length

        position += 1

        for i in range(object_design_length):
            block_index = data[position]

            if block_index == 0xFF:
                block_index = (data[position + 1] << 16) + (data[position + 2] << 8) + data[position + 3]

                position += 3

            object_metadata[object_definition][object_index].rom_object_design[i] = block_index

            position += 1

    # read overlay data
    if position >= len(data):
        return

    for object_index in range(object_count):
        object_design_length = object_metadata[object_definition][object_index].object_design_length

        object_metadata[object_definition][object_index].object_design2 = []

        for i in range(object_design_length):
            if i <= object_design_length:
                object_metadata[object_definition][object_index].object_design2.append(data[position])
                position += 1

    return object_metadata[object_definition]
