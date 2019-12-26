from smb3parse.objects.object_set import ObjectSet


class LevelBase:
    def __init__(self, memory_address: int):
        self._memory_address = memory_address

        self.width: int = 0
        self.height: int = 0

        self.object_set_index: int = 0
        self.object_set = ObjectSet(self.object_set_index)
