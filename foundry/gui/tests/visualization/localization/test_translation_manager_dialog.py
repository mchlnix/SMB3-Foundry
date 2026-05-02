import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QWidget

from foundry.gui.dialogs.SettingsDialog import SettingsDialog as FoundrySettingsDialog
from foundry.gui.dialogs.TranslationManagerDialog import TranslationManagerDialog
from foundry.gui.localization import install_language, tr
from foundry.gui.tests.visualization.localization.helpers import catalog_value, visible_widget_texts


def test_translation_manager_dialog_saves_partial_user_overrides(
    temporary_translation_dir, settings_factory, qtbot, qapp
):
    install_language(qapp, "it")

    try:
        dialog = TranslationManagerDialog("it")
        qtbot.addWidget(dialog)
        dialog.show()

        assert dialog.windowTitle() == catalog_value("it", "foundry.translation_manager", "title")
        assert dialog.locale_dropdown.currentData() == "it"
        assert dialog.search_input.placeholderText() == catalog_value(
            "it", "foundry.translation_manager", "filter.search.placeholder"
        )
        assert dialog.context_filter.count() > 1
        assert not dialog.save_button.isEnabled()
        assert dialog.fit_columns_button.text() == catalog_value(
            "it", "foundry.translation_manager", "button.fit_columns"
        )
        header = dialog.translation_table.horizontalHeader()
        for column in range(dialog.model.columnCount()):
            assert header.sectionResizeMode(column) == QHeaderView.ResizeMode.Interactive
        assert dialog.translation_table.horizontalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAsNeeded
        assert dialog.translation_table.horizontalScrollMode() == QAbstractItemView.ScrollMode.ScrollPerPixel

        original_key_width = dialog.translation_table.columnWidth(dialog.model.COLUMN_KEY)
        manual_key_width = original_key_width + 37
        dialog.translation_table.setColumnWidth(dialog.model.COLUMN_KEY, manual_key_width)
        button_search_term = "".join(("but", "ton"))
        dialog.search_input.setText(button_search_term)
        assert dialog.translation_table.columnWidth(dialog.model.COLUMN_KEY) == manual_key_width
        dialog.fit_columns()
        assert (
            dialog.translation_table.columnWidth(dialog.model.COLUMN_KEY)
            == dialog.DEFAULT_COLUMN_WIDTHS[dialog.model.COLUMN_KEY]
        )

        screen_width = dialog.screen().availableGeometry().width()
        assert dialog.width() <= screen_width // 2
        assert dialog.width() >= min(dialog.MINIMUM_TABLE_WIDTH, screen_width // 2)
        settings_parent = QWidget()
        qtbot.addWidget(settings_parent)
        settings_dialog = FoundrySettingsDialog(settings_factory("translation-button"), settings_parent)
        qtbot.addWidget(settings_dialog)
        assert catalog_value("it", "SettingsDialog", "translations") in visible_widget_texts(settings_dialog)

        row = dialog._find_row("foundry.settings", "style.retro")
        assert row >= 0
        assert dialog.model.rows[row].english == catalog_value("en", "foundry.settings", "style.retro")
        assert dialog.model.rows[row].translation == catalog_value("it", "foundry.settings", "style.retro")

        unchanged_row = dialog._find_row("foundry.translation_manager", "status.ok")
        assert unchanged_row >= 0
        assert dialog.model.rows[unchanged_row].translation == catalog_value(
            "it", "foundry.translation_manager", "status.ok"
        )
        assert dialog.model.rows[unchanged_row].status_kind == "unchanged"

        search_term = ".".join(("style", "retro"))
        dialog.search_input.setText(search_term)
        assert dialog.proxy_model.rowCount() == 1
        assert dialog.detail_english_text.toPlainText() == catalog_value("en", "foundry.settings", "style.retro")
        assert dialog.detail_translation_text.toPlainText() == catalog_value("it", "foundry.settings", "style.retro")

        custom_translation = "TEST_RETRO_STYLE"
        dialog.detail_translation_text.setPlainText(custom_translation)
        assert dialog.save_button.isEnabled()
        assert dialog.model.rows[row].dirty
        assert "1/" in dialog.summary_label.text()
        dialog.save_changes()

        override_catalog = json.loads((temporary_translation_dir / "it.json").read_text(encoding="utf-8"))
        assert override_catalog == {"foundry.settings": {"style.retro": custom_translation}}
        assert install_language(qapp, "it")
        assert tr("foundry.settings", "style.retro") == custom_translation

        dialog.revert_user_catalog()
        assert not (temporary_translation_dir / "it.json").exists()
        assert install_language(qapp, "it")
        assert tr("foundry.settings", "style.retro") == catalog_value("it", "foundry.settings", "style.retro")

        dialog.status_filter.setCurrentIndex(dialog.status_filter.findData("missing"))
        assert dialog.proxy_model.rowCount() < dialog.model.rowCount()
    finally:
        install_language(qapp, "en")


def test_translation_manager_dialog_filters_validation_issues(temporary_translation_dir, qtbot, qapp):
    install_language(qapp, "it")

    try:
        dialog = TranslationManagerDialog("it")
        qtbot.addWidget(dialog)

        search_term = ".".join(("summary", "bytes"))
        dialog.search_input.setText(search_term)
        assert dialog.proxy_model.rowCount() == 1

        dialog.detail_translation_text.setPlainText("Riepilogo non valido")
        assert not dialog.save_button.isEnabled()
        assert "Expected tokens" in dialog.detail_status_label.text()

        dialog.status_filter.setCurrentIndex(dialog.status_filter.findData("issues"))
        assert dialog.proxy_model.rowCount() == 1
    finally:
        install_language(qapp, "en")
