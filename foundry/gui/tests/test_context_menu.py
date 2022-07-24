from PySide6.QtCore import QPoint
from PySide6.QtGui import Qt

from foundry.game.gfx.objects import LevelObject
from foundry.gui.ContextMenu import LevelContextMenu


def test_correct_menu_position(main_window, monkeypatch, qtbot):
    # don't actually open the context menu but save its position for later assert
    menu_popup_position = QPoint(0, 0)

    def popup_mock(_, pos):
        nonlocal menu_popup_position
        menu_popup_position = pos

    monkeypatch.setattr(LevelContextMenu, "popup", popup_mock)

    # GIVEN a main window and its context menu
    context_menu = main_window.context_menu
    level_view = main_window.level_view

    # WHEN the level is scrolled to the right and a right click happens on the level_view to add an object
    main_window.scroll_panel.horizontalScrollBar().setValue(500)

    click_pos = QPoint(200, 200)
    point_in_level_view = level_view.mapFromGlobal(click_pos)
    qtbot.mouseClick(level_view, Qt.RightButton, pos=point_in_level_view)

    context_menu.triggered.emit(context_menu.add_object_action)

    # THEN the context menu is opened next to the cursor
    added_object: LevelObject = main_window.level_ref.objects[-1]

    assert menu_popup_position == click_pos, "LevelContextMenu not opened on Cursor"
    assert (
        added_object.get_position() == level_view.to_level_point(point_in_level_view).xy
    ), "Object not added at cursor"
