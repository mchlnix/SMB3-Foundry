from foundry.gui.dialogs.GamePropertiesDialog import GamePropertiesDialog, _PROP_PATH
from foundry.gui.localization import install_language


def _first_property_item(dialog: GamePropertiesDialog):
    """Expose the first editable game-property tree item for state checks.

    The helper reads the dialog's Qt item-to-ROM-property mapping without
    changing selection or spinner state so live-retranslation tests can compare
    the same metadata row across language changes.

    Parameters
    ----------
    dialog
        Game properties dialog whose rendered property tree is under test.

    Returns
    -------
    QTreeWidgetItem
        First property item tracked by the dialog's metadata mapping.
    """
    return next(iter(dialog._prop_item_to_data))


def test_dialog(qtbot, main_window, rom, qapp):
    install_language(qapp, "en")
    dialog = GamePropertiesDialog(main_window, rom)
    qtbot.addWidget(dialog)


def test_game_properties_dialog_translates_metadata_labels(qtbot, main_window, rom, qapp):
    install_language(qapp, "it")

    try:
        dialog = GamePropertiesDialog(main_window, rom)
        qtbot.addWidget(dialog)

        first_section = dialog._prop_tree.topLevelItem(0)
        first_property = first_section.child(0)
        info_widget = dialog._prop_info_widgets[first_property]

        assert dialog.windowTitle() == "Proprietà del gioco"
        assert first_section.text(0) == "Nemici"
        assert first_property.text(0) == "Velocità predefinita verso sinistra di molti nemici"
        assert info_widget._info_label.text() == "Velocità verso sinistra di molti nemici"
        assert info_widget._value_label.text() == "Valore:"
        assert info_widget._rom_address_label.text().startswith("Indirizzo ROM:")
    finally:
        install_language(qapp, "en")


def test_game_properties_dialog_live_retranslation_preserves_selection_and_value(qtbot, main_window, rom, qapp):
    install_language(qapp, "en")
    dialog = GamePropertiesDialog(main_window, rom)
    qtbot.addWidget(dialog)

    first_property = _first_property_item(dialog)
    dialog._prop_tree.setCurrentItem(first_property)
    info_widget = dialog._prop_info_widgets[first_property]
    selected_item = dialog._prop_tree.currentItem()
    spinner_value = info_widget._spinner.value()

    assert first_property.text(0) == "Default - Left speed of many enemies"
    assert info_widget._info_label.text() == "Left speed of many enemies"

    install_language(qapp, "it")
    dialog.retranslate_ui()

    assert dialog._prop_tree.currentItem() is selected_item
    assert info_widget._spinner.value() == spinner_value
    assert first_property.text(0) == "Velocità predefinita verso sinistra di molti nemici"
    assert info_widget._info_label.text() == "Velocità verso sinistra di molti nemici"
    assert info_widget._value_label.text() == "Valore:"

    install_language(qapp, "es")
    dialog.retranslate_ui()

    assert dialog._prop_tree.currentItem() is selected_item
    assert info_widget._spinner.value() == spinner_value
    assert first_property.text(0) == "Predeterminado - Velocidad izquierda de muchos enemigos"
    assert info_widget._info_label.text() == "Velocidad hacia la izquierda de muchos enemigos"
    assert info_widget._value_label.text() == "Valor:"

    install_language(qapp, "en")
    dialog.retranslate_ui()

    assert dialog._prop_tree.currentItem() is selected_item
    assert info_widget._spinner.value() == spinner_value
    assert first_property.text(0) == "Default - Left speed of many enemies"
    assert info_widget._info_label.text() == "Left speed of many enemies"
    assert info_widget._value_label.text() == "Value:"


def test_game_properties_ini_remains_english_source_data():
    assert "caption Default - Left speed of many enemies" in _PROP_PATH.read_text(encoding="utf-8")
