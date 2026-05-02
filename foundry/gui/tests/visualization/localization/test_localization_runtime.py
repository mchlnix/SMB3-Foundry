from foundry.gui.localization import (
    JsonTranslator,
    available_languages,
    install_language,
    install_language_from_settings,
    load_effective_catalog,
    save_user_catalog,
    tr,
    tr_data_name,
    translation_key,
    user_translation_dir,
)
from foundry.gui.tests.visualization.localization.helpers import catalog_value


def test_default_language_is_english(settings_factory):
    assert settings_factory("default-language").value("editor/language") == "en"


def test_install_language_uses_json_catalog(qapp):
    assert install_language(qapp, "en")
    assert tr("SettingsDialog", "language", "Language:") == catalog_value("en", "SettingsDialog", "language")
    assert tr("lang", "english") == catalog_value("en", "lang", "english")

    assert install_language(qapp, "es")

    try:
        assert tr("SettingsDialog", "language", "Language:") == catalog_value("es", "SettingsDialog", "language")
        assert tr("lang", "english") == catalog_value("es", "lang", "english")
        assert tr("Common", "open_rom", "Open ROM") == catalog_value("es", "Common", "open_rom")
    finally:
        install_language(qapp, "en")


def test_keyed_translation_falls_back_to_english_catalog(qapp):
    assert install_language(qapp, "es")

    try:
        assert tr("foundry.size_bar", "objects") == catalog_value("es", "foundry.size_bar", "objects")
        missing_key = ".".join(("missing", "example"))
        assert tr("foundry.size_bar", missing_key, "Readable fallback") == "Readable fallback"
        assert tr("foundry.size_bar", missing_key) == "missing.example"
    finally:
        install_language(qapp, "en")


def test_translation_preserves_accelerators_and_placeholders(qapp):
    assert install_language(qapp, "es")

    try:
        translated = tr("scribe.view_menu", "action.airship_travel_path")

        assert "&" in translated
        assert "{index}" in translated
        assert translated.format(index=2).endswith("2")
    finally:
        install_language(qapp, "en")


def test_data_name_translation_keeps_identity_at_display_boundary(qapp):
    representative_names = (
        ("Tile", "Cloud Upper Left"),
        ("Tile", "? 3"),
        ("MapItem", "Cloud"),
        ("ObjectSet", "Cloudy"),
        ("LevelObject", "Underwater Flat Ground"),
        ("LevelObject", "White Block Platform (Floating)"),
        ("LevelObject", "'?' with Flower"),
        ("LevelObject", "World 5 - Clouds A"),
        ("StockLevel", "World 1 Map"),
        ("StockLevel", "Dungeon"),
    )
    data_contexts = {
        "Tile": "data.tile",
        "MapItem": "data.map_item",
        "ObjectSet": "data.object_set",
        "LevelObject": "data.level_object",
        "StockLevel": "data.stock_level",
    }

    try:
        for locale in ("es", "it"):
            assert install_language(qapp, locale)
            for context, source in representative_names:
                assert tr_data_name(context, source) == catalog_value(
                    locale, data_contexts[context], translation_key(source)
                )
    finally:
        install_language(qapp, "en")


def test_data_name_translation_falls_back_to_english_for_missing_or_blank_entries(qapp):
    assert install_language(qapp, "es")

    blank_translator = JsonTranslator({"BlankData": {"Known Name": ""}})
    qapp.installTranslator(blank_translator)

    try:
        assert tr_data_name("BlankData", "Known Name") == "Known Name"
        assert tr_data_name("LevelObject", "Uncataloged Test Object") == "Uncataloged Test Object"
    finally:
        qapp.removeTranslator(blank_translator)
        install_language(qapp, "en")


def test_language_setting_installs_selected_translator(qapp, settings_factory):
    settings = settings_factory("localization-install")
    expected_languages = {"en", "es", "es_ES", "es_419", "it", "de", "fr", "pt_BR", "pt_PT"}
    assert expected_languages.issubset(set(available_languages()))

    try:
        expected_names = {
            "es": ("spanish", "Español"),
            "es_ES": ("spanish_spain", "Español (España)"),
            "es_419": ("spanish_latin_america", "Español (Latinoamérica)"),
            "it": ("italian", "Italiano"),
            "de": ("german", "Deutsch"),
            "fr": ("french", "Français"),
            "pt_BR": ("portuguese_brazil", "Português (Brasil)"),
            "pt_PT": ("portuguese_portugal", "Português (Portugal)"),
        }
        for language_code, (name_key, expected_name) in expected_names.items():
            settings.setValue("editor/language", language_code)
            assert install_language_from_settings(qapp, settings)
            assert tr("lang", name_key) == expected_name
    finally:
        install_language(qapp, "en")


def test_user_translation_catalog_overrides_and_custom_language(temporary_translation_dir, qapp):
    try:
        save_user_catalog(
            "zz",
            {
                "_meta": {"display_name": "Zed Locale"},
                "foundry.settings": {"style.retro": "TEST_STYLE_RETRO"},
            },
        )

        assert user_translation_dir() == temporary_translation_dir
        assert "zz" in available_languages()
        assert install_language(qapp, "zz")
        assert tr("foundry.settings", "style.retro") == "TEST_STYLE_RETRO"
        assert tr("foundry.settings", "style.dracula") == catalog_value("en", "foundry.settings", "style.dracula")
        assert load_effective_catalog("zz")["foundry.settings"]["style.retro"] == "TEST_STYLE_RETRO"
    finally:
        install_language(qapp, "en")
