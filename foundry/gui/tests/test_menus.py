from pathlib import Path

from PySide6.QtWidgets import QFileDialog

from foundry.game.File import ROM

test_data_dir = Path(__file__).parent.parent.joinpath("test_data")
test_m3l_path = test_data_dir.joinpath("test.m3l")


def _action_is_in_menu_bar(main_window, action):
    menu_actions = main_window.menuBar().actions()

    # return if the reload action is present in the menu bar
    return any(action in menu_action.menu().actions() for menu_action in menu_actions)


def _mocked_open_file_name(*_, **__):
    return str(test_m3l_path), ""


def test_level_reload_action(main_window):
    # GIVEN the reload level action, that is visible from the menu and a level that was changed
    reload_action = main_window.reload_action

    assert _action_is_in_menu_bar(main_window, reload_action)

    main_window.level_ref.level.changed = True

    assert main_window.level_ref.level.changed

    # WHEN the reload action is clicked/triggered
    reload_action.trigger()

    # THEN the level is not changed anymore
    assert not main_window.level_ref.level.changed


def test_load_m3l(main_window, qtbot):
    QFileDialog.getOpenFileName = _mocked_open_file_name
    # GIVEN the load from m3l action, th<t is visible from the menu
    rom_data_before_load = ROM.rom_data.copy()

    open_m3l_action = main_window.open_m3l_action

    assert _action_is_in_menu_bar(main_window, open_m3l_action)

    # WHEN the action is triggered and a m3l file is selected
    open_m3l_action.trigger()

    # THEN the level ref contains the level from the m3l and they consist of the same bytes
    m3l_data = bytearray(open(test_m3l_path, "rb").read())

    # world and level number is not preserved
    m3l_data[0] = 1
    m3l_data[1] = 1

    assert not main_window.level_ref.level.attached_to_rom
    assert main_window.level_ref.level.to_m3l() == m3l_data

    # also the current rom was not overwritten with any data
    assert ROM.rom_data == rom_data_before_load
