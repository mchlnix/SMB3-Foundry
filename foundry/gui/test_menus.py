def test_level_reload_action(main_window):
    # GIVEN the reload level action, that is visible from the menu and a level that was changed
    reload_action = main_window.reload_action

    menu_actions = main_window.menuBar().actions()

    # assert that the reload actions is present in the menu bar
    assert any(reload_action in menu_action.menu().actions() for menu_action in menu_actions)

    main_window.level_ref.level.changed = True

    assert main_window.level_ref.changed

    # WHEN the reload action is clicked/triggered
    reload_action.trigger()

    # THEN the level is not changed anymore
    assert not main_window.level_ref.changed
