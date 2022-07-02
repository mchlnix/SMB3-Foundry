from smb3parse.levels import FIRST_VALID_ROW
from smb3parse.levels.data_points import LevelPointerData, SpriteData


def test_read_values(world_1):
    sprites = list(world_1.gen_sprites())

    assert sprites[0].is_at(1, 7 - FIRST_VALID_ROW, 13)
    assert sprites[1].is_at(1, 8 - FIRST_VALID_ROW, 12)
    assert sprites[2].is_at(1, 8 - FIRST_VALID_ROW, 10)


def test_sprite_write_back(world_1):
    original_sprite = SpriteData(world_1, 0)

    original_sprite.screen += 1
    original_sprite.x += 1
    original_sprite.y += 1
    original_sprite.type += 1
    original_sprite.item += 1

    original_sprite.write_back()

    updated_sprite = SpriteData(world_1, 0)

    assert updated_sprite.screen == original_sprite.screen
    assert updated_sprite.x == original_sprite.x
    assert updated_sprite.y == original_sprite.y
    assert updated_sprite.type == original_sprite.type
    assert updated_sprite.item == original_sprite.item


def test_level_pointer_write_back(world_1):
    original_level_pointer = LevelPointerData(world_1, 5)

    original_level_pointer.screen += 1
    original_level_pointer.x += 1
    original_level_pointer.y += 1
    original_level_pointer.object_set += 1
    original_level_pointer.level_offset += 1
    original_level_pointer.enemy_offset += 1

    original_level_pointer.write_back()

    updated_level_pointer = LevelPointerData(world_1, 5)

    assert updated_level_pointer.screen == original_level_pointer.screen
    assert updated_level_pointer.x == original_level_pointer.x
    assert updated_level_pointer.y == original_level_pointer.y
    assert updated_level_pointer.object_set == original_level_pointer.object_set
    assert updated_level_pointer.level_offset == original_level_pointer.level_offset
    assert updated_level_pointer.enemy_offset == original_level_pointer.enemy_offset


def test_level_pointer_addresses_to_offset(world_1):
    level_pointer = LevelPointerData(world_1, 5)
    other_level_pointer = LevelPointerData(world_1, 5)

    level_pointer.level_address = level_pointer.level_address
    level_pointer.enemy_address = level_pointer.enemy_address

    level_pointer.index = level_pointer.index

    assert other_level_pointer.level_address == level_pointer.level_address
    assert other_level_pointer.enemy_address == level_pointer.enemy_address
    assert other_level_pointer.level_offset == level_pointer.level_offset
    assert other_level_pointer.enemy_offset == level_pointer.enemy_offset
