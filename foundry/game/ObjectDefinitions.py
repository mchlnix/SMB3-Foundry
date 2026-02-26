from enum import Enum
from functools import lru_cache

from foundry import data_dir
from smb3parse.objects.level_object import (
    ENEMY_OBJECT_DEFINITION,
    object_set_to_definition,
)
from smb3parse.util import apply


# TODO put somewhere else
def dollar_hex_to_int(hex_string: str):
    hex_string = hex_string.strip()

    if hex_string.startswith("$"):
        hex_string = hex_string.removeprefix("$")

        return int(hex_string, 16)
    else:
        return int(hex_string)


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
    SINGLE_BLOCK = 9
    CENTERED = 10  # like spinning platforms
    PYRAMID_TO_GROUND = 11  # to the ground or next object
    PYRAMID_2 = 12  # doesn't exist
    TO_THE_SKY = 13
    ENDING = 14
    BRICK_WALL = 15
    DIAG_STAGGERED = 16


class EndType(Enum):
    """
    Some level objects have blocks designated to be used at their ends. For example, pipes, which can be extended but
    always end at one side with the same couple of blocks. To keep track of where those special blocks are to be placed,
    this enum is used. When the value is TWO_ENDS, they are always on opposite sides, and whether they are left and
    right or top and bottom depends on the generator type of the object.
    """

    UNIFORM = 0
    TOP_OR_LEFT = 1
    BOTTOM_OR_RIGHT = 2
    TWO_ENDS = 3


class ObjectDefinition:
    """
    An object's data, like height, width, and which blocks it uses are information that is not stored in any look-up
    tables in the ROM, rather it is the result of generator code, written for many dozen different objects.

    To make this easier to emulate, we have the objects.dat (formerly data.dat) file from Workshop, listing all objects
    and their properties, which we can use to abstract away the drawing.

    The object definition is bundling this information.
    """

    def __init__(self, string):
        string = string.rstrip().replace("<", "").replace(">", "")

        (
            self.domain,
            _min_value,  # unused
            _max_value,  # unused
            bmp_width,
            bmp_height,
            generator_name,
            ending_name,
            is_4byte_str,
            description,
            *png_block_indexes_str,
        ) = apply(str.strip, string.split(","))

        self.bmp_width = int(bmp_width)
        self.bmp_height = int(bmp_height)
        self.generator_type = GeneratorType[generator_name]
        self.ending = EndType[ending_name]
        self.is_4byte = is_4byte_str == "4byte"
        self.description = description.replace(";;", ",")

        self.png_block_indexes = apply(dollar_hex_to_int, png_block_indexes_str)

        self.object_design_length = len(self.png_block_indexes)
        self.rom_block_indexes = [0] * self.object_design_length

        self.description = self.description.split("|")[0]

    def __repr__(self):
        return f"ObjectDefinition: {self.description}"


object_def_tables: list[list[ObjectDefinition]] = [[]]
# TODO Why x and x2?
enemy_handle_x = []
enemy_handle_x2 = []
enemy_handle_y = []

with open(data_dir.joinpath("objects.dat"), "r") as f:
    bank_index = 0
    obj_index = 0

    for line in f.readlines():
        if line.startswith(";"):  # is a comment
            continue

        if line.rstrip() == "":
            # a new "bank" of objects starts
            object_def_tables.append([])

            bank_index += 1
            obj_index = 0
            continue

        object_def_tables[bank_index].append(ObjectDefinition(line))

        # enemies can have additional offsets, so they are shown in the expected position in the editor
        if bank_index == ENEMY_OBJECT_DEFINITION:

            if "|" in line:
                after_bar = line.split("|")[1]
                before_block_indexes = after_bar.split(", <")[0]
                x, y, x2 = apply(int, before_block_indexes.split(" "))

            else:
                x = y = x2 = 0

            enemy_handle_x.append(x)
            enemy_handle_x2.append(x2)
            enemy_handle_y.append(y)

        obj_index += 1


@lru_cache(2**4)
def load_object_definitions(object_set):
    global object_def_tables

    object_def_no = object_set_to_definition[object_set]

    object_def_table = object_def_tables[object_def_no]

    if object_def_no == ENEMY_OBJECT_DEFINITION:
        # we cannot yet render the enemies from ROM data, so no need to update what we read in from objects.dat
        return object_def_table

    data = Path(data_dir.joinpath(f"romobjs{object_def_no}.dat")).read_bytes()

    assert data

    object_count = data[0]

    position = 1  # skip the object count

    for object_index in range(object_count):
        object_design_length = data[position]  # the first byte is the number of block indexes

        object_def = object_def_table[object_index]

        assert object_def.object_design_length == object_design_length, (object_def_no, object_def.description)
        object_def.object_design_length = object_design_length

        position += 1

        for i in range(object_design_length):
            block_index = data[position]

            # if the block index is 0xFF, it is a 24-bit address in the ROM
            if block_index == 0xFF:
                block_index = (data[position + 1] << 16) + (data[position + 2] << 8) + data[position + 3]

                position += 3

            object_def.rom_block_indexes[i] = block_index

            position += 1

    return object_def_table
