import pytest
from PySide2.QtWidgets import QComboBox, QCheckBox

from foundry.game.gfx.objects.LevelObject import SCREEN_WIDTH
from foundry.game.level.Level import Level
from foundry.gui.HeaderEditor import HeaderEditor


@pytest.fixture
def header_editor(main_window):
    level = main_window.level_ref

    return HeaderEditor(None, level)


def _test_dropdown(dropdown: QComboBox, level: Level, level_attr: str, expected_change, index_change=+1):
    # WHEN the combobox has been changed using the header editor
    old_index = dropdown.currentIndex()
    old_attr_value = getattr(level, level_attr)

    new_index = old_index + index_change

    assert new_index > 0

    dropdown.setCurrentIndex(new_index)
    dropdown.activated.emit(new_index)

    new_attr_value = getattr(level, level_attr)

    # THEN the level attribute should have changed
    assert new_attr_value == old_attr_value + expected_change


def _test_check_box(check_box: QCheckBox, level: Level, level_attr: str, expected_value):
    old_checked_status = check_box.isChecked()
    old_attr_value = getattr(level, level_attr)

    check_box.click()

    new_attr_value = getattr(level, level_attr)

    assert check_box.isChecked() != old_checked_status
    assert old_attr_value != new_attr_value
    assert new_attr_value == expected_value


@pytest.mark.parametrize(
    "dropdown, level_attr, expected_change",
    [
        ("length_dropdown", "length", +SCREEN_WIDTH),
        ("music_dropdown", "music_index", +1),
        ("time_dropdown", "time_index", +1),
        ("v_scroll_direction_dropdown", "scroll_type", +1),
        ("x_position_dropdown", "start_x_index", +1),
        ("action_dropdown", "start_action", +1),
        ("graphic_set_dropdown", "graphic_set", +1),
        ("next_area_object_set_dropdown", "next_area_object_set", +1),
    ],
)
def test_dropdown(header_editor, dropdown, level_attr, expected_change):
    _test_dropdown(getattr(header_editor, dropdown), header_editor.level, level_attr, expected_change)


def test_y_starting_point(header_editor):
    _test_dropdown(
        getattr(header_editor, "y_position_dropdown"), header_editor.level, "start_y_index", -1, index_change=-1
    )


@pytest.mark.parametrize(
    "check_box_name, level_attr, expected_value",
    [("pipe_ends_level_cb", "pipe_ends_level", True), ("level_is_vertical_cb", "is_vertical", True)],
)
def test_check_box(header_editor, check_box_name, level_attr, expected_value):
    _test_check_box(getattr(header_editor, check_box_name), header_editor.level, level_attr, expected_value)
