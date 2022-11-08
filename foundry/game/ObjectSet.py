from foundry.game.ObjectDefinitions import ObjectDefinition, load_object_definitions
from smb3parse.objects.object_set import ENEMY_ITEM_OBJECT_SET, ObjectSet as SMB3ObjectSet


class ObjectSet(SMB3ObjectSet):
    def __init__(self, object_set_number: int):
        super(ObjectSet, self).__init__(object_set_number)

        if self.number == ENEMY_ITEM_OBJECT_SET:
            self.name = "Enemy Object Set"

        self.definitions = load_object_definitions(self.number)

    def get_definition_of(self, object_id: int) -> ObjectDefinition:
        return self.definitions[object_id]

    def get_ending_offset(self) -> int:
        if self.number == ENEMY_ITEM_OBJECT_SET:
            raise ValueError(f"This method shouldn't be called for the {self.name}")

        return self.ending_graphic_offset
