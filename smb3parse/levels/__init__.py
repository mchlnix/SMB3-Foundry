from smb3parse.objects.object_set import ObjectSet


class LevelBase:
    def __init__(self, memory_address: int):
        self._memory_address = memory_address

        self._width: int = 0
        self._height: int = 0

        self._object_set_index: int = 0
        self._object_set = ObjectSet(self._object_set_index)

    @property
    def memory_address(self):
        return self._memory_address

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def object_set(self):
        return self._object_set
