ENEMY_BANK = 12

HORIZONTAL = 0
VERTICAL = 1  # vertical downward
DIAG_DOWN_LEFT = 2
DESERT_PIPE_BOX = 3
DIAG_DOWN_RIGHT = 4
DIAG_UP_RIGHT = 5
HORIZ_TO_GROUND = 6
HORIZONTAL_2 = 7  # special case of horizontal, basically floating boxes
DIAG_WEIRD = 8  #
SINGLE_BLOCK_OBJECT = 9
CENTERED = 10  # like spinning platforms
PYRAMID_TO_GROUND = 11
PYRAMID_TO_NEXT = 12  # to the ground or next object
TO_THE_SKY = 13
ENDING = 14

UNIFORM = 0
END_ON_TOP_OR_LEFT = 1
END_ON_BOTTOM_OR_RIGHT = 2
TWO_ENDS = 3


class ObjectDefinition:
    def __init__(self, string):
        string = string.rstrip().replace("<", "").replace(">", "")

        self.object_domain, self.min_value, self.max_value, self.bmp_width, self.bmp_height, *self.object_design, \
            self.orientation, self.ends, self.obj_flag, self.object_description = string.split(",")

        self.bmp_width = int(self.bmp_width)
        self.bmp_height = int(self.bmp_height)
        self.orientation = int(self.orientation)
        self.ends = int(self.ends)
        self.obj_flag = int(self.obj_flag)

        self.object_design2 = []
        self.rom_object_design = []

        for index, item in enumerate(self.object_design):
            self.object_design[index] = int(item)  # original data
            self.object_design2.append(0)  # data after trimming through romobjset*.dat file?
            self.rom_object_design.append(self.object_design[index])
            self.object_design_length = index + 1  # todo necessary when we have len()?

        self.object_description.replace(";;", ",")

        self.object_description = self.object_description.split("|")[0]


class ObjectSize:
    def __init__(self):
        self.left = self.right = 0
        self.top = self.bottom = 0
        self.width = self.height = 0
        self.handle_x = self.handle_y = 0
