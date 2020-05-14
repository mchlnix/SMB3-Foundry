import pytest
from PySide2.QtCore import QPoint, QRect, QSize
from PySide2.QtGui import QPaintEvent

from foundry import data_dir
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.ContextMenu import ContextMenu
from foundry.gui.LevelView import LevelView
from smb3parse.levels import HEADER_LENGTH
from smb3parse.objects.object_set import WORLD_MAP_OBJECT_SET

level_data = []
test_name = []

with open(data_dir / "levels.dat", "r") as level_data_file:
    for line in level_data_file.readlines():
        world_no, level_no, level_address, enemy_address, object_set_number, level_name = line.strip().split(",")

        world_no = int(world_no)
        level_no = int(level_no)

        level_address = int(level_address, 16) - HEADER_LENGTH

        enemy_address = int(enemy_address, 16)

        object_set_number = int(object_set_number, 16)

        if object_set_number == WORLD_MAP_OBJECT_SET:
            continue

        level_data.append((world_no, level_no, level_address, enemy_address, object_set_number))
        test_name.append(f"Level {world_no}-{level_no}: {level_name}")


@pytest.mark.parametrize("level_info", level_data, ids=test_name)
def test_level(level_info, qtbot):
    level_ref = LevelRef()
    level_ref.load_level(*level_info)

    level_view = LevelView(None, level_ref, ContextMenu(level_ref))

    level_view.paintEvent(QPaintEvent(QRect(QPoint(0, 0), QSize(*level_ref.level.size) * 16)))
