from foundry.game.gfx.objects.LevelObject import SCREEN_WIDTH
from foundry.gui.HeaderEditor import HeaderEditor


def test_level_length_change(main_window):
    # GIVEN a header editor and a level reference
    level = main_window.level_ref

    header_editor = HeaderEditor(None, level)

    # WHEN the level length has been changed using the header editor
    old_index = header_editor.length_dropdown.currentIndex()
    old_length = level.length

    new_index = old_index - 1

    assert new_index > 0

    header_editor.length_dropdown.setCurrentIndex(new_index)
    header_editor.length_dropdown.activated.emit(new_index)

    # THEN the level length should have changed
    assert level.length == old_length - SCREEN_WIDTH
