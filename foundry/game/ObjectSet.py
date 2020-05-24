from foundry.game.ObjectDefinitions import ObjectDefinition, load_object_definitions
from smb3parse.objects.object_set import ENEMY_ITEM_OBJECT_SET, ObjectSet as _ObjectSet


class ObjectSet:
    def __init__(self, object_set_number: int):
        self._internal_object_set = _ObjectSet(object_set_number)

        self.number = self._internal_object_set.number

        if self.number == ENEMY_ITEM_OBJECT_SET:
            self.name = "Enemy Object Set"
        else:
            self.name = self._internal_object_set.name

        self.definitions = load_object_definitions(self.number)

    def get_definition_of(self, object_id: int) -> ObjectDefinition:
        return self.definitions[object_id]

    def get_ending_offset(self) -> int:
        if self.number == ENEMY_ITEM_OBJECT_SET:
            raise ValueError(f"This method shouldn't be called for the {self.name}")

        return self._internal_object_set.ending_graphic_offset

    def get_object_byte_length(self, domain: int, object_id: int) -> int:
        if self.number == ENEMY_ITEM_OBJECT_SET:
            raise ValueError(f"This method shouldn't be called for the {self.name}")

        return self._internal_object_set.object_length(domain, object_id)
