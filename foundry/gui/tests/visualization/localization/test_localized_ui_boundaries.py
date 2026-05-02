import importlib
from types import SimpleNamespace

from PySide6.QtGui import QUndoStack
from PySide6.QtWidgets import QRadioButton, QWidget

from foundry.game.File import ROM
from foundry.game.gfx.objects.in_level.jump import Jump
from foundry.gui.dialogs.AutoSaveDialog import AutoSaveDialog
from foundry.gui.dialogs.JumpEditor import JumpAction, JumpEditor, JumpVerticalPosition
from foundry.gui.dialogs.LevelHeaderEditor import HeaderMusic, HeaderStartAction, LevelHeaderEditor
from foundry.gui.dialogs.ObjectSetSelector import ObjectSetSelector
from foundry.gui.dialogs.SettingsDialog import SettingsDialog as FoundrySettingsDialog
from foundry.gui.dialogs.level_selector.LevelSelector import LevelSelector
from foundry.gui.dialogs.level_selector.stock_level_list import StockLevelWidget
from foundry.gui.dialogs.new_level_dialog import NewLevelDialog
from foundry.gui.JumpList import JumpList, jump_display_text
from foundry.gui.localization import install_language, tr, tr_data_name
from foundry.gui.ObjectStatusBar import ObjectStatusBar
from foundry.gui.tests.visualization.localization.helpers import catalog_value, visible_widget_texts
from foundry.gui.tests.visualization.localization.stubs import (
    CounterLevelRef,
    EnemyItem,
    FakeScribeTool,
    FakeWorldMapLevelSelect,
    HeaderLevelRef,
    StatusLevelObject,
    StatusLevelRef,
)
from foundry.gui.widgets.size_bar.EnemySizeBar import EnemySizeBar
from foundry.gui.widgets.size_bar.LevelSizeBar import LevelSizeBar
from scribe.gui.settings_dialog import SettingsDialog as ScribeSettingsDialog
from scribe.gui.world_overview import WorldOverview


def test_auto_save_dialog_retranslates_recovery_prompt(qtbot, qapp):
    install_language(qapp, "en")
    dialog = AutoSaveDialog()
    qtbot.addWidget(dialog)
    discard_button = dialog.discard_rom_button
    load_button = dialog.use_auto_save_button

    assert dialog.windowTitle() == catalog_value("en", "foundry.startup", "autosave.restore.title")
    assert dialog.text() == catalog_value("en", "foundry.startup", "autosave.restore.prompt")
    assert discard_button.text() == catalog_value("en", "foundry.startup", "autosave.restore.discard")
    assert load_button.text() == catalog_value("en", "foundry.startup", "autosave.restore.load")

    install_language(qapp, "it")
    dialog.retranslate_ui()

    assert dialog.windowTitle() == catalog_value("it", "foundry.startup", "autosave.restore.title")
    assert dialog.text() == catalog_value("it", "foundry.startup", "autosave.restore.prompt")
    assert discard_button.text() == catalog_value("it", "foundry.startup", "autosave.restore.discard")
    assert load_button.text() == catalog_value("it", "foundry.startup", "autosave.restore.load")
    assert dialog.discard_rom_button is discard_button
    assert dialog.use_auto_save_button is load_button

    install_language(qapp, "es")
    dialog.retranslate_ui()

    assert dialog.windowTitle() == catalog_value("es", "foundry.startup", "autosave.restore.title")
    assert dialog.text() == catalog_value("es", "foundry.startup", "autosave.restore.prompt")
    assert discard_button.text() == catalog_value("es", "foundry.startup", "autosave.restore.discard")
    assert load_button.text() == catalog_value("es", "foundry.startup", "autosave.restore.load")
    assert dialog.discard_rom_button is discard_button
    assert dialog.use_auto_save_button is load_button

    install_language(qapp, "en")
    dialog.retranslate_ui()

    assert dialog.windowTitle() == catalog_value("en", "foundry.startup", "autosave.restore.title")
    assert dialog.text() == catalog_value("en", "foundry.startup", "autosave.restore.prompt")
    assert discard_button.text() == catalog_value("en", "foundry.startup", "autosave.restore.discard")
    assert load_button.text() == catalog_value("en", "foundry.startup", "autosave.restore.load")


def test_object_set_selector_translates_display_without_changing_ids(qtbot, qapp):
    assert install_language(qapp, "es")

    try:
        dialog = ObjectSetSelector()
        qtbot.addWidget(dialog)

        assert dialog.object_set_dropdown.itemText(0) == catalog_value("es", "Common", "object_set.0x1_plains")
        assert dialog.object_set_dropdown.itemData(0) == 1

        install_language(qapp, "it")
        italian_dialog = ObjectSetSelector()
        qtbot.addWidget(italian_dialog)

        assert italian_dialog.object_set_dropdown.itemText(0) == catalog_value("it", "Common", "object_set.0x1_plains")
        assert italian_dialog.object_set_dropdown.itemData(0) == 1
    finally:
        install_language(qapp, "en")


def test_new_level_dialog_translates_display_without_changing_ids(qtbot, qapp):
    assert install_language(qapp, "es")

    try:
        parent = QWidget()
        qtbot.addWidget(parent)
        dialog = NewLevelDialog(parent)
        qtbot.addWidget(dialog)

        assert dialog.object_set_dropdown.itemText(0) == catalog_value("es", "Common", "object_set.0x1_plains")
        assert dialog.object_set_dropdown.itemData(0) == 1

        install_language(qapp, "it")
        italian_dialog = NewLevelDialog(parent)
        qtbot.addWidget(italian_dialog)

        assert italian_dialog.object_set_dropdown.itemText(0) == catalog_value("it", "Common", "object_set.0x1_plains")
        assert italian_dialog.object_set_dropdown.itemData(0) == 1

        last_index = italian_dialog.object_set_dropdown.count() - 1
        italian_dialog.object_set_dropdown.setCurrentIndex(last_index)

        assert italian_dialog.object_set_index == italian_dialog.object_set_dropdown.itemData(last_index)
    finally:
        install_language(qapp, "en")


def test_stock_level_selector_translates_dat_labels_without_changing_selection(monkeypatch, qtbot, qapp):
    assert install_language(qapp, "es")
    monkeypatch.setattr(ROM, "additional_data", SimpleNamespace(found_levels=[]), raising=False)

    try:
        widget = StockLevelWidget()
        qtbot.addWidget(widget)

        assert widget.level_list.item(0).text() == tr_data_name("StockLevel", "Level 1")
        assert widget.level_name
        assert widget.level_address
        assert widget.object_set_number

        widget.level_list.setCurrentRow(1)
        level_address = widget.level_address
        object_set_number = widget.object_set_number

        install_language(qapp, "it")
        widget.retranslate_ui()

        assert widget.level_list.item(0).text() == tr_data_name("StockLevel", "Level 1")
        assert widget.level_name
        assert widget.level_address == level_address
        assert widget.object_set_number == object_set_number
    finally:
        install_language(qapp, "en")


def test_level_selector_uses_active_language_without_changing_object_set_ids(monkeypatch, qtbot, qapp):
    assert install_language(qapp, "es")
    level_selector_module = importlib.import_module("foundry.gui.dialogs.level_selector.LevelSelector")
    monkeypatch.setattr(ROM, "additional_data", SimpleNamespace(found_levels=[]), raising=False)
    monkeypatch.setattr(level_selector_module, "WorldMapLevelSelect", FakeWorldMapLevelSelect)
    monkeypatch.setattr(level_selector_module, "_should_use_vertical_preview", lambda _layout_address: False)
    monkeypatch.setattr(level_selector_module._LevelPreviewWidget, "set_level_preview", lambda *_args: None)

    try:
        selector = LevelSelector(None)
        qtbot.addWidget(selector)

        assert selector.windowTitle() == catalog_value("es", "LevelSelector", "level_selector")
        assert selector.object_set_label.text() == catalog_value("es", "LevelSelector", "object_set")
        assert selector.object_set_dropdown.itemText(0) == catalog_value("es", "Common", "object_set.0x0_overworld")
        selector.object_set_dropdown.setCurrentIndex(1)

        install_language(qapp, "it")
        selector.retranslate_ui()

        assert selector.windowTitle() == catalog_value("it", "LevelSelector", "level_selector")
        assert selector.object_set_label.text() == tr("LevelSelector", "object_set", "Object Set")
        assert selector.object_set_dropdown.itemText(0) == catalog_value("it", "Common", "object_set.0x0_overworld")
        assert selector.object_set_dropdown.currentIndex() == 1
    finally:
        install_language(qapp, "en")


def test_level_header_editor_uses_active_language_without_changing_encoded_values(qtbot, qapp):
    assert install_language(qapp, "es")
    parent = QWidget()
    undo_stack = QUndoStack(parent)
    undo_stack.setObjectName("undo_stack")
    qtbot.addWidget(parent)

    try:
        level_ref = HeaderLevelRef()
        dialog = LevelHeaderEditor(parent, level_ref)
        qtbot.addWidget(dialog)

        assert dialog.windowTitle() == catalog_value("es", "LevelHeaderEditor", "level_header_editor")
        assert dialog.tab_widget.tabText(0) == catalog_value("es", "LevelHeaderEditor", "level")
        assert dialog.music_dropdown.itemText(0) == catalog_value(
            "es", "foundry.level_header_editor", "headermusic.plain_level"
        )
        assert dialog.music_dropdown.itemData(0) == int(HeaderMusic.PLAIN_LEVEL)
        assert dialog.action_dropdown.itemText(0) == catalog_value(
            "es", "foundry.level_header_editor", "headerstartaction.none"
        )
        assert dialog.action_dropdown.itemData(0) == int(HeaderStartAction.NONE)
        assert dialog.next_area_object_set_dropdown.itemText(0) == catalog_value(
            "es", "Common", "object_set.0x0_overworld"
        )
        assert dialog.next_area_object_set_dropdown.currentIndex() == level_ref.next_area_object_set_no
        dialog.music_dropdown.setCurrentIndex(1)
        dialog.next_area_object_set_dropdown.setCurrentIndex(1)

        install_language(qapp, "it")
        dialog.retranslate_ui()

        assert dialog.windowTitle() == tr("LevelHeaderEditor", "level_header_editor", "Level Header Editor")
        assert dialog.tab_widget.tabText(0) == tr("LevelHeaderEditor", "level", "Level")
        assert dialog.music_dropdown.itemText(0) == tr("foundry.level_header_editor", "headermusic.plain_level")
        assert dialog.music_dropdown.itemData(0) == int(HeaderMusic.PLAIN_LEVEL)
        assert dialog.music_dropdown.currentData() == int(HeaderMusic.UNDERGROUND)
        assert dialog.action_dropdown.itemText(0) == tr("foundry.level_header_editor", "headerstartaction.none")
        assert dialog.action_dropdown.itemData(0) == int(HeaderStartAction.NONE)
        assert dialog.next_area_object_set_dropdown.itemText(0) == catalog_value(
            "it", "Common", "object_set.0x0_overworld"
        )
        assert dialog.next_area_object_set_dropdown.currentIndex() == 1
    finally:
        install_language(qapp, "en")


def test_foundry_settings_dialog_persists_language_choice(qtbot, settings_factory):
    parent = QWidget()
    qtbot.addWidget(parent)
    settings = settings_factory("foundry-language-dialog")
    dialog = FoundrySettingsDialog(settings, parent)
    qtbot.addWidget(dialog)

    dialog.language_dropdown.setCurrentIndex(dialog.language_dropdown.findData("it"))

    assert settings.value("editor/language") == "it"


def test_scribe_settings_dialog_persists_language_choice(qtbot, settings_factory):
    settings = settings_factory("scribe-language-dialog")
    dialog = ScribeSettingsDialog(settings)
    qtbot.addWidget(dialog)

    dialog.language_dropdown.setCurrentIndex(dialog.language_dropdown.findData("it"))

    assert settings.value("editor/language") == "it"


def test_open_settings_dialog_retranslates_language_names(qtbot, settings_factory, qapp):
    install_language(qapp, "en")
    parent = QWidget()
    qtbot.addWidget(parent)
    settings = settings_factory("foundry-language-dialog-live")
    dialog = FoundrySettingsDialog(settings, parent)
    qtbot.addWidget(dialog)
    dialog.show()

    spanish_index = dialog.language_dropdown.findData("es")
    spanish_spain_index = dialog.language_dropdown.findData("es_ES")
    spanish_latin_america_index = dialog.language_dropdown.findData("es_419")
    italian_index = dialog.language_dropdown.findData("it")
    german_index = dialog.language_dropdown.findData("de")
    french_index = dialog.language_dropdown.findData("fr")
    pt_br_index = dialog.language_dropdown.findData("pt_BR")
    pt_pt_index = dialog.language_dropdown.findData("pt_PT")
    desktop_index = dialog.path_dropdown.findData("Desktop")
    custom_index = dialog.path_dropdown.findData("Custom")
    language_items = {
        spanish_index: "spanish",
        spanish_spain_index: "spanish_spain",
        spanish_latin_america_index: "spanish_latin_america",
        italian_index: "italian",
        german_index: "german",
        french_index: "french",
        pt_br_index: "portuguese_brazil",
        pt_pt_index: "portuguese_portugal",
    }

    for index, key in language_items.items():
        assert dialog.language_dropdown.itemText(index) == catalog_value("en", "lang", key)
    assert dialog.path_dropdown.itemText(desktop_index) == catalog_value(
        "en", "foundry.settings", "default_dir.desktop"
    )
    assert dialog.path_dropdown.itemData(custom_index) == "Custom"

    install_language(qapp, "es")
    dialog.retranslate_ui()
    for index, key in language_items.items():
        assert dialog.language_dropdown.itemText(index) == catalog_value("es", "lang", key)
    assert dialog.path_dropdown.itemText(desktop_index) == catalog_value(
        "es", "foundry.settings", "default_dir.desktop"
    )
    assert dialog.path_dropdown.itemData(custom_index) == "Custom"

    install_language(qapp, "it")
    dialog.retranslate_ui()
    for index, key in language_items.items():
        assert dialog.language_dropdown.itemText(index) == catalog_value("it", "lang", key)
    assert dialog.path_dropdown.itemText(desktop_index) == catalog_value(
        "it", "foundry.settings", "default_dir.desktop"
    )
    assert dialog.path_dropdown.itemData(custom_index) == "Custom"

    install_language(qapp, "de")
    dialog.retranslate_ui()
    assert dialog.language_dropdown.itemText(german_index) == catalog_value("de", "lang", "german")

    install_language(qapp, "fr")
    dialog.retranslate_ui()
    assert dialog.language_dropdown.itemText(french_index) == catalog_value("fr", "lang", "french")

    install_language(qapp, "pt_BR")
    dialog.retranslate_ui()
    assert dialog.language_dropdown.itemText(pt_br_index) == catalog_value("pt_BR", "lang", "portuguese_brazil")

    install_language(qapp, "pt_PT")
    dialog.retranslate_ui()
    assert dialog.language_dropdown.itemText(pt_pt_index) == catalog_value("pt_PT", "lang", "portuguese_portugal")

    install_language(qapp, "en")
    dialog.retranslate_ui()
    for index, key in language_items.items():
        assert dialog.language_dropdown.itemText(index) == catalog_value("en", "lang", key)
    assert dialog.path_dropdown.itemText(desktop_index) == catalog_value(
        "en", "foundry.settings", "default_dir.desktop"
    )
    assert dialog.path_dropdown.itemData(custom_index) == "Custom"


def test_scribe_settings_default_dir_selection_retranslates_without_changing_path(qtbot, settings_factory, qapp):
    install_language(qapp, "en")
    settings = settings_factory("scribe-default-dir-live")
    settings.setValue("editor/default_dir", "Desktop")
    dialog = ScribeSettingsDialog(settings)
    qtbot.addWidget(dialog)
    dialog.show()

    desktop_index = dialog.path_dropdown.findData("Desktop")
    assert dialog.path_dropdown.currentData() == "Desktop"
    assert dialog.windowTitle() == catalog_value("en", "ScribeSettingsDialog", "settings")
    assert dialog.online_box.title() == catalog_value("en", "ScribeSettingsDialog", "online")
    assert dialog.default_path_label.text() == catalog_value("en", "ScribeSettingsDialog", "default_path")
    assert dialog.language_label.text() == catalog_value("en", "ScribeSettingsDialog", "language")
    assert dialog.path_dropdown.itemText(desktop_index) == catalog_value(
        "en", "foundry.settings", "default_dir.desktop"
    )
    original_path = dialog.default_dir_label.text()

    install_language(qapp, "es")
    dialog.retranslate_ui()
    assert dialog.path_dropdown.currentData() == "Desktop"
    assert dialog.windowTitle() == catalog_value("es", "ScribeSettingsDialog", "settings")
    assert dialog.online_box.title() == catalog_value("es", "ScribeSettingsDialog", "online")
    assert dialog.default_path_label.text() == catalog_value("es", "ScribeSettingsDialog", "default_path")
    assert dialog.language_label.text() == catalog_value("es", "ScribeSettingsDialog", "language")
    assert dialog.path_dropdown.itemText(desktop_index) == catalog_value(
        "es", "foundry.settings", "default_dir.desktop"
    )
    assert dialog.default_dir_label.text() == original_path

    install_language(qapp, "it")
    dialog.retranslate_ui()
    assert dialog.path_dropdown.currentData() == "Desktop"
    assert dialog.windowTitle() == catalog_value("it", "ScribeSettingsDialog", "settings")
    assert dialog.online_box.title() == catalog_value("it", "ScribeSettingsDialog", "online")
    assert dialog.default_path_label.text() == catalog_value("it", "ScribeSettingsDialog", "default_path")
    assert dialog.language_label.text() == catalog_value("it", "ScribeSettingsDialog", "language")
    assert dialog.path_dropdown.itemText(desktop_index) == catalog_value(
        "it", "foundry.settings", "default_dir.desktop"
    )
    assert dialog.default_dir_label.text() == original_path

    install_language(qapp, "en")


def test_visible_text_collector_catches_foundry_settings_live_language_changes(qtbot, settings_factory, qapp):
    install_language(qapp, "en")
    parent = QWidget()
    qtbot.addWidget(parent)
    settings = settings_factory("foundry-visible-settings-live")
    dialog = FoundrySettingsDialog(settings, parent)
    qtbot.addWidget(dialog)

    english_texts = visible_widget_texts(dialog)
    assert catalog_value("en", "SettingsDialog", "language") in english_texts
    assert catalog_value("en", "SettingsDialog", "start_up") in english_texts

    install_language(qapp, "it")
    dialog.retranslate_ui()
    italian_texts = visible_widget_texts(dialog)
    assert catalog_value("it", "SettingsDialog", "language") in italian_texts
    assert catalog_value("it", "SettingsDialog", "start_up") in italian_texts
    assert catalog_value("it", "foundry.settings", "style.retro") in italian_texts
    assert catalog_value("en", "SettingsDialog", "language") not in italian_texts
    assert catalog_value("en", "SettingsDialog", "start_up") not in italian_texts
    assert catalog_value("en", "foundry.settings", "style.retro") not in italian_texts
    assert {
        button.property("gui_style_key")
        for button in dialog.gui_box.findChildren(QRadioButton)
        if button.property("gui_style_key") is not None
    } == {"RETRO", "DRACULA"}

    install_language(qapp, "es")
    dialog.retranslate_ui()
    spanish_texts = visible_widget_texts(dialog)
    assert catalog_value("es", "SettingsDialog", "language") in spanish_texts
    assert catalog_value("es", "SettingsDialog", "start_up") in spanish_texts
    assert catalog_value("it", "SettingsDialog", "language") not in spanish_texts

    install_language(qapp, "en")


def test_visible_text_collector_catches_scribe_settings_live_language_changes(qtbot, settings_factory, qapp):
    install_language(qapp, "en")
    settings = settings_factory("scribe-visible-settings-live")
    dialog = ScribeSettingsDialog(settings)
    qtbot.addWidget(dialog)

    english_texts = visible_widget_texts(dialog)
    assert catalog_value("en", "SettingsDialog", "language") in english_texts
    assert catalog_value("en", "ScribeSettingsDialog", "settings") in english_texts

    install_language(qapp, "it")
    dialog.retranslate_ui()
    italian_texts = visible_widget_texts(dialog)
    assert catalog_value("it", "SettingsDialog", "language") in italian_texts
    assert catalog_value("it", "ScribeSettingsDialog", "settings") in italian_texts
    assert catalog_value("en", "SettingsDialog", "language") not in italian_texts

    install_language(qapp, "es")
    dialog.retranslate_ui()
    spanish_texts = visible_widget_texts(dialog)
    assert catalog_value("es", "SettingsDialog", "language") in spanish_texts
    assert catalog_value("es", "ScribeSettingsDialog", "settings") in spanish_texts
    assert catalog_value("it", "SettingsDialog", "language") not in spanish_texts

    install_language(qapp, "en")


def test_size_bar_counters_translate_and_retranslate(monkeypatch, qtbot, qapp):
    level_size_bar_module = importlib.import_module("foundry.gui.widgets.size_bar.LevelSizeBar")
    enemy_size_bar_module = importlib.import_module("foundry.gui.widgets.size_bar.EnemySizeBar")
    fake_rom = SimpleNamespace(additional_data=SimpleNamespace(managed_level_positions=False))
    monkeypatch.setattr(level_size_bar_module, "ROM", lambda: fake_rom)
    monkeypatch.setattr(enemy_size_bar_module, "ROM", lambda: fake_rom)

    level_ref = CounterLevelRef()
    level_size_bar = LevelSizeBar(None, level_ref)
    enemy_size_bar = EnemySizeBar(None, level_ref)
    qtbot.addWidget(level_size_bar)
    qtbot.addWidget(enemy_size_bar)

    install_language(qapp, "es")
    level_size_bar.retranslate_ui()
    enemy_size_bar.retranslate_ui()

    assert level_size_bar.info_label.text() == catalog_value("es", "foundry.size_bar", "summary.bytes").format(
        description=catalog_value("es", "foundry.size_bar", "objects"), current=7, maximum=20
    )
    assert enemy_size_bar.info_label.text() == catalog_value("es", "foundry.size_bar", "summary.bytes").format(
        description=catalog_value("es", "foundry.size_bar", "enemies_items"), current=5, maximum=12
    )

    install_language(qapp, "it")
    level_size_bar.retranslate_ui()
    enemy_size_bar.retranslate_ui()

    assert level_size_bar.info_label.text() == catalog_value("it", "foundry.size_bar", "summary.bytes").format(
        description=catalog_value("it", "foundry.size_bar", "objects"), current=7, maximum=20
    )
    assert enemy_size_bar.info_label.text() == catalog_value("it", "foundry.size_bar", "summary.bytes").format(
        description=catalog_value("it", "foundry.size_bar", "enemies_items"), current=5, maximum=12
    )

    install_language(qapp, "en")
    level_size_bar.retranslate_ui()
    enemy_size_bar.retranslate_ui()

    assert level_size_bar.info_label.text() == catalog_value("en", "foundry.size_bar", "summary.bytes").format(
        description=catalog_value("en", "foundry.size_bar", "objects"), current=7, maximum=20
    )
    assert enemy_size_bar.info_label.text() == catalog_value("en", "foundry.size_bar", "summary.bytes").format(
        description=catalog_value("en", "foundry.size_bar", "enemies_items"), current=5, maximum=12
    )


def test_jump_list_rows_translate_without_changing_jump_identity(qtbot, qapp):
    level_ref = CounterLevelRef()
    jump = level_ref.jumps[0]
    jump_list = JumpList(None, level_ref)
    qtbot.addWidget(jump_list)

    assert str(jump) == catalog_value("en", "foundry.jump_list", "row.screen").format(screen_index=3)

    install_language(qapp, "es")
    jump_list.retranslate_ui()

    assert jump_display_text(jump) == tr("foundry.jump_list", "row.screen", "Jump on screen #{screen_index}").format(
        screen_index=3
    )
    assert jump_list.item(0).text() == tr("foundry.jump_list", "row.screen", "Jump on screen #{screen_index}").format(
        screen_index=3
    )
    assert jump.to_bytes() == bytearray([0xE3, 0x00, 0x00])

    install_language(qapp, "it")
    jump_list.retranslate_ui()

    assert jump_display_text(jump) == tr("foundry.jump_list", "row.screen", "Jump on screen #{screen_index}").format(
        screen_index=3
    )
    assert jump_list.item(0).text() == tr("foundry.jump_list", "row.screen", "Jump on screen #{screen_index}").format(
        screen_index=3
    )
    assert jump.to_bytes() == bytearray([0xE3, 0x00, 0x00])

    install_language(qapp, "en")
    jump_list.retranslate_ui()

    assert jump_list.item(0).text() == tr("foundry.jump_list", "row.screen", "Jump on screen #{screen_index}").format(
        screen_index=3
    )
    assert str(jump) == catalog_value("en", "foundry.jump_list", "row.screen").format(screen_index=3)


def test_jump_editor_retranslates_open_dialog_without_changing_encoded_values(qtbot, qapp):
    jump = Jump.from_properties(3, int(JumpAction.RIGHT_PIPE), 9, int(JumpVerticalPosition.VERTICAL_12))
    dialog = JumpEditor(None, jump)
    qtbot.addWidget(dialog)

    assert dialog.exit_action.currentData() == int(JumpAction.RIGHT_PIPE)
    assert dialog.exit_vertical.currentData() == int(JumpVerticalPosition.VERTICAL_12)
    assert catalog_value("en", "foundry.jump_editor", "label.exit_action") in visible_widget_texts(dialog)

    install_language(qapp, "it")
    dialog.retranslate_ui()
    italian_texts = visible_widget_texts(dialog)

    assert catalog_value("it", "foundry.jump_editor", "label.exit_action") in italian_texts
    assert catalog_value("it", "foundry.jump_editor", "jumpaction.right_pipe") in italian_texts
    assert catalog_value("en", "foundry.jump_editor", "label.exit_action") not in italian_texts
    assert dialog.exit_action.currentData() == int(JumpAction.RIGHT_PIPE)
    assert dialog.exit_vertical.currentData() == int(JumpVerticalPosition.VERTICAL_12)

    install_language(qapp, "es")
    dialog.retranslate_ui()
    spanish_texts = visible_widget_texts(dialog)

    assert catalog_value("es", "foundry.jump_editor", "label.exit_action") in spanish_texts
    assert catalog_value("es", "foundry.jump_editor", "jumpaction.right_pipe") in spanish_texts
    assert catalog_value("it", "foundry.jump_editor", "label.exit_action") not in spanish_texts
    assert dialog.exit_action.currentData() == int(JumpAction.RIGHT_PIPE)

    install_language(qapp, "en")
    dialog.retranslate_ui()

    assert catalog_value("en", "foundry.jump_editor", "label.exit_action") in visible_widget_texts(dialog)
    assert dialog.exit_action.currentData() == int(JumpAction.RIGHT_PIPE)


def test_object_status_bar_translates_level_object_footer(qtbot, qapp):
    level_object = StatusLevelObject()
    level_ref = StatusLevelRef(level_object)
    parent = QWidget()
    qtbot.addWidget(parent)
    status_bar = ObjectStatusBar(parent, level_ref)
    qtbot.addWidget(status_bar)

    install_language(qapp, "it")
    status_bar.update()

    assert f"{tr('foundry.object_status', 'field.width')}: 3" in status_bar.currentMessage()
    assert f"{tr('foundry.object_status', 'field.height')}: 2" in status_bar.currentMessage()
    assert level_object.get_status_info()[0] == ("Width", 3)

    install_language(qapp, "es")
    status_bar.retranslate_ui()

    assert f"{tr('foundry.object_status', 'field.width')}: 3" in status_bar.currentMessage()
    assert f"{tr('foundry.object_status', 'field.height')}: 2" in status_bar.currentMessage()

    install_language(qapp, "en")
    status_bar.retranslate_ui()

    assert f"{tr('foundry.object_status', 'field.width')}: 3" in status_bar.currentMessage()
    assert level_ref.selected_objects[0] is level_object


def test_object_status_bar_translates_enemy_name_footer(qtbot, qapp):
    enemy = EnemyItem()
    level_ref = StatusLevelRef(enemy)
    parent = QWidget()
    qtbot.addWidget(parent)
    status_bar = ObjectStatusBar(parent, level_ref)
    qtbot.addWidget(status_bar)

    install_language(qapp, "it")
    status_bar.update()

    assert (
        f"{tr('foundry.object_status', 'field.name')}: {tr_data_name('EnemyItem', 'Still Bullet Bill')}"
        in status_bar.currentMessage()
    )
    assert f"{tr('foundry.object_status', 'field.x')}: 4" in status_bar.currentMessage()

    install_language(qapp, "en")
    status_bar.retranslate_ui()

    assert (
        f"{tr('foundry.object_status', 'field.name')}: {tr_data_name('EnemyItem', 'Still Bullet Bill')}"
        in status_bar.currentMessage()
    )
    assert enemy.get_status_info()[0] == ("Name", "Still Bullet Bill")


def test_scribe_world_overview_footer_retranslates(qapp):
    overview = WorldOverview.__new__(WorldOverview)
    overview.world_data_points = [SimpleNamespace(screen_count=2, level_count=3)]

    install_language(qapp, "en")
    assert (
        catalog_value("en", "ScribeWorldOverview", "status.world_capacity_summary").format(
            screen_count=2, screen_limit=19, level_count=3, level_limit=340
        )
        == overview.status_msg
    )

    install_language(qapp, "it")
    assert overview.status_msg == tr("ScribeWorldOverview", "status.world_capacity_summary").format(
        screen_count=2, screen_limit=19, level_count=3, level_limit=340
    )

    install_language(qapp, "es")
    assert overview.status_msg == tr("ScribeWorldOverview", "status.world_capacity_summary").format(
        screen_count=2, screen_limit=19, level_count=3, level_limit=340
    )

    install_language(qapp, "en")


def test_scribe_tool_window_tabs_retranslate_live(monkeypatch, qtbot, qapp):
    tool_window_module = importlib.import_module("scribe.gui.tool_window.tool_window")
    monkeypatch.setattr(tool_window_module, "BlockPicker", FakeScribeTool)
    monkeypatch.setattr(tool_window_module, "LevelPointerList", FakeScribeTool)
    monkeypatch.setattr(tool_window_module, "SpriteList", FakeScribeTool)
    monkeypatch.setattr(tool_window_module, "LocksList", FakeScribeTool)

    install_language(qapp, "en")
    tool_window = tool_window_module.ToolWindow(None, SimpleNamespace())
    qtbot.addWidget(tool_window)
    tool_window.show()

    assert tool_window.windowTitle() == catalog_value("en", "scribe.tool_window", "window.title")
    assert [tool_window.tabbed_widget.tabText(index) for index in range(4)] == [
        catalog_value("en", "scribe.tool_window", "tab.tiles"),
        catalog_value("en", "scribe.tool_window", "tab.level_pointers"),
        catalog_value("en", "scribe.tool_window", "tab.sprites"),
        catalog_value("en", "scribe.tool_window", "tab.locks_bridges"),
    ]

    install_language(qapp, "es")
    tool_window.retranslate_ui()
    assert tool_window.windowTitle() == catalog_value("es", "scribe.tool_window", "window.title")
    assert [tool_window.tabbed_widget.tabText(index) for index in range(4)] == [
        catalog_value("es", "scribe.tool_window", "tab.tiles"),
        catalog_value("es", "scribe.tool_window", "tab.level_pointers"),
        catalog_value("es", "scribe.tool_window", "tab.sprites"),
        catalog_value("es", "scribe.tool_window", "tab.locks_bridges"),
    ]
    assert tool_window.level_pointer_list.retranslate_count >= 1
    assert tool_window.sprite_list.retranslate_count >= 1
    assert tool_window.locks_list.retranslate_count >= 1

    install_language(qapp, "it")
    tool_window.retranslate_ui()
    assert tool_window.windowTitle() == catalog_value("it", "scribe.tool_window", "window.title")
    assert [tool_window.tabbed_widget.tabText(index) for index in range(4)] == [
        catalog_value("it", "scribe.tool_window", "tab.tiles"),
        catalog_value("it", "scribe.tool_window", "tab.level_pointers"),
        catalog_value("it", "scribe.tool_window", "tab.sprites"),
        catalog_value("it", "scribe.tool_window", "tab.locks_bridges"),
    ]
    assert tool_window.level_pointer_list.retranslate_count >= 2
    assert tool_window.sprite_list.retranslate_count >= 2
    assert tool_window.locks_list.retranslate_count >= 2

    install_language(qapp, "en")


def test_ui_sweep_translates_representative_surfaces(qapp):
    representative_keys = (
        ("foundry.main", "menu.level"),
        ("LevelSelector", "level_selector"),
        ("LevelContextMenu", "place_object"),
        ("PipePairMixin", "enable_pipe_pair_exits"),
        ("ScribeEditWorldInfo", "world_data"),
        ("scribe.tool_window", "tab.tiles"),
        ("Common", "grid_lines"),
    )
    formatted_keys = (
        (
            "scribe.main",
            "undo.pasting_objects",
            {"count": 2},
        ),
        (
            "FoundryMainWindow",
            "error.world_level_tile_missing",
            {"world": 3},
        ),
        (
            "FoundryCommands",
            "command.add_object_at_position",
            {"object_name": "Goomba", "x_position": 3, "y_position": 4},
        ),
        (
            "ScribeCommands",
            "command.set_lp_level_address",
            {"pointer_index": 2, "level_address": 0x1234},
        ),
    )

    try:
        for locale in ("es", "it", "fr", "de"):
            assert install_language(qapp, locale)
            for context, key in representative_keys:
                assert tr(context, key) == catalog_value(locale, context, key)
            for context, key, values in formatted_keys:
                assert tr(context, key).format(**values) == catalog_value(locale, context, key).format(**values)
    finally:
        install_language(qapp, "en")
