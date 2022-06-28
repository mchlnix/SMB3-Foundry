from smb3parse.levels import FIRST_VALID_ROW
from smb3parse.levels.data_points import SpriteData


def test_read_values(world_1):
    sprites = list(world_1.gen_sprites())

    assert sprites[0].is_at(1, 7 - FIRST_VALID_ROW, 13)
    assert sprites[1].is_at(1, 8 - FIRST_VALID_ROW, 12)
    assert sprites[2].is_at(1, 8 - FIRST_VALID_ROW, 10)


def test_write_back(rom, world_1):
    original_sprite = SpriteData(rom, world_1, 0)

    original_sprite.screen += 1
    original_sprite.x += 1
    original_sprite.y += 1
    original_sprite.type += 1
    original_sprite.item += 1

    original_sprite.write_back()

    updated_sprite = SpriteData(rom, world_1, 0)

    assert updated_sprite.screen == original_sprite.screen
    assert updated_sprite.x == original_sprite.x
    assert updated_sprite.y == original_sprite.y
    assert updated_sprite.type == original_sprite.type
    assert updated_sprite.item == original_sprite.item
