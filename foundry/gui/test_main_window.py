import pytest
from PySide2.QtCore import QPoint
from PySide2.QtGui import QWheelEvent, Qt

from smb3parse.objects.object_set import ENEMY_ITEM_OBJECT_SET, PLAINS_OBJECT_SET


def test_open(main_window):
    pass


@pytest.mark.parametrize(
    "coordinates, obj_index, domain, object_set_number",
    [
        ((0, 0), 0x03, 0x00, PLAINS_OBJECT_SET),  # background symbols
        ((334, 265), 0xE2, 0x00, PLAINS_OBJECT_SET),  # background cloud
        ((233, 409), 0x72, 0x00, ENEMY_ITEM_OBJECT_SET),  # goomba
    ],
)
@pytest.mark.parametrize("wheel_delta, type_change", [(10, 1), (-10, -1)])  # scroll wheel up  # scroll wheel down
def test_wheel_event(coordinates, obj_index, domain, object_set_number, wheel_delta, type_change, main_window, qtbot):
    level_object = main_window.level_view.object_at(*coordinates)

    original_type = level_object.type

    x, y = coordinates
    y += main_window.menuBar().height()

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

    assert not main_window.wheelEvent(event)

    level_object.selected = True

    assert main_window.wheelEvent(event)

    new_type = main_window.level_view.object_at(*coordinates).type

    assert new_type == original_type + type_change, (original_type, new_type)
