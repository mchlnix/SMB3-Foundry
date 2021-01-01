from foundry.game.ObjectSet import ObjectSet
from smb3parse.objects.object_set import ENEMY_ITEM_OBJECT_SET


def test_enemy_names(main_window):
    warning_list = main_window.warning_list

    enemy_object_set = ObjectSet(ENEMY_ITEM_OBJECT_SET)

    enemy_names = [obj_def.description for obj_def in enemy_object_set.definitions]

    for enemy_name in warning_list._enemy_dict.keys():
        assert enemy_name in enemy_names
