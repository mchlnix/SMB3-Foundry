from foundry.game.ObjectDefinitions import load_object_definitions, ObjectDefinition
from smb3parse.objects.object_set import ObjectSet as _ObjectSet

ENEMY_OBJECT_SET = 16


class Tileset:
    def __init__(self, object_set_number: int):
        self.object_set_number = object_set_number

        self._internal_object_set = _ObjectSet(object_set_number)

        self.number = self._internal_object_set.number

        if self.number == ENEMY_OBJECT_SET:
            self.name = "Enemy Object Set"
        else:
            self.name = self._internal_object_set.name

        self.background_block = self._internal_object_set.background_block
        self.definitions = load_object_definitions(self.number)

    def get_definition_of(self, object_id: int) -> ObjectDefinition:
        try:
            return self.definitions[object_id]
        except KeyError:
            print(f"The sprite {object_id} does not exist")
            return self.definitions[0]

    def get_ending_offset(self) -> int:
        if self.number == ENEMY_OBJECT_SET:
            raise ValueError(f"This method shouldn't be called for the {self.name}")

        return self._internal_object_set.ending_graphic_offset

    def get_object_byte_length(self, domain: int, object_id: int) -> int:
        if self.number == ENEMY_OBJECT_SET:
            raise ValueError(f"This method shouldn't be called for the {self.name}")

        return self._internal_object_set.object_length(domain, object_id)

    def __str__(self):
        return f"Tileset({self.object_set_number}) aka {self.name}"

    def __repr__(self):
        return f"Tileset({self.object_set_number})"