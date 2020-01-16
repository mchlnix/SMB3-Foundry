from foundry.game.gfx.objects.Jump import Jump


def test_add_jump(main_window):
    # GIVEN the jump list inside the main window
    jump_list = main_window.jump_list

    jumps_before = len(main_window.level_ref.jumps)

    assert jumps_before == jump_list.count() == 1

    # WHEN a jump is added through the context menu
    jump_list.add_jump.emit()

    # THEN there is one more jump in the level and it is displayed in the jump list
    jumps_after = len(main_window.level_ref.jumps)
    assert jumps_after == jumps_before + 1
    assert jumps_after == jump_list.count()


def test_edit_jump(main_window):
    _jump_index = 0
    jump_list = main_window.jump_list

    # GIVEN the jump list with a selected jump and its textual representation
    jump_before = main_window.level_ref.jumps[_jump_index]

    # manually select jump in list
    jump_list.setCurrentRow(_jump_index)
    list_index = jump_list.currentIndex()

    jump_list_item_text_before = jump_list.currentItem().text()

    # WHEN a jump is edited and the callback of MainWindow is called
    updated_jump = Jump.from_properties(
        jump_before.screen_index + 1,
        jump_before.exit_action + 1,
        jump_before.exit_horizontal + 1,
        jump_before.exit_vertical + 1,
    )

    main_window.on_jump_edited(updated_jump)

    # THEN the jump in the level and the text in the jump list should be updated
    # reselect jump in list
    jump_list.setCurrentIndex(list_index)

    jump_after = main_window.level_ref.jumps[_jump_index]

    jump_list_item_text_after = jump_list.currentItem().text()

    assert jump_before != jump_after
    assert jump_after == updated_jump
    assert jump_list_item_text_before != jump_list_item_text_after
