class ROM:
    data = bytearray()

    def __init__(self, path="SMB3.nes"):
        if not ROM.data:
            with open(path, "rb") as rom:
                ROM.data = list(rom.read())

        self.position = 0

    def seek(self, position):
        if position > len(ROM.data) or position < 0:
            return -1

        self.position = position

        return 0

    def get_byte(self, position=-1):
        if position >= 0:
            k = self.seek(position) >= 0
        else:
            k = self.position < len(ROM.data)

        if k:
            return_byte = ROM.data[self.position]
        else:
            return_byte = 0

        self.position += 1

        return return_byte

    def peek_byte(self, position=-1):
        old_position = self.position

        byte = self.get_byte(position)

        self.position = old_position

        return byte

    def put_byte(self, byte, position=-1):
        if position >= 0:
            self.seek(position)

        ROM.data[self.position] = byte

        self.position += 1

    def bulk_read(self, count, position=-1):
        if position >= 0:
            self.seek(position)
        else:
            position = self.position

        self.position += count

        return ROM.data[position:position+count]


object_sets = {
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


def convert_object_sets(real_set):
    return object_sets.get(real_set, 1)


def get_enemy_size(index):
    pass
    # hx = enemyhandle_x2[enemy_array[0, i]]


# updates gui strings with level info
def update_level_info():
    pass


LEVEL_HEADER_LENGTH = 9  # bytes
ENEMY_SIZE = 3
OBJECT_3_SIZE = 3
OBJECT_3_FLAG = 3
OBJECT_4_SIZE = 4
OBJECT_4_FLAG = 4

COLOR_SIZE = 3
COLOR_COUNT = 64
NESPalette = []

tsa_object_set = bytearray([0, 2, 3, 1, 9, 12, 8, 5, 10, 11, 13, 13])

MODE_EDIT_OBJDEF = 0
MODE_EDIT_LEVEL = 1
MODE_EDIT_WORLD = 2

MAX_LEVEL_WIDTH = 0xFF
MAX_LEVEL_HEIGHT = 27  # todo correct?
BLOCK_WIDTH = 16
BLOCK_HEIGHT = 16

Object_Sizes = dict()
