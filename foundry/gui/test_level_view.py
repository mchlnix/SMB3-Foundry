import pytest

from foundry.gui.LevelView import LevelView
from smb3parse.objects.object_set import ENEMY_ITEM_OBJECT_SET, PLAINS_OBJECT_SET


@pytest.fixture
def level_view(main_window, qtbot):
    return main_window.level_view


@pytest.mark.parametrize(
    "coordinates, obj_index, domain, object_set_number",
    [
        ((0, 0), 0x03, 0x00, PLAINS_OBJECT_SET),  # background symbols
        ((361, 283), 0xE2, 0x00, PLAINS_OBJECT_SET),  # background cloud
        ((233, 409), 0x72, 0x00, ENEMY_ITEM_OBJECT_SET),  # goomba
    ],
)
def test_object_at(level_view: LevelView, qtbot, coordinates, obj_index, domain, object_set_number):
    screen_coordinates = coordinates  # in pixels

    level_object = level_view.object_at(*screen_coordinates)

    assert level_object
    assert level_object.obj_index == obj_index
    assert level_object.domain == domain
    assert level_object.object_set.number == object_set_number
