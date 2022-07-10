import os
from pathlib import Path

import pytest
from PySide6.QtCore import QPoint, QRect, QSize

from foundry import data_dir
from foundry.conftest import compare_images
from foundry.game.gfx.drawable.Block import Block
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.ContextMenu import LevelContextMenu
from foundry.gui.LevelView import LevelView
from foundry.gui.MainView import MainView
from foundry.gui.WorldView import WorldView
from scribe.gui.world_view_context_menu import WorldContextMenu
from smb3parse.levels import HEADER_LENGTH
from smb3parse.objects.object_set import WORLD_MAP_OBJECT_SET

reference_image_dir = Path(__file__).parent.joinpath("test_refs")
reference_image_dir.mkdir(parents=True, exist_ok=True)

m3l_dir = Path(__file__).parent.joinpath("test_m3ls")
m3l_dir.mkdir(parents=True, exist_ok=True)


def _test_level_against_reference(main_view: MainView, qtbot):
    qtbot.addWidget(main_view)

    image_name = f"{main_view.level_ref.level.name}.png"
    ref_image_path = str(reference_image_dir.joinpath(image_name))

    main_view.repaint()

    compare_images(image_name, ref_image_path, main_view.grab())


def current_test_name():
    return os.environ.get("PYTEST_CURRENT_TEST").split(":")[-1].replace("/", "_")


level_data = []
world_data = []
level_test_name = []
world_test_name = []

with open(data_dir / "levels.dat", "r") as level_data_file:
    for line in level_data_file.readlines():
        world_no, level_no, level_address, enemy_address, object_set_number, level_name = line.strip().split(",")

        world_no = int(world_no)
        level_no = int(level_no)

        level_address = int(level_address, 16)

        enemy_address = int(enemy_address, 16)

        object_set_number = int(object_set_number, 16)

        if object_set_number == WORLD_MAP_OBJECT_SET:
            world_data.append((level_name, level_address, enemy_address, object_set_number))
            world_test_name.append(f"Overworld {world_no} - {level_name}")
            continue

        level_data.append((level_name, level_address - HEADER_LENGTH, enemy_address, object_set_number, False))
        level_data.append((level_name, level_address - HEADER_LENGTH, enemy_address, object_set_number, True))

        level_test_name.append(f"Level {world_no}-{level_no} - {level_name}, no transparency")
        level_test_name.append(f"Level {world_no}-{level_no} - {level_name}")


@pytest.mark.parametrize("world_info", world_data, ids=world_test_name)
def test_world(world_info, qtbot):
    level_ref = LevelRef()
    level_ref.load_level(*world_info)

    Block._block_cache.clear()

    # monkeypatch level names, since the level name data is broken atm
    level_ref.level.name = current_test_name()

    world_view = WorldView(None, level_ref, WorldContextMenu(level_ref))
    world_view.zoom_in()

    rect = QRect(QPoint(0, 0), QSize(*level_ref.level.size) * 16 * 2)

    world_view.setGeometry(rect)

    _test_level_against_reference(world_view, qtbot)


@pytest.mark.parametrize("level_info", level_data, ids=level_test_name)
def test_level(level_info, qtbot):
    *level_info, transparent = level_info
    level_ref = LevelRef()
    level_ref.load_level(*level_info)

    Block._block_cache.clear()

    # monkeypatch level names, since the level name data is broken atm
    level_ref.level.name = current_test_name()

    level_view = LevelView(None, level_ref, LevelContextMenu(level_ref))
    level_view.transparency = transparent
    level_view.draw_jumps = False
    level_view.draw_grid = False
    level_view.draw_autoscroll = True

    rect = QRect(QPoint(0, 0), QSize(*level_ref.level.size) * 16)

    level_view.setGeometry(rect)

    _test_level_against_reference(level_view, qtbot)


@pytest.mark.parametrize("jump_test_name", ["jump_vertical_ref", "jump_horizontal_ref"])
def test_draw_jumps(jump_test_name, level, qtbot):
    with open(str(Path(__file__).parent / f"{jump_test_name}.m3l"), "rb") as m3l_file:
        level.from_m3l(bytearray(m3l_file.read()))

        ref = LevelRef()
        ref._internal_level = level

        view = LevelView(None, ref, LevelContextMenu(ref))
        view.draw_jumps = True
        view.draw_grid = False

        view.resize(view.sizeHint())

        compare_images(jump_test_name, str(Path(__file__).parent / f"{jump_test_name}.png"), view.grab())


def _get_all_m3l_files(with_ending=True):
    for path in m3l_dir.iterdir():
        if path.match("*.m3l"):
            if with_ending:
                yield path
            else:
                yield path.stem


@pytest.mark.parametrize("m3l_file_name", _get_all_m3l_files(), ids=_get_all_m3l_files(False))
def test_draw_m3ls(m3l_file_name, level, qtbot):
    with open(m3l_file_name, "rb") as m3l_file:
        level.from_m3l(bytearray(m3l_file.read()))

        ref = LevelRef()
        ref._internal_level = level

        view = LevelView(None, ref, LevelContextMenu(ref))
        view.draw_grid = False

        compare_images(m3l_file_name.stem, str(reference_image_dir / f"{m3l_file_name.stem}.png"), view.grab())
