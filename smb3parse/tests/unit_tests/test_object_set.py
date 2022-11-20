from pathlib import Path

import pytest

from smb3parse.objects.object_set import ENEMY_ITEM_OBJECT_SET, ObjectSet
from smb3parse.tests.conftest import test_rom_path
from smb3parse.util.rom import Rom

rom = Rom(Path(test_rom_path).open("rb").read())


def test_enemy_item_set_value_error():
    enemy_item_set = ObjectSet(rom, ENEMY_ITEM_OBJECT_SET)

    with pytest.raises(ValueError):
        assert enemy_item_set.ending_graphic_index
