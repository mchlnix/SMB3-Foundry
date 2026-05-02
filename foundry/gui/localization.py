"""Install catalog-backed, display-only translations for Foundry and Scribe.

This module is the runtime boundary between stable editor identities and
translated UI text. ROM data, object ids, settings keys, undo command payloads,
parser symbols, and source ``.dat`` records remain English and stable. Qt
widgets receive localized strings only when those values are rendered for a
person.

Built-in catalogs live under ``data/translations``. User catalogs are partial
overlays discovered from a writable translation directory and merged at runtime.
The effective catalog order is bundled English, English user overlay, bundled
selected locale, then selected-locale user overlay. Normal blank overlay values
are ignored so a partial or accidentally blank user catalog falls back instead
of showing empty labels.

See Also
--------
foundry.gui.dialogs.TranslationManagerDialog
    User-facing editor for writable overlay catalogs.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PySide6.QtCore import QCoreApplication, QLocale, QStandardPaths, QTranslator

LANGUAGE_SYSTEM = "system"
LANGUAGE_ENGLISH = "en"
LANGUAGE_SPANISH = "es"
LANGUAGE_SPANISH_SPAIN = "es_ES"
LANGUAGE_SPANISH_LATIN_AMERICA = "es_419"
LANGUAGE_ITALIAN = "it"
LANGUAGE_GERMAN = "de"
LANGUAGE_FRENCH = "fr"
LANGUAGE_PORTUGUESE_BRAZIL = "pt_BR"
LANGUAGE_PORTUGUESE_PORTUGAL = "pt_PT"

LANGUAGE_CODES = (
    LANGUAGE_SYSTEM,
    LANGUAGE_ENGLISH,
    LANGUAGE_SPANISH,
    LANGUAGE_SPANISH_SPAIN,
    LANGUAGE_SPANISH_LATIN_AMERICA,
    LANGUAGE_ITALIAN,
    LANGUAGE_GERMAN,
    LANGUAGE_FRENCH,
    LANGUAGE_PORTUGUESE_BRAZIL,
    LANGUAGE_PORTUGUESE_PORTUGAL,
)
LANGUAGE_CONTEXT = "Language"
LANGUAGE_KEY_CONTEXT = "lang"
DATA_NAME_CONTEXTS = frozenset(
    (
        "Tile",
        "ObjectSet",
        "MapObject",
        "MapItem",
        "LevelObject",
        "EnemyItem",
        "StockLevel",
        "MusicTheme",
        "GraphicsSet",
    )
)
DATA_NAME_KEY_CONTEXTS = {
    "Tile": "data.tile",
    "ObjectSet": "data.object_set",
    "MapObject": "data.map_object",
    "MapItem": "data.map_item",
    "LevelObject": "data.level_object",
    "EnemyItem": "data.enemy_item",
    "StockLevel": "data.stock_level",
    "MusicTheme": "data.music_theme",
    "GraphicsSet": "data.graphics_set",
}

_TRANSLATION_DIR = Path(__file__).parents[2] / "data" / "translations"
_USER_TRANSLATION_ENV = "FOUNDRY_USER_TRANSLATION_DIR"
_METADATA_CONTEXT = "_meta"
_METADATA_DISPLAY_NAME = "display_name"
_installed_translator: QTranslator | None = None
_installed_catalog: dict[str, dict[str, str]] = {}
_english_catalog: dict[str, dict[str, str]] | None = None
_KEY_PART_RE = re.compile(r"[^a-z0-9]+")
_FORMAT_FIELD_RE = re.compile(r"\{[^{}]+\}")
_PRINTF_TOKEN_RE = re.compile(r"%(?:\([^)]+\))?[#0 +\-]?(?:\d+|\*)?(?:\.\d+)?[bcdeEfFgGnosxX%]")
_HTML_TAG_RE = re.compile(r"</?[A-Za-z][^>]*>")
_ACCELERATOR_RE = re.compile(r"(?<!&)&(?!&)")
_SOURCE_TEXT_DEFAULT_KEYS = {
    "0 Overworld": "object_set.0x0_overworld",
    "1 Plains": "object_set.0x1_plains",
    "2 Dungeon": "object_set.0x2_dungeon",
    "3 Hilly": "object_set.0x3_hilly",
    "4 Sky": "object_set.0x4_sky",
    "5 Piranha Plant": "object_set.0x5_piranha_plant",
    "6 Water": "object_set.0x6_water",
    "7 Mushroom": "object_set.0x7_mushroom",
    "8 Pipe": "object_set.0x8_pipe",
    "9 Desert": "object_set.0x9_desert",
    "A Ship": "object_set.0xa_ship",
    "B Giant": "object_set.0xb_giant",
    "C Ice": "object_set.0xc_ice",
    "D Cloudy": "object_set.0xd_cloudy",
    "E Underground": "object_set.0xe_underground",
    "F Spade Bonus": "object_set.0xf_spade_bonus",
    "3 Green Koopa Paratroopas": "three_green_koopa_paratroopas",
    "3 Yellow Cheep-Cheeps": "three_yellow_cheep_cheeps",
    "Changes exit location on map (works on warp pipe levels)": "map_exit_location_changer",
    "Double Rotodisc (rotates both ways, starting at sides)": "double_rotodisc_side_start",
    "Double Rotodisc (rotates both ways, starting at top)": "double_rotodisc_top_start",
    "Infinite Bob-Ombs (leftward) (use with bullet shooters)": "infinite_bob_ombs_left",
    "Infinite Bob-Ombs (rightward) (use with bullet shooters)": "infinite_bob_ombs_right",
    "Invisible door (appears when you hit a P-switch)": "invisible_p_switch_door",
    "Jumping Cheep-Cheep (2 jumps, down and right)": "jumping_cheep_cheep_down_right",
    "Jumping Cheep-Cheep (3 jumps, up and right)": "jumping_cheep_cheep_up_right",
    "Still wooden platform (moves right when stepped on)": "wooden_platform_still_right_step",
    "Wooden platform - moves back and forth (a little)": "wood_platform_short_horizontal",
    "Wooden platform - moves back and forth (a lot)": "wood_platform_long_horizontal",
    "Wooden platform - moves left,falls when stepped on": "wooden_platform_left_fall_step",
    "Wooden platform - moves up and down (a little)": "wood_platform_short_vertical",
    "Wooden platform - moves up and down (a lot)": "wood_platform_long_vertical",
    "1 Background Pillar": "variant_1_background_pillar",
    "1 Background Pole": "variant_1_background_pole",
    "1 Hill Strip": "variant_1_hill_strip",
    "1 Metal Bar A": "variant_1_metal_bar_a",
    "1 Metal Bar B": "variant_1_metal_bar_b",
    "1 Plain Background (used to block out stuff)": "variant_1_plain_background_mask",
    "1 Platform Wire": "variant_1_platform_wire",
    "1 no-ended pipe": "variant_1_no_ended_pipe",
    "1 platform wire": "variant_1_platform_wire_lowercase",
    "2-Way Bullet Shooter": "two_way_bullet_shooter",
    "4-Way Bullet Shooter A": "four_way_bullet_shooter_a",
    "4-Way Bullet Shooter B": "four_way_bullet_shooter_b",
    "E. End of Road over Water": "east_end_road_over_water",
    "E. Road Connector A": "east_road_connector_a",
    "E. Road Connector B": "east_road_connector_b",
    "E. Road Connector C": "east_road_connector_c",
    "E. Road Connector over Water": "east_road_connector_water",
    "E.-W. Drawbridge": "east_west_drawbridge",
    "E.-W. Road A": "east_west_road_a",
    "E.-W. Road B": "east_west_road_b",
    "E.-W. Road C": "east_west_road_c",
    "E.-W. Road over Water": "east_west_road_water",
    "Flat Ground with green on top (SMAS only)": "smas_flat_ground_green_top",
    "Hilly Wall - 50=right, 51=left (SMAS only)": "smas_hilly_wall_left_right",
    "Horizontal Plain Background A (used to block out stuff)": "horizontal_bg_mask_a",
    "Horizontal Plain Background B (used to block out stuff)": "horizontal_bg_mask_b",
    "Silver Coins (appear when you hit a P-Switch)": "p_switch_silver_coins",
    "Wooden Ship Beam with 2 strips of wood": "ship_beam_double_strip",
    "World 5 - E-W Road Connector view from clouds": "w5_clouds_east_west_connector",
    "World 5 - E-W Road view from clouds": "w5_clouds_east_west_road",
    "World 5 - SE Road view from clouds A": "w5_clouds_southeast_road_a",
    "World 5 - SE Road view from clouds B": "w5_clouds_southeast_road_b",
    "World 8 - Bottom Left of Bowser's Castle": "w8_bowser_castle_bottom_left",
    "World 8 - Bottom Right of Bowser's Castle": "w8_bowser_castle_bottom_right",
    "World 8 - Top Left of Bowser's Castle": "w8_bowser_castle_top_left",
    "World 8 - Top Right of Bowser's Castle": "w8_bowser_castle_top_right",
}


@dataclass(frozen=True)
class CatalogValidationIssue:
    """Describe one user catalog validation finding.

    Validation issues are shared by the localization core and the Translation
    Manager. They describe display-catalog problems without changing catalog
    identity, ROM data, settings values, or parser-facing names.

    Attributes
    ----------
    context : str
        Catalog context that owns the finding, or ``""`` for whole-catalog
        shape errors.
    key : str
        Catalog key that owns the finding, or ``""`` when the issue is not tied
        to a single entry.
    issue : str
        Stable machine-readable issue code.
    message : str
        Human-readable validation message shown in the Translation Manager.
    severity : str
        ``"error"`` blocks import or save; ``"warning"`` is displayed but may
        still be useful for partial user overlays.

    See Also
    --------
    validate_catalog
        Produces these issues for imported or edited user overlays.
    """

    context: str
    key: str
    issue: str
    message: str
    severity: str = "error"


class JsonTranslator(QTranslator):
    """Translate Qt strings from a JSON catalog.

    ``JsonTranslator`` adapts the merged JSON catalog to Qt's
    :class:`QTranslator` interface. It supports Qt callbacks that still pass
    source text by also checking :func:`translation_key` when an exact
    source-text lookup is missing.

    Parameters
    ----------
    catalog : dict[str, dict[str, str]]
        Effective translation catalog already merged by
        :func:`load_effective_catalog`.

    Notes
    -----
    The translator falls back to the ``Common`` context after checking the
    exact owner context. This keeps repeated labels such as ``Cancel`` and
    ``Enabled`` consistent without forcing every caller to share one context.

    Attributes
    ----------
    _catalog : dict[str, dict[str, str]]
        Effective merged catalog used for display lookup. It contains only UI
        text and must not become the source of ROM data, object identity,
        settings values, or undo/replay payloads.
    """

    def __init__(self, catalog: dict[str, dict[str, str]]):
        """Store the effective catalog used by Qt translation callbacks.

        Parameters
        ----------
        catalog : dict[str, dict[str, str]]
            Already merged display catalog from :func:`load_effective_catalog`.
            The translator keeps a reference to this mapping for lookup only;
            it does not validate, normalize, or mutate catalog contents.
        """
        super().__init__()
        self._catalog = catalog

    def translate(self, context: str, source_text: str, disambiguation: str | None = None, n: int = -1) -> str:
        """Resolve one Qt display lookup against the merged JSON catalog.

        This is the only place where Qt's ``QTranslator`` callback touches the
        effective Foundry catalog. It serves already-merged display text to
        menus, dialogs, and labels while leaving ROM data, SMB3 object
        identity, settings keys, and undo payloads in their stable source form.

        Parameters
        ----------
        context : str
            Qt translation context supplied by the caller.
        source_text : str
            Original English display text.
        disambiguation : str | None, optional
            Optional Qt disambiguation string.
        n : int, optional
            Plural count supplied by Qt.

        Returns
        -------
        str
            Translated display text, or an empty string when this catalog does
            not own the string so Qt can continue fallback handling.

        Notes
        -----
        Qt calls this method while painting labels, menus, and dialogs. The
        lookup accepts Qt's source text and its deterministic generated key as
        fallback shapes, but the returned value is always display text and is
        never written back into Foundry identities.
        ``JsonTranslator`` is the adapter layer between Qt's translation
        callback API and Foundry's JSON catalog/overlay system, so widget code
        can ask Qt for labels without knowing how user overlays were merged.

        Returning ``""`` for a miss is intentional Qt translator behavior: it
        lets Qt continue to the next translator or caller fallback while
        keeping Foundry's catalog merge order outside widget code.
        ROM-backed names, SMB3 parser constants, and settings keys therefore
        stay in their original stable form while Qt receives localized labels.
        The method is stateless for each lookup: installing a new language
        replaces the translator instance rather than mutating widget-owned
        data during translation.
        """
        del disambiguation, n

        if context in self._catalog and source_text in self._catalog[context]:
            return self._catalog[context][source_text]

        keyed_source = translation_key(source_text)
        if context in self._catalog and keyed_source in self._catalog[context]:
            return self._catalog[context][keyed_source]

        common_catalog = self._catalog.get("Common", {})
        return common_catalog.get(source_text, "") or common_catalog.get(keyed_source, "")


def available_languages() -> tuple[str, ...]:
    """Discover stable locale codes selectable by Foundry's Qt UI.

    The result includes the built-in ``LANGUAGE_CODES`` values, bundled catalog
    file stems, and user catalog file stems. Known codes keep their configured
    order so settings remain stable, while custom user locales are appended in
    sorted order. ``system`` is included here for settings, but callers such as
    the Translation Manager may omit it because user catalogs are saved by
    concrete locale code.

    Returns
    -------
    tuple[str, ...]
        Stable locale codes, not translated display names.
    """
    discovered_codes = {
        *LANGUAGE_CODES,
        *(_catalog_path.stem for _catalog_path in _TRANSLATION_DIR.glob("*.json")),
        *(_catalog_path.stem for _catalog_path in user_translation_dir().glob("*.json")),
    }
    ordered_codes = [language_code for language_code in LANGUAGE_CODES if language_code in discovered_codes]
    ordered_codes.extend(sorted(discovered_codes - set(ordered_codes) - {LANGUAGE_SYSTEM}))
    return tuple(ordered_codes)


def language_display_name(language_code: str) -> str:
    """Resolve a locale code into the label shown in Foundry's Qt controls.

    Known locales are translated through the ``lang`` catalog context. Custom
    catalogs can provide ``"_meta": {"display_name": "..."}``; otherwise the
    locale code itself is shown. The returned name is display text only and
    must not be written back as the settings value.
    Language selectors should store ``language_code`` and use this value only
    for the visible row text.
    Settings dialogs and the Translation Manager use this helper while
    rebuilding combo boxes after catalog discovery, so locale identity flows
    through item data while the label is refreshed from the installed catalog.
    The selected settings state therefore stays code-facing while the Qt
    display text can change during live language workflows.

    Parameters
    ----------
    language_code : str
        Language code stored in settings.

    Returns
    -------
    str
        Translated display name for the language.
    """
    names = {
        LANGUAGE_SYSTEM: tr(LANGUAGE_KEY_CONTEXT, "system_default", "System default"),
        LANGUAGE_ENGLISH: tr(LANGUAGE_KEY_CONTEXT, "english", "English"),
        LANGUAGE_SPANISH: tr(LANGUAGE_KEY_CONTEXT, "spanish", "Spanish"),
        LANGUAGE_SPANISH_SPAIN: tr(LANGUAGE_KEY_CONTEXT, "spanish_spain", "Spanish (Spain)"),
        LANGUAGE_SPANISH_LATIN_AMERICA: tr(
            LANGUAGE_KEY_CONTEXT,
            "spanish_latin_america",
            "Spanish (Latin America)",
        ),
        LANGUAGE_ITALIAN: tr(LANGUAGE_KEY_CONTEXT, "italian", "Italian"),
        LANGUAGE_GERMAN: tr(LANGUAGE_KEY_CONTEXT, "german", "German"),
        LANGUAGE_FRENCH: tr(LANGUAGE_KEY_CONTEXT, "french", "French"),
        LANGUAGE_PORTUGUESE_BRAZIL: tr(LANGUAGE_KEY_CONTEXT, "portuguese_brazil", "Portuguese (Brazil)"),
        LANGUAGE_PORTUGUESE_PORTUGAL: tr(
            LANGUAGE_KEY_CONTEXT,
            "portuguese_portugal",
            "Portuguese (Portugal)",
        ),
    }
    if language_code in names:
        return names[language_code]

    metadata_name = _catalog_metadata_display_name(language_code)
    return metadata_name or language_code


def resolved_language(language_code: str) -> str:
    """Resolve a stored language code to a concrete catalog code.

    ``system`` resolves through :class:`QLocale` and the project fallback
    policy. Exact catalog matches win first; Spanish falls back to ``es_419``
    and then ``es``, Portuguese falls back to ``pt_BR``, and base English,
    Italian, German, and French locales fall back to their base catalog.
    The result feeds catalog loading for Qt display text only; it does not
    rewrite Foundry settings, ROM metadata, or SMB3 data labels.
    ``install_language`` consumes the resolved code, then the selected catalog
    flows into the installed translator and the ``tr`` fallback cache.

    Parameters
    ----------
    language_code : str
        Stored settings value, usually a concrete locale code or ``system``.

    Returns
    -------
    str
        Normalized locale code used to load catalogs.
    """
    if language_code == LANGUAGE_SYSTEM:
        return _resolve_system_language()
    return _normalize_language_code(language_code)


def _normalize_language_code(language_code: str) -> str:
    """Convert a user or Qt locale code into Foundry's catalog filename form.

    Qt and user input may use hyphenated locale tags, while catalog files and
    settings comparisons use underscore-separated stems. Normalization keeps
    language discovery and overlay lookup on stable file identities without
    translating or validating the displayed language name.
    The normalized value flows into catalog path construction, system-language
    fallback checks, and user-overlay saves so all three lifecycle paths probe
    the same JSON filename.

    Parameters
    ----------
    language_code : str
        Locale code from settings, Qt, or a user catalog filename.

    Returns
    -------
    str
        Locale code using underscores, suitable for catalog path lookup.
    """
    return language_code.replace("-", "_")


def _catalog_exists(language_code: str) -> bool:
    """Check whether Foundry can load display text for a locale code.

    The probe covers both read-only bundled catalogs and writable user
    overlays so system-language resolution can select custom installed
    catalogs as well as shipped Qt display catalogs.
    ``_resolve_system_language`` uses this result to decide which catalog code
    enters the translator install path.
    That boundary protects the install workflow from loading a missing catalog
    while preserving the selected settings state.

    Parameters
    ----------
    language_code : str
        Locale code to normalize and probe.

    Returns
    -------
    bool
        ``True`` when either the read-only bundled catalog or the writable user
        overlay file exists for the normalized code.

    Notes
    -----
    This is a discovery helper only. It does not load or merge catalogs, and
    it treats locale codes as stable file identities rather than translated
    language names.
    """
    return any(path.exists() for path in translation_catalog_paths(language_code))


def _resolve_system_language() -> str:
    """Resolve the OS locale to the best supported catalog.

    The resolver tries an exact normalized locale first, then applies the
    project regional policy for Spanish and Portuguese catalogs. Supported
    one-catalog languages fall back to their base language, and English is the
    final fallback when no catalog exists for the system locale family.
    The selected code flows into ``load_effective_catalog`` during Qt
    translator installation; the stored ``system`` preference is not rewritten.

    Returns
    -------
    str
        Concrete locale code used for Foundry Qt catalog loading.
    """
    locale_name = _normalize_language_code(QLocale.system().name())
    base_language = locale_name.split("_", 1)[0].lower()
    candidates = [locale_name]

    if base_language == "es":
        candidates.extend((LANGUAGE_SPANISH_LATIN_AMERICA, LANGUAGE_SPANISH))
    elif base_language == "pt":
        candidates.append(LANGUAGE_PORTUGUESE_BRAZIL)
    elif base_language in {
        LANGUAGE_ENGLISH,
        LANGUAGE_ITALIAN,
        LANGUAGE_GERMAN,
        LANGUAGE_FRENCH,
    }:
        candidates.append(base_language)

    for candidate in candidates:
        if candidate in LANGUAGE_CODES and _catalog_exists(candidate):
            return candidate

    return LANGUAGE_ENGLISH


def user_translation_dir() -> Path:
    """Locate the writable directory for Foundry user translation overlays.

    Directory discovery is intentionally explicit so tests, portable builds,
    and packaged applications can share the same catalog overlay behavior:
    ``FOUNDRY_USER_TRANSLATION_DIR`` wins first, then the platform
    application-data location, then the ``~/.smb3-foundry/translations``
    compatibility fallback for older user catalog locations.
    The returned path is where the Translation Manager imports, saves, and
    removes partial JSON overlays; bundled catalogs remain read-only.

    Returns
    -------
    Path
        Directory that may contain partial user catalog JSON files.
    """
    override_dir = os.environ.get(_USER_TRANSLATION_ENV, "")
    if override_dir:
        return Path(override_dir)

    data_location = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    if data_location:
        return Path(data_location) / "translations"

    return Path.home() / ".smb3-foundry" / "translations"


def translation_catalog_paths(language_code: str) -> tuple[Path | None, Path]:
    """Build bundled and writable catalog paths for a Foundry locale.

    This keeps catalog discovery on locale-code file stems rather than
    translated language names. Callers can load the bundled catalog when it
    exists and separately manage the user overlay path used by the Translation
    Manager.
    The returned paths coordinate the load, save, delete, and merge lifecycle
    for Qt display catalogs without touching ROM or SMB3 level data.

    Parameters
    ----------
    language_code : str
        Locale code or custom user-catalog stem.

    Returns
    -------
    tuple[Path | None, Path]
        Built-in catalog path when one exists, plus the writable user overlay
        path for the normalized locale code.
    """
    normalized_code = _normalize_language_code(language_code)
    built_in_path = _TRANSLATION_DIR / f"{normalized_code}.json"
    return built_in_path if built_in_path.exists() else None, user_translation_dir() / f"{normalized_code}.json"


def reload_available_languages() -> tuple[str, ...]:
    """Refresh language discovery after user catalog changes.

    This clears the cached English effective catalog because an English user
    overlay participates in every other effective catalog as the display
    baseline.
    Call this after importing, saving, or deleting user overlays so Qt language
    selectors and Foundry's fallback catalog see the updated files.

    Returns
    -------
    tuple[str, ...]
        Newly discovered language codes.
    """
    global _english_catalog

    _english_catalog = None
    return available_languages()


def _load_catalog_path(catalog_path: Path) -> dict[str, dict[str, str]]:
    """Load one JSON translation catalog from disk.

    Catalog loading is intentionally tolerant at the file boundary. Non-object
    roots return an empty catalog, non-object contexts are skipped, and context,
    key, and value fields are coerced to strings so validation can report
    user-facing catalog issues after import.

    Parameters
    ----------
    catalog_path : Path
        JSON file for a bundled catalog or writable user overlay.

    Returns
    -------
    dict[str, dict[str, str]]
        Catalog mapping grouped by translation context.
    """
    with catalog_path.open(encoding="utf-8") as catalog_file:
        raw_catalog = json.load(catalog_file)

    if not isinstance(raw_catalog, dict):
        return {}

    catalog: dict[str, dict[str, str]] = {}
    for context, translations in raw_catalog.items():
        if not isinstance(translations, dict):
            continue
        catalog[str(context)] = {str(source): str(translated) for source, translated in translations.items()}
    return catalog


def load_catalog(language_code: str) -> dict[str, dict[str, str]]:
    """Load a JSON translation catalog.

    Only the read-only bundled catalog is loaded here. User overlays are kept
    separate so Foundry can validate, save, remove, and merge them in the
    documented runtime order without modifying shipped catalog files.

    Parameters
    ----------
    language_code : str
        Locale code such as ``es``, ``pt_BR``, or a custom catalog stem.

    Returns
    -------
    dict[str, dict[str, str]]
        Translation catalog, or an empty mapping when the catalog does not
        exist.
    """
    built_in_path, _user_path = translation_catalog_paths(language_code)
    if built_in_path is None:
        return {}

    return _load_catalog_path(built_in_path)


def load_user_catalog(language_code: str) -> dict[str, dict[str, str]]:
    """Load a user translation overlay for ``language_code``.

    User catalogs may be partial and may contain only the keys a translator
    changed. Missing files return an empty mapping so merge callers can treat
    user overlays as optional.
    The returned values are display text layered over bundled catalogs and
    must not replace ROM data, settings values, or SMB3 parser identifiers.
    ``load_effective_catalog`` layers this mapping after bundled catalogs so a
    translator edit flows into live Qt labels without changing source data.
    This data flow lets save/import workflows stage partial overlays while
    preserving the bundled fallback state.

    Parameters
    ----------
    language_code : str
        Locale code or custom catalog stem.

    Returns
    -------
    dict[str, dict[str, str]]
        User catalog mapping, or an empty mapping when no overlay exists.
    """
    _built_in_path, user_path = translation_catalog_paths(language_code)
    if not user_path.exists():
        return {}
    return _load_catalog_path(user_path)


def _merge_catalogs(*catalogs: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    """Merge catalogs, ignoring blank normal values so fallback stays useful.

    The reserved ``"_meta"`` context is copied directly because it describes
    catalog metadata, not user-visible translation entries.
    Later catalogs override earlier ones, which implements the runtime order
    of bundled English, English user overlay, selected bundled locale, and
    selected user overlay.

    Parameters
    ----------
    *catalogs : dict[str, dict[str, str]]
        Catalogs ordered from lowest to highest display priority.

    Returns
    -------
    dict[str, dict[str, str]]
        Effective catalog used for Qt and helper lookups.
    """
    merged: dict[str, dict[str, str]] = {}
    for catalog in catalogs:
        for context, translations in catalog.items():
            if context == _METADATA_CONTEXT:
                merged.setdefault(context, {}).update(translations)
                continue
            target_context = merged.setdefault(context, {})
            for key, value in translations.items():
                if value:
                    target_context[key] = value
    return merged


def load_effective_catalog(language_code: str) -> dict[str, dict[str, str]]:
    """Load the catalog used at runtime after applying user overrides.

    The merge order is the localization contract:

    1. bundled English
    2. English user overlay
    3. bundled selected locale
    4. selected-locale user overlay

    Normal blank values are ignored during merge so partial user catalogs fall
    back through the chain. ``"_meta"`` is merged directly because it describes
    the catalog file rather than one displayed string.

    Parameters
    ----------
    language_code : str
        Stored language code or concrete locale code.

    Returns
    -------
    dict[str, dict[str, str]]
        Complete effective catalog used by Qt and :func:`tr`.
    """
    normalized_code = resolved_language(language_code)
    english_base = load_catalog(LANGUAGE_ENGLISH)
    english_user = load_user_catalog(LANGUAGE_ENGLISH)

    if normalized_code == LANGUAGE_ENGLISH:
        return _merge_catalogs(english_base, english_user)

    return _merge_catalogs(
        english_base, english_user, load_catalog(normalized_code), load_user_catalog(normalized_code)
    )


def save_user_catalog(language_code: str, catalog: dict[str, dict[str, str]]) -> Path:
    """Write a user translation overlay and return its path.

    The bundled catalogs are never modified here. This low-level helper writes
    the provided overlay as-is, so callers that accept user input must run
    :func:`validate_catalog` first. Existing files for the same locale are
    replaced at the JSON-file level by the final write.

    Parameters
    ----------
    language_code : str
        Locale code or custom user-catalog stem.
    catalog : dict[str, dict[str, str]]
        User overlay catalog to persist.

    Returns
    -------
    Path
        Path of the saved user catalog.
    """
    _built_in_path, user_path = translation_catalog_paths(language_code)
    user_path.parent.mkdir(parents=True, exist_ok=True)
    with user_path.open("w", encoding="utf-8") as catalog_file:
        json.dump(catalog, catalog_file, ensure_ascii=False, indent=2, sort_keys=True)
        catalog_file.write("\n")
    reload_available_languages()
    return user_path


def remove_user_catalog(language_code: str) -> bool:
    """Delete the user overlay for ``language_code`` when it exists.

    This removes only the writable JSON overlay managed by the Translation
    Manager. Bundled Foundry catalogs and stable ROM or SMB3 data identities
    are left untouched, then language discovery is refreshed so UI selectors
    stop advertising catalog files that no longer exist.
    Cache invalidation happens through ``reload_available_languages`` so later
    catalog merges and language lists observe the deletion.

    Parameters
    ----------
    language_code : str
        Locale code or custom user-catalog stem whose overlay should be
        removed.

    Returns
    -------
    bool
        ``True`` when an overlay file was removed.
    """
    _built_in_path, user_path = translation_catalog_paths(language_code)
    if not user_path.exists():
        return False
    user_path.unlink()
    reload_available_languages()
    return True


def _catalog_metadata_display_name(language_code: str) -> str:
    """Read a custom locale's display name from catalog metadata.

    User overlay metadata wins over bundled metadata so translators can rename
    custom language entries without changing shipped Foundry catalogs. The
    value is used only for Qt language selectors; settings continue to store
    the stable locale code.
    ``language_display_name`` consumes this value when rebuilding locale rows,
    keeping metadata in the display layer and out of persisted preferences.
    The metadata lookup coordinates user-overlay state with Qt selector labels
    without changing the selected locale code.

    Parameters
    ----------
    language_code : str
        Locale code or custom catalog stem to inspect.

    Returns
    -------
    str
        Metadata display name, or ``""`` when no catalog provides one.
    """
    for catalog in (load_user_catalog(language_code), load_catalog(language_code)):
        display_name = catalog.get(_METADATA_CONTEXT, {}).get(_METADATA_DISPLAY_NAME, "")
        if display_name:
            return display_name
    return ""


def validate_catalog(
    language_code: str,
    catalog: dict[str, dict[str, str]],
    baseline_catalog: dict[str, dict[str, str]] | None = None,
) -> list[CatalogValidationIssue]:
    """Validate one user-editable translation catalog.

    Validation is structural and local. It verifies that catalogs use the JSON
    object shape expected by the runtime, that normal keys and values are
    strings, and that translated values preserve the English baseline's
    placeholders, printf tokens, HTML tags, and keyboard accelerators.
    ``"_meta"`` is allowed for catalog metadata and is skipped by token checks.
    Unknown contexts or keys are allowed structurally because user overlays may
    define custom locales incrementally; token comparison only runs when the
    English baseline contains the same context and key.

    Blank strings and unchanged-English values are warnings because partial
    overlays are useful while a translation is in progress. Token and shape
    mismatches are errors and should block import or save.

    Parameters
    ----------
    language_code : str
        Locale code being validated. Reserved for locale-specific checks.
    catalog : dict[str, dict[str, str]]
        Candidate user catalog or partial catalog.
    baseline_catalog : dict[str, dict[str, str]] | None, optional
        English baseline used for structural token comparison.

    Returns
    -------
    list[CatalogValidationIssue]
        Validation findings sorted by traversal order.
    """
    del language_code

    issues: list[CatalogValidationIssue] = []
    baseline_catalog = baseline_catalog or english_catalog()

    if not isinstance(catalog, dict):
        return [
            CatalogValidationIssue(
                "",
                "",
                "catalog-not-object",
                "Catalog root must be a JSON object.",
            )
        ]

    for context, translations in catalog.items():
        if not isinstance(context, str):
            issues.append(
                CatalogValidationIssue(str(context), "", "context-not-string", "Catalog contexts must be strings.")
            )
        if not isinstance(translations, dict):
            issues.append(
                CatalogValidationIssue(str(context), "", "context-not-object", "Catalog context must be an object.")
            )
            continue
        for key, translated in translations.items():
            if not isinstance(key, str):
                issues.append(
                    CatalogValidationIssue(str(context), str(key), "key-not-string", "Catalog keys must be strings.")
                )
            if not isinstance(translated, str):
                issues.append(
                    CatalogValidationIssue(str(context), str(key), "value-not-string", "Translations must be strings.")
                )
                continue
            if context == _METADATA_CONTEXT:
                continue
            baseline = baseline_catalog.get(context, {}).get(key, "")
            if not translated:
                issues.append(
                    CatalogValidationIssue(context, key, "blank", "Blank values fall back to English.", "warning")
                )
                continue
            if baseline:
                issues.extend(_structural_token_issues(context, key, baseline, translated))
                if translated == baseline:
                    issues.append(
                        CatalogValidationIssue(
                            context,
                            key,
                            "unchanged",
                            "Translation matches English baseline.",
                            "warning",
                        )
                    )
    return issues


def _structural_token_issues(
    context: str,
    key: str,
    baseline: str,
    translated: str,
) -> list[CatalogValidationIssue]:
    """Detect structural token mismatches that block catalog import/save.

    This validates exact preservation of format fields, printf tokens, HTML
    tags, and Qt accelerators. It does not judge translation quality or
    naturalness; it only protects strings whose runtime formatting or markup
    would break if those structural tokens were dropped or changed.

    Parameters
    ----------
    context : str
        Catalog context that owns the translated entry.
    key : str
        Stable catalog key being compared.
    baseline : str
        English baseline display string.
    translated : str
        Candidate translated display string.

    Returns
    -------
    list[CatalogValidationIssue]
        Blocking validation issues for placeholder, HTML, printf, or
        accelerator drift.
    """
    checks = (
        ("format-token-mismatch", _FORMAT_FIELD_RE),
        ("printf-token-mismatch", _PRINTF_TOKEN_RE),
        ("html-tag-mismatch", _HTML_TAG_RE),
        ("accelerator-mismatch", _ACCELERATOR_RE),
    )
    issues: list[CatalogValidationIssue] = []
    for issue_name, pattern in checks:
        baseline_tokens = sorted(pattern.findall(baseline))
        translated_tokens = sorted(pattern.findall(translated))
        if baseline_tokens != translated_tokens:
            issues.append(
                CatalogValidationIssue(
                    context,
                    key,
                    issue_name,
                    f"Expected tokens {baseline_tokens}, found {translated_tokens}.",
                )
            )
    return issues


def english_catalog() -> dict[str, dict[str, str]]:
    """Provide Foundry's cached English catalog for Qt display fallback.

    The English user overlay participates in this catalog, so translators can
    customize English display text and still have every target locale inherit
    that adjusted baseline until it provides a locale-specific value.

    Returns
    -------
    dict[str, dict[str, str]]
        Effective English catalog after merging bundled English and the
        writable English user overlay.
    """
    global _english_catalog

    if _english_catalog is None:
        _english_catalog = load_effective_catalog(LANGUAGE_ENGLISH)

    return _english_catalog


def install_language(app: QCoreApplication, language_code: str) -> bool:
    """Install the selected display language into Qt.

    This replaces any previously installed JSON translator, resolves
    ``system`` when needed, loads the effective catalog, and stores that catalog
    for :func:`tr`. It does not refresh widgets; callers that respond to a
    user-facing language change should use :func:`set_application_language`.

    Parameters
    ----------
    app : QCoreApplication
        Active Qt application.
    language_code : str
        Stored language code. ``system`` resolves through ``QLocale``.

    Returns
    -------
    bool
        ``True`` when a catalog-backed translator was installed.
    """
    global _installed_catalog, _installed_translator

    if _installed_translator is not None:
        app.removeTranslator(_installed_translator)
        _installed_translator = None
        _installed_catalog = {}

    language_code = resolved_language(language_code)
    if language_code == "":
        return False

    catalog = load_effective_catalog(language_code)
    if not catalog:
        return False

    translator = JsonTranslator(catalog)
    app.installTranslator(translator)
    _installed_translator = translator
    _installed_catalog = catalog
    return True


def set_application_language(app: QCoreApplication, language_code: str) -> bool:
    """Install a language and process pending Qt language-change events.

    This is the high-level live-switching entry point. It installs the
    catalog-backed translator, lets Qt process pending events, and then walks
    open top-level widgets looking for ``retranslate_ui()`` hooks. The hook
    contract is display-only: widgets refresh text while preserving selections,
    stable item data, settings values, object identities, and undo payloads.

    Parameters
    ----------
    app : QCoreApplication
        Active Qt application.
    language_code : str
        Language code selected by the user.

    Returns
    -------
    bool
        ``True`` when a catalog-backed translator was installed.
    """
    installed = install_language(app, language_code)
    app.processEvents()
    retranslate_application(app)
    return installed


def install_language_from_settings(app: QCoreApplication, settings: Any) -> bool:
    """Install the language selected in a ``Settings`` object.

    This bridges Foundry's persisted editor preference into the live Qt
    translator. The setting remains a stable locale code such as ``en`` or
    ``system``; only widget display text is refreshed through
    :func:`set_application_language`.

    Parameters
    ----------
    app : QCoreApplication
        Active Qt application.
    settings : object
        Settings-like object exposing ``value("editor/language")``.

    Returns
    -------
    bool
        ``True`` when a catalog-backed translator was installed.
    """
    return set_application_language(app, settings.value("editor/language"))


def tr(context: str, key: str, fallback: str | None = None) -> str:
    """Translate one display string by stable catalog key.

    ``tr`` reads the effective catalog installed by :func:`install_language`.
    It never mutates catalogs and never returns a
    translated value for identity-sensitive code. Use it only at UI display
    boundaries such as labels, table headers, status text, prompts, and
    tooltips.

    Parameters
    ----------
    context : str
        Short catalog context such as ``foundry.settings``.
    key : str
        Stable code-facing translation id, not display prose or an English
        source sentence.
    fallback : str | None, optional
        English display text used when the key has not reached ``en.json`` yet.

    Returns
    -------
    str
        Localized display text. Missing target-locale entries fall back to the
        English catalog and then to ``fallback`` so raw ids are not shown to
        users during incremental migration.

    Notes
    -----
    The lookup reads the installed effective catalog first and the cached
    English catalog second. This mirrors the bundled/user overlay merge order
    while keeping stable code-facing keys separate from displayed labels.
    """
    translated = _installed_catalog.get(context, {}).get(key, "")
    if translated:
        return translated

    english = english_catalog().get(context, {}).get(key, "")
    if english:
        return english

    return fallback if fallback is not None else key


def translation_key(source_text: str) -> str:
    """Generate a stable catalog key for Foundry display text.

    Known data labels use their authored short default key. Other labels use a
    deterministic slug capped at 63 characters. The helper is used only for
    data/source labels whose displayed text is derived from a stable English
    record. Authored UI strings should pass their short semantic key directly
    to :func:`tr` instead of deriving one from display prose.
    The generated key is a catalog lookup id only; it must not become ROM data,
    an SMB3 parser symbol, a settings value, or a user-visible label.

    Parameters
    ----------
    source_text : str
        Stable English source label that needs a code-facing translation key.

    Returns
    -------
    str
        Catalog key used for stable-key lookup.
    """
    if source_text in _SOURCE_TEXT_DEFAULT_KEYS:
        return _SOURCE_TEXT_DEFAULT_KEYS[source_text]

    key = _KEY_PART_RE.sub("_", source_text.casefold()).strip("_") or "blank"
    return key[:63].rstrip("_") or "blank"


def tr_data_name(context: str, source_text: str) -> str:
    """Translate a stable data label for display only.

    Foundry's data files remain the English source of truth for tiles, object
    sets, enemies, level objects, music themes, and graphics sets. This helper
    maps those stable names to keyed catalog entries only when populating Qt
    labels, dropdowns, search rows, or tooltips.

    Parameters
    ----------
    context : str
        Data-label context such as ``Tile`` or ``ObjectSet``.
    source_text : str
        Stable English data label used by the parser, renderer, or lookup
        table.

    Returns
    -------
    str
        Translated display label.

    Notes
    -----
    This helper marks the boundary where ROM/parser names become user-facing
    text. Callers must keep using the original English value for lookups,
    serialization, undo payloads, and object identity.
    """
    key_context = DATA_NAME_KEY_CONTEXTS.get(context)
    if key_context is None:
        return tr(context, translation_key(source_text), source_text)

    return tr(key_context, translation_key(source_text), source_text)


def tr_object_name(level_object: Any) -> str:
    """Translate an in-level object or enemy name for display only.

    The object instance remains the identity. Callers should put the returned
    string into labels, rows, tooltips, or command text only; ``Qt.UserRole``
    data, object lookup, serialization, and undo payloads must keep the object
    itself or its stable English attributes.
    The helper chooses the Foundry data-name catalog based on whether the
    object is an enemy item or a level object, then delegates to
    :func:`tr_data_name` for display lookup.
    Object lists, tooltips, and command text can refresh this label during
    ``retranslate_ui`` while model ownership and undo/replay state keep the
    original object.

    Parameters
    ----------
    level_object : object
        Object with a stable English ``name`` attribute.

    Returns
    -------
    str
        Translated display label, or the original name when no catalog entry
        exists.
    """
    name = str(getattr(level_object, "name", level_object))
    context = "EnemyItem" if level_object.__class__.__name__ == "EnemyItem" else "LevelObject"
    return tr_data_name(context, name)


def retranslate_application(app: QCoreApplication) -> None:
    """Refresh open widgets that expose a ``retranslate_ui`` hook.

    The traversal starts at every top-level widget and delegates the actual
    update to widgets that choose to expose ``retranslate_ui``. This keeps live
    language switching incremental and avoids reconstructing editor windows
    with active selections or pending edits.

    Parameters
    ----------
    app : QCoreApplication
        Active Qt application. GUI applications expose ``topLevelWidgets``;
        non-GUI startup paths simply have nothing to refresh.
    """
    top_level_widgets = getattr(app, "topLevelWidgets", None)
    if not callable(top_level_widgets):
        return

    visited: set[int] = set()
    for widget in top_level_widgets():
        retranslate_widget_tree(widget, visited)


def retranslate_widget_tree(widget: Any, visited: set[int] | None = None) -> None:
    """Call ``retranslate_ui`` on one widget tree after a language change.

    ``visited`` prevents repeated refreshes when Qt ownership graphs expose the
    same object through multiple paths. Hooks are expected to be idempotent and
    to refresh display text from stable backing data rather than from
    previously translated strings.
    The active translator has already changed before this traversal starts, so
    each hook can rebuild Qt labels from catalog-backed helpers and stable
    model data.

    Parameters
    ----------
    widget : object
        Qt object or widget to refresh.
    visited : set[int] | None, optional
        Object ids already refreshed during one traversal.

    Notes
    -----
    The traversal is display-boundary work only. A ``retranslate_ui`` hook may
    relabel controls, menus, rows, and tooltips, but it must preserve stable
    ``Qt.UserRole`` payloads, selected object identities, settings keys,
    serialized values, and undo/replay data.
    """
    if visited is None:
        visited = set()

    object_id = id(widget)
    if object_id in visited:
        return
    visited.add(object_id)

    retranslate = getattr(widget, "retranslate_ui", None)
    if callable(retranslate):
        retranslate()

    children = getattr(widget, "children", None)
    if not callable(children):
        return

    for child in children():
        retranslate_widget_tree(child, visited)
