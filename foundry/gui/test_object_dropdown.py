from foundry.conftest import level_1_2_enemy_address, level_1_2_object_address, level_2, world_1
from smb3parse.objects.object_set import HILLY_OBJECT_SET


def test_object_update_on_level_change(main_window):
    # GIVEN the main window and the object dropdown
    object_dropdown = main_window.object_dropdown

    original_object_set = main_window.level_ref.object_set_number
    original_objects = "".join(map(str, object_dropdown._object_items))

    # WHEN the level is changed
    main_window.update_level(world_1, level_2, level_1_2_object_address, level_1_2_enemy_address, HILLY_OBJECT_SET)

    assert original_object_set != main_window.level_ref.object_set_number

    # THEN the objects in the dropdown should be changed
    new_objects = "".join(map(str, object_dropdown._object_items))

    assert original_objects != new_objects, "Objects didn't change."

    assert not new_objects.startswith(original_objects), "Dropdown wasn't cleared before adding new objects."
