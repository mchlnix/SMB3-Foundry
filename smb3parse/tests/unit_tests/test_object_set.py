from pathlib import Path

import pytest
from hypothesis import given, strategies

from smb3parse.objects import MAX_DOMAIN, MAX_ID_VALUE, MIN_DOMAIN, MIN_ID_VALUE
from smb3parse.objects.object_set import ENEMY_ITEM_OBJECT_SET, MAX_OBJECT_SET, MIN_OBJECT_SET, ObjectSet
from smb3parse.tests.conftest import test_rom_path
from smb3parse.util.rom import Rom

rom = Rom(Path(test_rom_path).open("rb").read())


def test_enemy_item_set_value_error():
    enemy_item_set = ObjectSet(rom, ENEMY_ITEM_OBJECT_SET)

    with pytest.raises(ValueError):
        assert enemy_item_set.ending_graphic_offset


@given(
    domain=strategies.integers(min_value=MIN_DOMAIN, max_value=MAX_DOMAIN),
    object_id=strategies.integers(min_value=MIN_ID_VALUE, max_value=MAX_ID_VALUE),
)
def test_enemy_item_set_object_length(domain, object_id):
    enemy_item_set = ObjectSet(rom, ENEMY_ITEM_OBJECT_SET)

    assert enemy_item_set.object_length(domain, object_id) == 3


@given(
    object_set_number=strategies.integers(min_value=MIN_OBJECT_SET, max_value=MAX_OBJECT_SET),
    domain=strategies.integers(min_value=MIN_DOMAIN, max_value=MAX_DOMAIN),
    object_id=strategies.integers(min_value=MIN_ID_VALUE, max_value=MAX_ID_VALUE),
)
def test_object_length(object_set_number, domain, object_id):
    object_set = ObjectSet(rom, object_set_number)

    assert object_set.object_length(domain, object_id) in [3, 4]
