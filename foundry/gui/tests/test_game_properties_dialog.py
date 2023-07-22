from foundry.gui.dialogs.GamePropertiesDialog import GamePropertiesDialog


def test_dialog(qtbot, main_window, rom):
    GamePropertiesDialog(main_window, rom)
