from abc import ABC

from smb3parse.objects.object_set import ObjectSet


class LevelBase(ABC):
    def __init__(self, object_set: ObjectSet, layout_address: int):
        self.layout_address = layout_address

        self.object_set = object_set
        self.object_set_number = object_set.number

    @property
    def width(self) -> int:
        raise NotImplementedError()

    @property
    def height(self) -> int:
        raise NotImplementedError()

    def point_in(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height
