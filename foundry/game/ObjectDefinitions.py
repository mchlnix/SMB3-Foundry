from enum import Enum
from functools import lru_cache
from pathlib import Path

from foundry import data_dir
from smb3parse.objects.level_object import ENEMY_OBJECT_DEFINITION, object_set_to_definition


class GeneratorType(Enum):
    """
    Level objects are generated using different methods, depending on their generator type. Some objects extend until
    they hit another object, some extend up to the sky. To identify in what way a specific type of level object is
    constructed, this enum lists the known generator types.
    """

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


class EndType(Enum):
    """
    Some level objects have blocks designated to be used at their ends. For example pipes, which can be extended, but
    always end at one side with the same couple of blocks. To keep track of where those special blocks are to be placed,
    this enum is used. When the value is TWO_ENDS they are always on opposite sides and whether they are left and right
    or top and bottom depends on the generator type of the object.
    """

    UNIFORM = 0
    END_ON_TOP_OR_LEFT = 1
    END_ON_BOTTOM_OR_RIGHT = 2
    TWO_ENDS = 3


class ObjectDefinition:
    """
    An object's data, like height, width and which blocks it uses are information, that is not stored in any look up
    tables in the ROM, rather it is the result of generator code, written for many dozen different objects.

    To make this easier to emulate we have the data.dat file from Workshop, listing all objects and their
    properties, which we can use to abstract away the drawing.

    The object definition is bundling this information.
    """

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

    def __repr__(self):
        return f"ObjectDefinition: {self.description}"


object_metadata: list[list[ObjectDefinition]] = [[]]
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

            enemy_handle_x.append(int(x))
            enemy_handle_x2.append(int(x2))
            enemy_handle_y.append(int(y))

        second_index += 1


@lru_cache(2**4)
def load_object_definitions(object_set):
    global object_metadata

    object_definition = object_set_to_definition[object_set]

    if object_definition == ENEMY_OBJECT_DEFINITION:
        return object_metadata[object_definition]

    data = Path(data_dir.joinpath(f"romobjs{object_definition}.dat")).read_bytes()

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
