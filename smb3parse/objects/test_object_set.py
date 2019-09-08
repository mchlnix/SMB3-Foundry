import pytest
from hypothesis import given, strategies

from smb3parse.objects import MIN_DOMAIN, MAX_DOMAIN, MIN_ID_VALUE, MAX_ID_VALUE
from smb3parse.objects.object_set import ObjectSet, ENEMY_ITEM_OBJECT_SET


def test_enemy_item_set_value_error():
    enemy_item_set = ObjectSet(ENEMY_ITEM_OBJECT_SET)

    with pytest.raises(ValueError):
        assert enemy_item_set.ending_graphic_offset

    with pytest.raises(ValueError):
        enemy_item_set.is_in_level_range(0)


@given(
    domain=strategies.integers(min_value=MIN_DOMAIN, max_value=MAX_DOMAIN),
    object_id=strategies.integers(min_value=MIN_ID_VALUE, max_value=MAX_ID_VALUE),
)
def test_enemy_item_set_object_length(domain, object_id):
    enemy_item_set = ObjectSet(ENEMY_ITEM_OBJECT_SET)

    assert enemy_item_set.object_length(domain, object_id) == 3
