import pytest
from PySide6.QtCore import QPoint
from PySide6.QtGui import QMouseEvent, Qt

import foundry
from foundry.game.gfx.objects.sprite import Sprite
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.WorldView import WorldView
from smb3parse.constants import TILE_MUSHROOM_HOUSE_1
from smb3parse.data_points import WorldMapData
from smb3parse.levels import WORLD_MAP_BLANK_TILE_ID, WORLD_MAP_SCREEN_WIDTH
from smb3parse.objects.object_set import WORLD_MAP_OBJECT_SET


@pytest.fixture
def worldview(rom, qtbot):
    world_1 = WorldMapData(rom, 0)
    level_ref = LevelRef()
    level_ref.load_level("", world_1.layout_address, 0x0, WORLD_MAP_OBJECT_SET)

    worldview = WorldView(None, level_ref)

    return worldview


def drag_from_to(worldview, start_point: QPoint, end_point: QPoint, modifiers: Qt.KeyboardModifier = Qt.NoModifier):
    # click left on a tile
    click_event = QMouseEvent(QMouseEvent.MouseButtonPress, start_point, Qt.LeftButton, Qt.LeftButton, modifiers)
    worldview.mousePressEvent(click_event)

    # move the mouse, while holding down
    move_event = QMouseEvent(QMouseEvent.MouseMove, end_point, Qt.LeftButton, Qt.NoButton, modifiers)
    worldview.mouseMoveEvent(move_event)

    # let go of button, while out of bounds
    release_event = QMouseEvent(QMouseEvent.MouseButtonRelease, end_point, Qt.LeftButton, Qt.NoButton, modifiers)
    worldview.mouseReleaseEvent(release_event)


def test_moving_tiles_out_of_scene(worldview):
    # when moving tiles out of scene, they are simply set back from whence they came
    start_point = QPoint(100, 100)
    end_point = QPoint(*worldview.world.size) * worldview.block_length + QPoint(100, 100)

    assert TILE_MUSHROOM_HOUSE_1 == worldview._visible_object_at(start_point).type

    drag_from_to(worldview, start_point, end_point)

    assert TILE_MUSHROOM_HOUSE_1 == worldview._visible_object_at(start_point).type


def test_moving_tiles_in_scene(worldview):
    start_point = QPoint(100, 100)
    end_point = QPoint(*worldview.world.size) * worldview.block_length - QPoint(10, 10)

    assert TILE_MUSHROOM_HOUSE_1 == worldview._visible_object_at(start_point).type
    assert 0x2 == worldview._visible_object_at(end_point).type

    drag_from_to(worldview, start_point, end_point)

    assert WORLD_MAP_BLANK_TILE_ID == worldview._visible_object_at(start_point).type
    assert TILE_MUSHROOM_HOUSE_1 == worldview._visible_object_at(end_point).type


def test_selecting_all_objects_via_selection_square(worldview, qtbot):
    foundry.ctrl_is_pressed = lambda: True

    start_point = QPoint(0, 0)
    end_point = QPoint(*worldview.world.size) * worldview.block_length

    assert not worldview.get_selected_objects()
    click_event = QMouseEvent(
        QMouseEvent.MouseButtonPress, start_point, Qt.LeftButton, Qt.LeftButton, Qt.ControlModifier
    )
    worldview.mousePressEvent(click_event)

    # move the mouse, while holding down
    move_event = QMouseEvent(QMouseEvent.MouseMove, end_point, Qt.NoButton, Qt.NoButton, Qt.ControlModifier)
    worldview.mouseMoveEvent(move_event)
    assert len(worldview.get_selected_objects()) == len(worldview.world.get_all_objects())

    move_event = QMouseEvent(QMouseEvent.MouseMove, start_point, Qt.NoButton, Qt.NoButton, Qt.ControlModifier)
    worldview.mouseMoveEvent(move_event)
    assert len(worldview.get_selected_objects()) == 1


def test_moving_all_objects_partly_off_screen(worldview):
    start_point = QPoint(0, 0)
    end_point = QPoint(worldview.world.size[0], 0) * worldview.block_length - QPoint(1, 0)

    assert worldview.world.point_in(*worldview._to_level_point(end_point)), (
        end_point,
        worldview._to_level_point(end_point),
    )

    worldview.select_all()
    assert len(worldview.get_selected_objects()) == len(worldview.world.get_all_objects())

    drag_from_to(worldview, start_point, end_point)

    for index, map_object in enumerate(worldview.world.get_all_objects()):
        if map_object.pos.x % WORLD_MAP_SCREEN_WIDTH == WORLD_MAP_SCREEN_WIDTH - 1:
            assert map_object.type != WORLD_MAP_BLANK_TILE_ID, index
        else:
            assert map_object.type == WORLD_MAP_BLANK_TILE_ID, index


def test_move_sprite(worldview):
    start_pos = QPoint(10, 6) * worldview.block_length
    end_pos = QPoint(0, 0) * worldview.block_length

    assert isinstance(worldview._visible_object_at(start_pos), Sprite)

    drag_from_to(worldview, start_pos, end_pos)

    assert not isinstance(worldview._visible_object_at(start_pos), Sprite)
    assert isinstance(worldview._visible_object_at(end_pos), Sprite)


def test_fill_tiles(worldview):
    tile_to_replace_with = 0x20

    worldview.on_put_tile(tile_to_replace_with)

    pos = QPoint(0, 0)

    tile_at_0_0 = worldview.object_at(pos)

    assert tile_at_0_0.type != tile_to_replace_with

    worldview.mousePressEvent(
        QMouseEvent(
            QMouseEvent.MouseButtonPress,
            pos,
            Qt.LeftButton,
            Qt.LeftButton,
            Qt.ShiftModifier,
        )
    )

    for index, map_object in enumerate(worldview.world.get_all_objects()):
        if map_object.pos.x % WORLD_MAP_SCREEN_WIDTH == 0:
            assert map_object.type == tile_to_replace_with, index
