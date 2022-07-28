import abc

from smb3parse.levels import LevelBase


class LevelLike(LevelBase, abc.ABC):
    width: int
    height: int

    def __init__(self, object_set_number, layout_address):
        super(LevelLike, self).__init__(object_set_number, layout_address)

    @abc.abstractmethod
    def index_of(self, obj):
        pass

    @abc.abstractmethod
    def object_at(self, x, y):
        pass

    @abc.abstractmethod
    def get_all_objects(self):
        pass

    @abc.abstractmethod
    def draw(self, dc, block_length, transparency, show_expansion):
        pass
