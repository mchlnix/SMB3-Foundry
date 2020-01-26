from PySide2.QtCore import QPoint
from PySide2.QtGui import Qt

from foundry.gui.ContextMenu import ContextMenu


def test_correct_menu_position(main_window, monkeypatch, qtbot):
    # don't actually open the context menu
    monkeypatch.setattr(ContextMenu, "popup", lambda *_: None)

    # GIVEN a main window

    # WHEN the level is scrolled to the end and a right click happens on the level_view
    main_window.scroll_panel.horizontalScrollBar().setValue(500)

    click_pos = QPoint(200, 200)
    qtbot.mouseClick(main_window.level_view, Qt.RightButton, pos=main_window.level_view.mapFromGlobal(click_pos))

    # THEN the context menu is opened next to the cursor
    assert main_window.level_view.context_menu.get_position() == click_pos.toTuple()
