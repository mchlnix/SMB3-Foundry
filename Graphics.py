class LevelObject:
    def __init__(self, data):
        self.data = data

        # where to look for the graphic data?
        self.domain = (data[0] & 0b1110_0000) >> 5

        # position relative to the start of the level (top)
        self.y_position = data[0] & 0b0001_1111

        # position relative to the start of the level (left)
        self.x_position = data[1]

        # describes what object it is
        self.type = data[2]


class ThreeByteObject(LevelObject):
    def __init__(self, data):
        super(ThreeByteObject, self).__init__(data)


class FourByteObject(LevelObject):
    def __init__(self, data):
        super(FourByteObject, self).__init__(data)

        # some objects have variable lengths (ground tiles)
        self.length = data[3]


class EnemyObject:
    def __init__(self, data):
        self.type = data[0]
        self.x_position = data[1]
        self.y_position = data[2]


