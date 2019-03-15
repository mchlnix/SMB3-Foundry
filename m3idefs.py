ENEMY_BANK = 12

EXT_SKY = 13


class ObjectDefinition:
    def __init__(self, string):
        string = string.rstrip().replace("<", "").replace(">", "")

        self.object_domain, self.min_value, self.max_value, self.bmp_width, self.bmp_height, *self.object_design, \
            self.orientation, self.ends, self.obj_flag, self.object_description = string.split(",")

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
