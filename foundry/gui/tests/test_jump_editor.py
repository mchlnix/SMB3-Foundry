from foundry.gui.dialogs.JumpEditor import JumpEditor


def _check_jump_cb(jump_before):
    def check_against_jump_from_signal(jump_after):
        assert jump_after != jump_before
        assert jump_after.screen_index == jump_before.screen_index + 1
        assert jump_after.exit_action == jump_before.exit_action + 1
        assert jump_after.exit_horizontal == jump_before.exit_horizontal + 1
        assert jump_after.exit_vertical == jump_before.exit_vertical + 1

    return check_against_jump_from_signal


def test_on_ok(main_window):
    _jump_index = 0

    # GIVEN a jump to be edited and the JumpEditor
    jump_before = main_window.level_ref.level.jumps[_jump_index]

    jump_editor = JumpEditor(None, jump_before)

    # WHEN the properties changed and the ok button pressed
    jump_editor.screen_spinner.setValue(jump_before.screen_index + 1)
    jump_editor.exit_action.setCurrentIndex(jump_before.exit_action + 1),
    jump_editor.exit_horizontal.setValue(jump_before.exit_horizontal + 1)
    jump_editor.exit_vertical.setCurrentIndex(jump_before.exit_vertical + 1)

    jump_editor.ok_button.click()

    # THEN the resulting jump should be updated correctly
    assert jump_editor.jump != jump_before
    assert jump_editor.jump.screen_index == jump_before.screen_index + 1
    assert jump_editor.jump.exit_action == jump_before.exit_action + 1
    assert jump_editor.jump.exit_horizontal == jump_before.exit_horizontal + 1
    assert jump_editor.jump.exit_vertical == jump_before.exit_vertical + 1
