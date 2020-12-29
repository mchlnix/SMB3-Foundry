from abc import ABC

from foundry.core.util import LEVEL_MIN_LENGTH, LEVEL_MAX_LENGTH, \
    LEVEL_PARTITION_LENGTH
from smb3parse.objects.object_set import ObjectSet


def is_valid_level_length(level_length: int) -> bool:
    return level_length in range(LEVEL_MIN_LENGTH, LEVEL_MAX_LENGTH + 1, LEVEL_PARTITION_LENGTH)


class LevelBase(ABC):
    width: int
    height: int

    def __init__(self, object_set_number: int, layout_address: int):
        self.layout_address = layout_address

        self.object_set_number = object_set_number
        self.object_set = ObjectSet(self.object_set_number)
