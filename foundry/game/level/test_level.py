import pytest
from PySide6.QtCore import QPoint

from foundry.game.gfx.objects import EnemyItem, Jump, LevelObject
from foundry.game.level.Level import LEVEL_DEFAULT_HEIGHT
from foundry.gui.asm import asm_to_bytes
from smb3parse.data_points import Position


@pytest.mark.parametrize(
    "method, params",
    [
        ("add_object_at", (QPoint(0, 0),)),
        ("add_enemy_at", (QPoint(0, 0),)),
        ("on_jump_added", tuple()),
    ],
)
def test_level_too_big(rom, main_window, method, params, qtbot):
    # GIVEN a level
    assert not main_window.level_ref.level.is_too_big()

    # WHEN you add an object
    getattr(main_window, method)(*params)

    # THEN it should recognize itself as being too big
    assert main_window.level_ref.level.is_too_big()


def test_not_too_big_jump(level):
    # GIVEN a level
    pass

    # WHEN you remove a jump
    jump = level.jumps[0]
    assert isinstance(jump, Jump)

    level.jumps.remove(jump)

    # THEN the level is not marked as too big
    assert not level.is_too_big()


def test_not_too_big_object(level):
    # GIVEN a level
    pass

    # WHEN you remove a object
    level_object = level.objects[0]
    assert isinstance(level_object, LevelObject)

    level.remove_object(level_object)

    # THEN the level is not marked as too big
    assert not level.is_too_big()


def test_not_too_big_enemy(level):
    # GIVEN a level
    pass

    # WHEN you remove an enemy
    enemy = level.enemies[0]
    assert isinstance(enemy, EnemyItem)

    level.remove_object(enemy)

    # THEN the level is not marked as too big
    assert not level.is_too_big()


def test_not_too_big_nothing(level):
    # GIVEN a level
    pass

    # WHEN we do nothing
    pass

    # THEN the level is not too big
    assert not level.is_too_big()


def test_level_insert_in_vertical_level(level):
    # GIVEN a vertical level without objects
    level.is_vertical = True

    level.objects.clear()
    level.enemies.clear()
    level.jumps.clear()

    # WHEN an object is added at a Y-value, too large for horizontal levels
    domain = object_index = 0x00
    pos = Position.from_xy(0, LEVEL_DEFAULT_HEIGHT * 2)

    level.add_object(domain, object_index, pos, None)

    # THEN that object is still the same and at the correct position
    added_object = level.objects[0]

    assert added_object.domain == domain
    assert added_object.obj_index == object_index
    assert added_object.rendered_base_x == pos.x
    assert added_object.rendered_base_y == pos.y


def test_to_asm(level):
    level_asm, enemy_asm = level.to_asm()
    (_, level_bytes), (__, enemy_bytes) = level.to_bytes()

    assert level_bytes + bytearray([0xFF]) == asm_to_bytes(level_asm)
    assert enemy_bytes == asm_to_bytes(enemy_asm)
