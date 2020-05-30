import yaml
from yaml import CLoader as Loader
import logging
from foundry import data_dir
from dataclasses import dataclass

from foundry.game.Range import Range
from foundry.game.Size import Size

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
UPWARD_PIPE = 15
DOWNWARD_PIPE = 16
RIGHTWARD_PIPE = 17
LEFTWARD_PIPE = 18
DIAG_DOWN_RIGHT_30 = 19
DIAG_DOWN_LEFT_30 = 20
HORIZONTAL_WITH_TOP = 21
HORIZONTAL_WITH_SIDE = 22
VERTICAL_WITH_TOP = 23
VERTICAL_WITH_ALL_SIDES = 24
HORIZTONAL_WITH_ALL_SIDES = 25
VERTICAL_WITH_TOP_AND_BOTTOM = 26
DIAG_DOWN_LEFT_60 = 27
DIAG_DOWN_RIGHT_60 = 28
HORIZONTAL_WITH_BOTTOM = 29
DIAG_UP_LEFT = 30
DIAG_UP_RIGHT_30 = 31
VERTICAL_WITH_DOUBLE_TOP = 32
VERTICAL_WITH_BOTTOM = 33

UNIFORM = 0
END_ON_TOP_OR_LEFT = 1
END_ON_BOTTOM_OR_RIGHT = 2
TWO_ENDS = 3

ENEMY_OBJECT_DEFINITION = 12

OBJECT_SET_TO_DEFINITION = {
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


logging.basicConfig(filename=data_dir.joinpath("logs/obj_def.log"), level=logging.CRITICAL)


class Block_Design:
    """Defines the design of an object"""
    def __init__(self, blocks: list = None):
        self.blocks = blocks if blocks else []

    @classmethod
    def from_dat_file(cls, data, len, pos):
        """Legacy function to load block designs from a .dat file"""
        l = []
        for i in range(len):
            if data[pos] == 0xFF:
                block_index = (data[pos + 1] << 16) + (data[pos + 2] << 8) + data[pos + 3]
                pos += 3
            else:
                block_index = data[pos]

            l.append(block_index)
            pos += 1
        return cls(l), pos

    def __repr__(self):
        return f"Block_Design([{','.join(str(i) for i in self.blocks)}]"


@dataclass
class BitMapPicture:
    """Bit map picture """
    size: Size
    obj_generator: int
    ending: int = 0
    offset_x: int = 0
    offset_y: int = 0

    with open(data_dir.joinpath("object_definitions_reference_names.yaml")) as f:
        STR_TO_ORIENTATION = yaml.load(f, Loader=Loader)

    @property
    def orientation(self):
        """Legacy property for compatibility"""
        return self.obj_generator

    @classmethod
    def from_dict(cls, dic):
        """Makes a bmp from a dictionary of values"""
        size = Size.from_dict(dic["size"]) if "size" in dic else Size(1, 1)
        obj_generator = cls.STR_TO_ORIENTATION[dic["obj_generator"]] if "obj_generator" in dic else [0xFF]
        ending = dic["ending"] if "ending" in dic else 0
        offset_x = dic["offset_x"] if "offset_x" in dic else 0
        offset_y = dic["offset_y"] if "offset_y" in dic else 0
        return cls(size, obj_generator, ending, offset_x, offset_y)

    @classmethod
    def from_ints(cls, width: int, height: int, obj_generator: int, ending: int, offset_x: int = 0, offset_y: int = 0):
        """Makes a bmp from a series of ints"""
        try:
            return cls(Size(width, height), obj_generator, ending, offset_x, offset_y)
        except TypeError as e:
            logging.critical(f"{e} from BitMapPicture.from_ints({width}, {height}, {obj_generator}, {ending}, "
                             f"{offset_x}, {offset_y}")
            print(e)


@dataclass
class ObjectDefinition:
    """Determines what an object (Block generator or sprite generator is)"""
    object_design: list
    domain: int = 0
    bmp: BitMapPicture = BitMapPicture.from_ints(1, 1, 0, 0)
    range: Range = Range(-1, -1)
    bytes: int = 0
    block_design: Block_Design = Block_Design()
    description: str = ""
    overload: tuple = ()

    @property
    def is_4byte(self):
        """Legacy property for compatibility"""
        return self.bytes == 4

    @property
    def object_design_length(self):
        """Legacy property for compatibility"""
        return len(self.object_design)

    @object_design_length.setter
    def object_design_length(self, length: int):
        """Legacy property for compatibility"""
        pass

    @property
    def rom_object_design(self):
        """Legacy property for compatibility"""
        return self.block_design.blocks

    @rom_object_design.setter
    def rom_object_design(self, design: list):
        """Legacy property for compatibility"""
        self.object_design = design

    @property
    def ending(self):
        """Legacy property for compatibility"""
        return self.bmp.ending

    @property
    def bmp_width(self):
        """Legacy property for compatibility"""
        return self.bmp.size.width

    @property
    def bmp_height(self):
        """Legacy property for compatibility"""
        return self.bmp.size.height

    @property
    def orientation(self):
        """Legacy property for compatibility"""
        return self.bmp.orientation

    def log(self):
        """Logs all of the class' attributes"""
        logging.debug(f"{self}")

    def __repr__(self):
        return f"ObjectDefinition {self.description}"

    @classmethod
    def from_string(cls, string: str):
        """Legacy method for old data.dat file"""
        string = string.rstrip().replace("<", "").replace(">", "")

        domain, min_value, max_value, bmp_width, bmp_height, *object_design, orientation, ending, extra_bytes, \
            description = string.split(",")

        if string.find("|") >= 0:
            offset_x, offset_y, offset_sub_x = string.split("|")[1].split(" ")
        else:
            offset_x, offset_y = "0", "0"

        return cls(
            object_design=[int(i) for i in object_design],
            domain=int(domain),
            range=Range(start=int(min_value, 16), end=int(max_value, 16)),
            bmp=BitMapPicture.from_ints(
                int(bmp_width), int(bmp_height), int(orientation), int(ending),
                offset_x=int(offset_x), offset_y=int(offset_y)
            ),
            bytes=int(extra_bytes) + 3,
            description=description.split("|")[0].replace(";;", ",")
        )


enemy_handle_x, enemy_handle_x2, enemy_handle_y = [], [], []


def load_obj_definitions_from_yaml(file_path):
    """Loads all the object definitions at once from a .yaml file"""
    with open(file_path) as f:
        obj_definitions = yaml.load(f, Loader=Loader)

    for key, tileset in obj_definitions.items():
        for k, tile in tileset.items():
            tileset[k] = ObjectDefinition(
                object_design=tile["object_design"] if "object_design" in tile else [0],
                domain=tile["domain"] if "domain" in tile else 0,
                bmp=BitMapPicture.from_dict(tile["bmp"]),
                range=Range.from_dict(tile["range"]),
                bytes=tile["bytes"],
                description=tile["description"],
                block_design=Block_Design(tile["block_design"]),
                overload=tile["overload"] if "overload" in tile else ()
            )

            if int(key) == ENEMY_OBJECT_DEFINITION and int(k) <= 236:
                enemy_handle_x.append(str(tileset[k].bmp.offset_x))
                enemy_handle_y.append(str(tileset[k].bmp.offset_y))

            tileset[k].log()

    return obj_definitions


def load_obj_definitions_from_dat(file_path):
    """Loads all the object definitions at once from a .dat file"""
    obj_metadata, tileset, idx = [[]], 0, 0
    with open(file_path, "r") as f:
        for line in f.readlines():
            if line.startswith(";"):
                continue
            if not line.rstrip():
                obj_metadata.append([])
                tileset, idx = tileset + 1, 0
            else:
                obj_def = ObjectDefinition.from_string(line)
                obj_metadata[tileset].append(obj_def)
                obj_def.log()
                if tileset == ENEMY_OBJECT_DEFINITION and idx <= 236:
                    if line.find("|") >= 0:
                        x, y, x2 = line.split("|")[1].split(" ")
                    else:
                        x, y, x2 = "0 0 0".split(" ")

                    enemy_handle_x.append(x)
                    enemy_handle_x2.append(x2)
                    enemy_handle_y.append(y)
                idx += 1
    return obj_metadata


object_metadata = load_obj_definitions_from_yaml(data_dir.joinpath("object_definitions.yaml"))


def load_all_obj_definitions():
    """A method to generate all object definitions for debugging or recreations"""
    for object_definition in range(0, 11):

        if object_definition == ENEMY_OBJECT_DEFINITION:
            continue

        with open(data_dir.joinpath(f"romobjs{object_definition}.dat"), "rb") as obj_def:
            data = obj_def.read()

        object_count = data[0]

        if object_definition != 0 and object_count < 0xF7:
            # first byte did not represent the object_count
            object_count = 0xFF
            position = 0
        else:
            position = 1

        for object_index in range(object_count):
            object_design_length = data[position]
            position += 1

            bd, position = Block_Design.from_dat_file(data, object_design_length, position)
            try:
                object_metadata[object_definition][object_index].block_design = bd
            except:
                pass


def load_object_definitions(object_set):
    """Loads the object definitions with the block definitions"""
    global object_metadata

    object_definition = OBJECT_SET_TO_DEFINITION[object_set]

    return object_metadata[object_definition]


def load_object_definition_tile(object_set: int, tile: int, domain: int):
    """Loads the object definition for a tile"""
    object_definition = OBJECT_SET_TO_DEFINITION[object_set]

    for _, obj in object_metadata[object_definition].items():
        if obj.range.is_inside(tile) and obj.domain == domain:
            return obj
    return None
