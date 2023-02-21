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
from foundry.gui.settings import Settings
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
    return os.environ.get("PYTEST_CURRENT_TEST", "no_test_name").split(":")[-1].replace("/", "_")


level_data = []
world_data = []
level_test_name = []
world_test_name = []

with Path(data_dir / "levels.dat").open("r") as level_data_file:
    for line in level_data_file.readlines():
        parts = line.strip().split(",")

        world_no, level_no = map(int, parts[:2])
        level_address, enemy_address, object_set_number = [int(number, 16) for number in parts[2:-1]]
        level_name = parts[-1]

        if object_set_number == WORLD_MAP_OBJECT_SET:
            world_data.append((level_name, level_address, enemy_address, object_set_number, False))
            world_data.append((level_name, level_address, enemy_address, object_set_number, True))
            world_test_name.append(f"Overworld {world_no} - {level_name}")
            world_test_name.append(f"Overworld {world_no} - {level_name} - Bordered")
            continue

        level_data.append((level_name, level_address - HEADER_LENGTH, enemy_address, object_set_number, False))
        level_data.append((level_name, level_address - HEADER_LENGTH, enemy_address, object_set_number, True))

        level_test_name.append(f"Level {world_no}-{level_no} - {level_name}, no transparency")
        level_test_name.append(f"Level {world_no}-{level_no} - {level_name}")


@pytest.fixture
def settings():
    settings = Settings()
    settings.setValue("level view/block_transparency", True)
    settings.setValue("level view/draw_jumps", True)
    settings.setValue("level view/draw_mario", True)
    settings.setValue("level view/draw_grid", True)
    settings.setValue("level view/draw_expansion", True)
    settings.setValue("level view/draw_jump_on_objects", True)
    settings.setValue("level view/draw_items_in_blocks", True)
    settings.setValue("level view/draw_invisible_items", True)
    settings.setValue("level view/draw_autoscroll", True)
    settings.setValue("level view/object_tooltip_enabled", False)

    settings.setValue("world view/show grid", True)
    settings.setValue("world view/show border", False)
    settings.setValue("world view/show level pointers", True)
    settings.setValue("world view/show sprites", True)
    settings.setValue("world view/show airship paths", 0b111)
    settings.setValue("world view/show start position", True)
    settings.setValue("world view/show locks", True)
    settings.setValue("world view/show pipes", True)

    return settings


@pytest.mark.parametrize("world_info", world_data, ids=world_test_name)
def test_world(world_info, settings, qtbot):
    level_ref = LevelRef()

    show_border = world_info[-1]

    level_ref.load_level(*world_info[:-1])

    Block._block_cache.clear()

    # monkeypatch level names, since the level name data is broken atm
    level_ref.level.name = current_test_name()

    settings.setValue("world view/show border", show_border)

    world_view = WorldView(None, level_ref, settings, WorldContextMenu(level_ref))

    world_view.zoom_in()

    rect = QRect(QPoint(0, 0), QSize(world_view.sizeHint()))

    world_view.setGeometry(rect)

    _test_level_against_reference(world_view, qtbot)


@pytest.mark.parametrize("level_info", level_data, ids=level_test_name)
def test_level(level_info, settings, qtbot):
    *level_info, transparent = level_info
    level_ref = LevelRef()
    level_ref.load_level(*level_info)

    Block._block_cache.clear()

    # monkeypatch level names, since the level name data is broken atm
    level_ref.level.name = current_test_name()

    settings.setValue("level view/block_transparency", transparent)

    level_view = LevelView(None, level_ref, settings, LevelContextMenu(level_ref))

    rect = QRect(QPoint(0, 0), QSize(*level_ref.level.size) * 16)

    level_view.setGeometry(rect)

    _test_level_against_reference(level_view, qtbot)


@pytest.mark.parametrize("jump_test_name", ["jump_vertical_ref", "jump_horizontal_ref"])
def test_draw_jumps(jump_test_name, level, settings, qtbot):
    with open(str(Path(__file__).parent / f"{jump_test_name}.m3l"), "rb") as m3l_file:
        level.from_m3l(bytearray(m3l_file.read()))

        ref = LevelRef()
        ref._internal_level = level

        settings.setValue("level view/draw_grid", False)

        level_view = LevelView(None, ref, settings, LevelContextMenu(ref))

        level_view.resize(level_view.sizeHint())

        compare_images(jump_test_name, str(Path(__file__).parent / f"{jump_test_name}.png"), level_view.grab())


def _get_all_m3l_files(with_ending=True):
    for path in m3l_dir.iterdir():
        if path.match("*.m3l"):
            if with_ending:
                yield path
            else:
                yield path.stem


@pytest.mark.parametrize("m3l_file_name", _get_all_m3l_files(), ids=_get_all_m3l_files(False))
def test_draw_m3ls(m3l_file_name, level, settings, qtbot):
    with open(m3l_file_name, "rb") as m3l_file:
        level.from_m3l(bytearray(m3l_file.read()))

        ref = LevelRef()
        ref._internal_level = level

        settings.setValue("level view/draw_grid", False)

        level_view = LevelView(None, ref, settings, LevelContextMenu(ref))

        compare_images(m3l_file_name.stem, str(reference_image_dir / f"{m3l_file_name.stem}.png"), level_view.grab())
