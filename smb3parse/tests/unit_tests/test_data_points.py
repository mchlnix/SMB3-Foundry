from itertools import starmap

from smb3parse.data_points import LevelPointerData, Position, SpriteData, WorldMapData
from smb3parse.util import compare_bytearrays


def test_read_values(world_1):
    sprites = list(world_1.gen_sprites())

    assert sprites[0].is_at(0, 7, 13)
    assert sprites[1].is_at(0, 8, 12)
    assert sprites[2].is_at(0, 8, 10)


def test_sprite_write_back(world_1):
    original_sprite = SpriteData(world_1.data, 0)

    original_sprite.screen += 1
    original_sprite.x += 1
    original_sprite.y += 1
    original_sprite.type += 1
    original_sprite.item += 1

    original_sprite.write_back()

    updated_sprite = SpriteData(world_1.data, 0)

    assert updated_sprite.screen == original_sprite.screen
    assert updated_sprite.x == original_sprite.x
    assert updated_sprite.y == original_sprite.y
    assert updated_sprite.type == original_sprite.type
    assert updated_sprite.item == original_sprite.item


def test_level_pointer_write_back(world_1):
    original_level_pointer = LevelPointerData(world_1.data, 5)

    original_level_pointer.screen += 1
    original_level_pointer.x += 1
    original_level_pointer.y += 1
    original_level_pointer.object_set += 1
    original_level_pointer.level_offset += 1
    original_level_pointer.enemy_offset += 1

    original_level_pointer.write_back()

    updated_level_pointer = LevelPointerData(world_1.data, 5)

    assert updated_level_pointer.screen == original_level_pointer.screen
    assert updated_level_pointer.x == original_level_pointer.x
    assert updated_level_pointer.y == original_level_pointer.y
    assert updated_level_pointer.object_set == original_level_pointer.object_set
    assert updated_level_pointer.level_offset == original_level_pointer.level_offset
    assert updated_level_pointer.enemy_offset == original_level_pointer.enemy_offset


def test_level_pointer_addresses_to_offset(world_1):
    level_pointer = LevelPointerData(world_1.data, 5)
    other_level_pointer = LevelPointerData(world_1.data, 5)

    level_pointer.level_address = level_pointer.level_address
    level_pointer.enemy_address = level_pointer.enemy_address

    level_pointer.index = level_pointer.index

    assert other_level_pointer.level_address == level_pointer.level_address
    assert other_level_pointer.enemy_address == level_pointer.enemy_address
    assert other_level_pointer.level_offset == level_pointer.level_offset
    assert other_level_pointer.enemy_offset == level_pointer.enemy_offset


def test_chance_level_count(world_8):
    assert world_8.data.level_count_screen_1 == 8
    assert world_8.data.level_count_screen_2 == 10
    assert world_8.data.level_count_screen_3 == 17
    assert world_8.data.level_count_screen_4 == 6

    old_x_pos_list_start = world_8.data.x_pos_list_start

    world_8.data.level_count_screen_1 += 2

    assert world_8.data.level_count_screen_1 == 8 + 2
    assert world_8.data.level_count_screen_2 == 10
    assert world_8.data.level_count_screen_3 == 17
    assert world_8.data.level_count_screen_4 == 6

    assert world_8.data.x_pos_list_start == old_x_pos_list_start + 2


def test_sort_level_pointers(world_1):
    original_level_pointers = world_1.level_pointers
    changed_level_pointers = original_level_pointers.copy()

    changed_level_pointers[2], changed_level_pointers[-2] = (
        changed_level_pointers[-2],
        changed_level_pointers[2],
    )

    assert original_level_pointers != changed_level_pointers

    assert original_level_pointers == list(sorted(changed_level_pointers))


def _compare_worlds(world_1, world_2):
    for attr_name in dir(world_1):
        if attr_name.startswith("_"):
            continue

        if callable(getattr(world_1, attr_name)):
            continue

        assert getattr(world_1, attr_name) == getattr(world_2, attr_name), attr_name


def test_change_index_of_world_1(rom):
    old_data = rom._data.copy()

    orig_world_1 = WorldMapData(rom, 0)
    orig_world_2 = WorldMapData(rom, 1)
    world_1 = WorldMapData(rom, 0)
    world_2 = WorldMapData(rom, 1)

    world_1.write_back()
    world_2.write_back()

    world_1.change_index(1)
    world_2.change_index(0)

    world_2.write_back()
    world_1.write_back()

    world_1.change_index(0)
    world_2.change_index(1)

    world_1.write_back()
    world_2.write_back()

    _compare_worlds(orig_world_1, world_1)
    _compare_worlds(orig_world_2, world_2)

    compare_bytearrays(old_data, rom._data)


def test_change_index_of_world_2(rom):
    orig_world_1 = WorldMapData(rom, 1)
    changed_world_1 = WorldMapData(rom, 1)

    changed_world_1.change_index(2)
    changed_world_1.change_index(1)

    _compare_worlds(orig_world_1, changed_world_1)


def test_reading_airship_travel_sets(world_1):
    set_0 = [
        (0x6, 0xA, 0),
        (0x6, 0x2, 0),
        (0xC, 0x2, 0),
        (0x6, 0xA, 0),
        (0x6, 0x2, 0),
        (0xC, 0x2, 0),
    ]
    assert world_1.data.airship_travel_sets[0] == list(starmap(Position, set_0))


def test_reading_locks(world_1):
    assert world_1.data.fortress_fx_count == 4
    assert world_1.data.fortress_fx[0].pos == Position(4, 5, 0)
    assert world_1.data.fortress_fx[0].replacement_block_index == 0x46

    assert world_1.data.fortress_fx_indexes == [0, 0, 0, 0]


def test_write_back_world_map(rom):
    old_data = rom._data.copy()

    WorldMapData(rom, 0).write_back()

    assert old_data == rom._data

    # get a world map data object
    orig_world_1 = WorldMapData(rom, 0)
    assert orig_world_1.screen_count == 1

    # change a level pointer, by setting it to a different screen
    original_level_index = 4
    a_level_pointer = orig_world_1.level_pointers[original_level_index]

    original_level_count_screen_1 = orig_world_1.level_count_screen_1
    original_level_count_screen_2 = orig_world_1.level_count_screen_2

    assert a_level_pointer.index == original_level_index
    assert a_level_pointer.screen == 0
    a_level_pointer.screen = 1

    orig_world_1.write_back()

    new_world_1 = WorldMapData(rom, 0)

    assert a_level_pointer.index != original_level_index
    assert orig_world_1.level_count_screen_1 == original_level_count_screen_1 - 1 == new_world_1.level_count_screen_1
    assert orig_world_1.level_count_screen_2 == original_level_count_screen_2 + 1 == new_world_1.level_count_screen_2
