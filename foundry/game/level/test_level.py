import pytest

from foundry.game.gfx.objects import EnemyItem, Jump, LevelObject
from foundry.game.level.Level import LEVEL_DEFAULT_HEIGHT


@pytest.mark.parametrize(
    "method, params", [("add_object", (0, 0, 0, 0, None)), ("add_enemy", (0, 0, 0)), ("add_jump", tuple())]
)
def test_level_too_big(rom, level, method, params, qtbot):
    # GIVEN a level
    pass

    # WHEN you add an object
    getattr(level, method)(*params)

    # THEN it should recognize itself as being too big
    assert level.is_too_big()


def test_not_too_big_jump(level):
    # GIVEN a level
    pass

    # WHEN you remove a jump
    jump = level.jumps[0]
    assert isinstance(jump, Jump)

    level.remove_jump(jump)

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
    x, y = 0, LEVEL_DEFAULT_HEIGHT * 2

    level.add_object(domain, object_index, x, y, None)

    # THEN that object is still the same and at the correct position
    added_object = level.objects[0]

    assert added_object.domain == domain
    assert added_object.obj_index == object_index
    assert added_object.rendered_base_x == x
    assert added_object.rendered_base_y == y
