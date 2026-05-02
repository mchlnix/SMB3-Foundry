from PySide6.QtCore import Qt

from foundry.gui.localization import install_language, tr, tr_object_name
from foundry.conftest import level_1_2_enemy_address, level_1_2_object_address
from smb3parse.constants import HILLY_OBJECT_SET


def test_object_update_on_level_change(main_window):
    # GIVEN the main window and the object dropdown
    object_dropdown = main_window.object_dropdown

    original_object_set = main_window.level_ref.object_set_number
    original_first_object = object_dropdown.itemText(0)

    # WHEN the level is changed
    main_window.update_level("Level 1-2", level_1_2_object_address, level_1_2_enemy_address, HILLY_OBJECT_SET)

    assert original_object_set != main_window.level_ref.object_set_number

    # THEN the objects in the dropdown should be changed
    new_first_object = object_dropdown.itemText(0)

    assert original_first_object != new_first_object, "Objects didn't change."


def test_dropdown_selects_equivalent_toolbar_object(main_window):
    dropdown_object = main_window.object_dropdown.itemData(0)
    toolbar_object = main_window.object_toolbar.tabbed_tool_box.get_equivalent(dropdown_object)

    assert toolbar_object is not None
    assert toolbar_object is not dropdown_object

    main_window.object_dropdown.select_object(toolbar_object)

    assert main_window.object_dropdown.currentData() == dropdown_object


def test_main_window_language_change_retranslates_visible_labels(main_window, qapp):
    install_language(qapp, "en")
    main_window.retranslate_ui()
    main_window.object_toolbar.select_object(main_window.object_dropdown.itemData(0))

    assert main_window.level_menu.title() == "&Level"
    assert main_window.spinner_panel.domain_label.text() == "Bank/Domain:"
    assert main_window.object_toolbar.tabbed_tool_box.tabText(1) == "Level Objects"
    english_object_list_labels = [
        main_window.object_list.item(index).text() for index in range(main_window.object_list.count())
    ]

    main_window._on_language_changed("it")

    try:
        assert main_window.level_menu.title() == "&Livello"
        assert tr("foundry.main", "menu.level") == "&Livello"
        assert main_window.spinner_panel.domain_label.text() == "Banco/dominio:"
        assert main_window.spinner_panel.type_label.text() == "Indice:"
        assert main_window.spinner_panel.length_label.text() == "Lunghezza:"
        assert main_window.object_toolbar.tabbed_tool_box.tabText(0) == "Recenti"
        assert main_window.object_toolbar.tabbed_tool_box.tabText(1) == tr("TabbedToolBox", "level_objects")
        assert main_window.object_toolbar.tabbed_tool_box.tabText(2) == "Nemici"
        assert main_window.object_dropdown.itemText(0) == tr_object_name(main_window.object_dropdown.itemData(0))
        assert main_window.object_toolbar.current_object_name.text() == tr_object_name(
            main_window.object_toolbar.current_object_icon.object
        )
        assert any(
            main_window.object_list.item(index).text() != english_object_list_labels[index]
            for index in range(main_window.object_list.count())
        )
        assert all(
            main_window.object_list.item(index).text()
            == tr_object_name(main_window.object_list.item(index).data(Qt.ItemDataRole.UserRole))
            for index in range(main_window.object_list.count())
        )
        assert main_window.level_size_bar.info_label.text().startswith("Oggetti:")
        assert main_window.enemy_size_bar.info_label.text().startswith("Nemici/oggetti:")
        assert main_window.jump_list.item(0).text().startswith("Salto nella schermata")

        main_window._on_language_changed("es")
        assert main_window.level_menu.title() == "&Nivel"
        assert tr("foundry.main", "menu.level") == "&Nivel"
    finally:
        main_window._on_language_changed("en")

    assert main_window.level_menu.title() == "&Level"
    assert tr("foundry.main", "menu.level") == "&Level"
