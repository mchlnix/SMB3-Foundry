import re

from foundry.gui.dialogs.JumpEditor import JumpAction, JumpVerticalPosition
from foundry.gui.dialogs.LevelHeaderEditor import CameraMovement, HeaderMusic, HeaderStartAction, HeaderTime
from foundry.gui.localization import translation_key
from foundry.gui.tests.visualization.localization.helpers import (
    SUPPORTED_LOCALES,
    TARGET_LOCALES,
    assert_structural_tokens_match,
    catalog_value,
    load_test_catalog,
)


def test_target_catalogs_preserve_structural_tokens():
    english_catalog = load_test_catalog("en")

    for locale in TARGET_LOCALES:
        catalog = load_test_catalog(locale)
        for context, translations in catalog.items():
            for key, translated in translations.items():
                baseline = english_catalog[context][key]
                assert_structural_tokens_match(baseline, translated)


def test_english_catalog_maps_all_sources_to_themselves():
    catalog = load_test_catalog("en")

    for context, translations in catalog.items():
        for key, translated in translations.items():
            assert re.fullmatch(r"^[a-z0-9][a-z0-9_.-]*$", key), (context, key)
            assert translated, (context, key)


def test_locale_catalogs_cover_the_same_required_sources():
    english_catalog = load_test_catalog("en")
    english_keys = {(context, key) for context, translations in english_catalog.items() for key in translations}

    for locale in TARGET_LOCALES:
        locale_catalog = load_test_catalog(locale)
        locale_keys = {(context, key) for context, translations in locale_catalog.items() for key in translations}

        assert english_keys == locale_keys, locale


def test_display_constants_are_catalog_backed_without_translating_symbol_names():
    english_catalog = load_test_catalog("en")

    assert catalog_value("en", "foundry.jump_editor", "jumpaction.downward_pipe_1")
    for locale in SUPPORTED_LOCALES:
        assert catalog_value(locale, "foundry.jump_editor", "jumpaction.downward_pipe_1")
        assert catalog_value(locale, "foundry.level_header_editor", "headermusic.plain_level")

    assert "Downward Pipe 1" not in english_catalog.get("JumpEditor", {})
    assert "00 (Vertical)" not in english_catalog.get("JumpEditor", {})
    assert "Plain level" not in english_catalog.get("LevelHeaderEditor", {})
    assert "Out of pipe ↑" not in english_catalog.get("LevelHeaderEditor", {})

    for locale in SUPPORTED_LOCALES:
        catalog = load_test_catalog(locale)
        assert "JUMP_ACTIONS" not in catalog.get("JumpEditor", {})
        assert "VERT_POSITIONS" not in catalog.get("JumpEditor", {})


def test_enum_display_option_values_preserve_encoded_indexes():
    assert [int(option) for option in JumpAction] == list(range(0x10))
    assert [int(option) for option in JumpVerticalPosition] == list(range(0x10))
    assert [int(option) for option in HeaderStartAction] == list(range(0x8))
    assert [int(option) for option in HeaderMusic] == list(range(0x10))
    assert [int(option) for option in HeaderTime] == list(range(0x4))
    assert [int(option) for option in CameraMovement] == list(range(0x4))


def test_enemy_item_display_names_are_catalog_backed():
    representative_sources = (
        "Bullet Bills",
        "Still Bullet Bill",
        "Chain Chomp",
        "Podoboo (comes out of lava)",
        "Hammer Brother",
    )

    for locale in SUPPORTED_LOCALES:
        enemy_items = load_test_catalog(locale)["data.enemy_item"]
        for source in representative_sources:
            key = translation_key(source)
            assert key in enemy_items, (locale, source, key)
            assert enemy_items[key], (locale, source, key)
