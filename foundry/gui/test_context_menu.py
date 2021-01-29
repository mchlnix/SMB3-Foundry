from PySide2.QtCore import QPoint
from PySide2.QtGui import Qt

from foundry.game.gfx.objects.LevelObj.ObjectLikeLevelObjectRendererAdapter import (
    ObjectLikeLevelObjectRendererAdapter as LevelObject,
)
from foundry.gui.ContextMenu import ContextMenu


def test_correct_menu_position(main_window, monkeypatch, qtbot):
    # don't actually open the context menu but save its position for later assert
    menu_popup_position = QPoint(0, 0)

    def popup_mock(_, pos):
        nonlocal menu_popup_position
        menu_popup_position = pos

    monkeypatch.setattr(ContextMenu, "popup", popup_mock)

    # GIVEN a main window and its context menu
    context_menu = main_window.context_menu
    level_view = main_window.level_view

    # show the main window, otherwise the scroll doesn't happen
    main_window.show()

    # WHEN the level is scrolled to the right and a right click happens on the level_view to add an object
    main_window.scroll_panel.horizontalScrollBar().setValue(500)

    click_pos = QPoint(200, 200)
    # make position positive so the level factory doesn't freak out
    qt_point_in_level_view = level_view.mapFromGlobal(click_pos)
    point_in_level_view = (abs(i) for i in qt_point_in_level_view.toTuple())
    qtbot.mouseClick(level_view, Qt.RightButton, pos=qt_point_in_level_view)

    context_menu.triggered.emit(context_menu.add_object_action)

    main_window.hide()

    # THEN the context menu is opened next to the cursor
    added_object: LevelObject = main_window.level_ref.objects[-1]

    assert menu_popup_position == click_pos, "ContextMenu not opened on Cursor"
    assert added_object.get_position() == level_view._to_level_point(*point_in_level_view), "Object not added at cursor"
