import abc

from smb3parse.levels import LevelBase


class LevelLike(LevelBase, abc.ABC):
    width: int
    height: int

    def __init__(self, object_set_number, layout_address):
        super(LevelLike, self).__init__(object_set_number, layout_address)

        self.changed = False
        self.attached_to_rom = True

    @abc.abstractmethod
    def index_of(self, obj):
        pass

    @abc.abstractmethod
    def object_at(self, x, y):
        pass

    @abc.abstractmethod
    def get_object_names(self):
        pass

    @abc.abstractmethod
    def get_all_objects(self):
        pass

    @abc.abstractmethod
    def get_object(self, index):
        pass

    @abc.abstractmethod
    def remove_object(self, obj):
        pass

    @abc.abstractmethod
    def draw(self, dc, block_length, transparency, show_expansion):
        pass

    @abc.abstractmethod
    def to_bytes(self):
        pass

    @abc.abstractmethod
    def from_bytes(self, object_data, enemy_data):
        pass
