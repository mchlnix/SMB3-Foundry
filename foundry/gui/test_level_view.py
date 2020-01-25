import pytest

from foundry.gui.HeaderEditor import HeaderEditor
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


def test_level_larger(level_view):
    # GIVEN level_view and a header editor
    header_editor = HeaderEditor(None, level_view.level_ref)
    length_dropdown = header_editor.length_dropdown

    original_size = level_view.size()

    # WHEN the level is made larger using the header editor
    original_index = length_dropdown.currentIndex()

    length_dropdown.setCurrentIndex(original_index + 1)
    length_dropdown.activated.emit(length_dropdown.currentIndex())

    # THEN the level_view should be larger as well
    assert level_view.size().width() > original_size.width()
    assert level_view.size().height() >= original_size.height()


def test_level_smaller(level_view):
    header_editor = HeaderEditor(None, level_view.level_ref)
    length_dropdown = header_editor.length_dropdown

    original_size = level_view.size()

    # WHEN the level is made larger using the header editor
    original_index = length_dropdown.currentIndex()

    length_dropdown.setCurrentIndex(original_index - 1)
    length_dropdown.activated.emit(length_dropdown.currentIndex())

    # THEN the level_view should be larger as well
    assert level_view.size().width() < original_size.width()
    assert level_view.size().height() >= original_size.height()
