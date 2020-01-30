import pytest
from PySide2.QtCore import QPoint
from PySide2.QtGui import QWheelEvent, Qt

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


@pytest.mark.parametrize("scroll_amount", [0, 100])
@pytest.mark.parametrize(
    "coordinates", [(2, 2), (334, 265), (233, 409)]  # background symbols  # background cloud  # goomba
)
@pytest.mark.parametrize("wheel_delta, type_change", [(10, 1), (-10, -1)])  # scroll wheel up  # scroll wheel down
def test_wheel_event(scroll_amount, coordinates, wheel_delta, type_change, main_window, qtbot):
    # GIVEN a level view and a cursor position over an object
    x, y = coordinates

    level_view = main_window.level_view
    object_under_cursor = level_view.object_at(x, y)
    original_type = object_under_cursor.type

    # WHEN level view is scrolled horizontally, the object is selected and the scroll wheel is used on it
    main_window.scroll_panel.horizontalScrollBar().setMaximum(level_view.width())
    main_window.scroll_panel.horizontalScrollBar().setValue(scroll_amount)

    main_window.show()
    qtbot.wait_for_window_shown(main_window)

    main_window.hide()

    qtbot.mouseClick(level_view, Qt.LeftButton, pos=QPoint(x, y))
    assert object_under_cursor.selected

    event = QWheelEvent(
        QPoint(x, y),
        QPoint(-1, -1),
        QPoint(0, wheel_delta),
        QPoint(0, wheel_delta),
        Qt.LeftButton,
        Qt.NoModifier,
        Qt.ScrollEnd,
        False,
    )

    assert level_view.wheelEvent(event)

    # THEN the type of the object should have changed
    new_type = level_view.object_at(*coordinates).type

    assert new_type == original_type + type_change, (original_type, new_type)
