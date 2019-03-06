from Data import map_pointers, level_array, MAP_ENEMY_OFFSET


class ROM:
    def __init__(self, path):
        with open(path, "rb") as rom:
            self.data = list(rom.read())
        self.position = 0

    def seek(self, position):
        if position > len(self.data) or position < 0:
            return -1

        self.position = position

        return 0

    def get_byte(self, position=-1):
        if position >= 0:
            k = self.seek(position) >= 0
        else:
            k = self.position < len(self.data)

        if k:
            return_byte = self.data[self.position]
        else:
            return_byte = 0

        self.position += 1

        return return_byte

    def put_byte(self, byte, position=-1):
        if position >= 0:
            self.seek(position)

        self.data[self.position] = byte

        self.position += 1
