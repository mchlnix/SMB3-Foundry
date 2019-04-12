ENEMY_BANK = 12

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


class ObjectDefinition:
    def __init__(self, string):
        string = string.rstrip().replace("<", "").replace(">", "")

        self.domain, self.min_value, self.max_value, self.bmp_width, self.bmp_height, *self.object_design, \
            self.orientation, self.ending, self.is_4byte, self.description = string.split(",")

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
