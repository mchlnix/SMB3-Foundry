from functools import lru_cache

from foundry.game.File import ROM
from foundry.game.ObjectDefinitions import ObjectDefinition, load_object_definitions
from smb3parse.objects.object_set import (
    ENEMY_ITEM_OBJECT_SET,
    ObjectSet as SMB3ObjectSet,
)


ENDING_OBJECT_BASE_OFFSET = 0x1C8F9
"""
There are different Level Ending Objects. The design and necessary blocks to use are written into the ROM at this
address. To figure out which belongs to which Object Set we need to get the index for said Object Set and then multiply
by ENDING_OBJECT_BLOCK_COUNT.
"""

ENDING_OBJECT_BLOCK_COUNT = 96
"""Size in blocks of Level Ending Object data per object saved in the ROM."""


class ObjectSet(SMB3ObjectSet):
    def __init__(self, object_set_number: int):
        super(ObjectSet, self).__init__(ROM(), object_set_number)

        if self.number == ENEMY_ITEM_OBJECT_SET:
            self.name = "Enemy Object Set"

        self.definitions = load_object_definitions(self.number)

    def get_definition_of(self, object_id: int) -> ObjectDefinition:
        return self.definitions[object_id]

    def get_ending_offset(self) -> int:
        """
        The blocks that make up the ending Object are hard coded in the ROM. This function will return the offset into
        the ROM, that corresponds to this Object Set.
        """
        if self.number == ENEMY_ITEM_OBJECT_SET:
            raise ValueError(f"This method shouldn't be called for the {self.name}")

        return ENDING_OBJECT_BASE_OFFSET + self.ending_graphic_index * ENDING_OBJECT_BLOCK_COUNT

    @staticmethod
    @lru_cache(16)
    def from_number(object_set_num: int) -> "ObjectSet":
        """Helper function, that is cacheable, since initializers are not."""
        return ObjectSet(object_set_num)
