from smb3parse.levels import LevelBase

BASE_ENEMY_OFFSET = 0x00010
BASE_LEVEL_OFFSET = 0x10010


class Level(LevelBase):
    def __init__(self, memory_address):
        super(Level, self).__init__(memory_address)
