Localization Architecture
=========================

Problem and Context
-------------------

Foundry and Scribe now treat localization as a display-boundary subsystem. The
editor keeps ROM data, object names, settings keys, command payloads,
undo/replay state, parser identifiers, and source ``.dat`` records stable in
English. Translated text is applied only where users see labels, menus,
tooltips, status text, dialogs, option names, and data-backed display names.

The main risk in this subsystem is accidental identity drift: a translated
label must never become the value used for lookup, persistence, command replay,
or ROM serialization. The second risk is catalog drift: supported locales must
share the same key set, preserve placeholders and markup, and use keys that are
maintainable for programmers rather than generated from whole English
sentences.

Goals
-----

- Keep English as the canonical internal identity and runtime fallback.
- Load every visible locale, including English, from JSON catalogs under
  ``data/translations``.
- Allow users to import, export, and edit translation overlays from a
  user-writable catalog directory without modifying bundled catalogs.
- Use short, semantic, code-facing keys for new and migrated strings.
- Keep long help text, rich text, error messages, and data-backed names
  catalog-backed without making their keys unreadable.
- Support live language switching through ``retranslate_ui()`` hooks on open
  windows and high-traffic child widgets.
- Audit coverage, key quality, structural tokens, regional usefulness, and
  target-locale wording before a localization change is considered complete.

Current State
-------------

Localization is a JSON-catalog subsystem shared by Foundry and Scribe. The
runtime supports built-in locales, user overlay catalogs, custom locale codes,
live language switching, data-backed display names, and deterministic audit
coverage. The Translation Manager is the supported in-app tool for exporting a
complete effective catalog, importing JSON catalogs, editing translations, and
saving partial user overrides.

The implementation is intentionally conservative: translations are display
values only. Stable English identifiers continue to own data loading, object
lookup, settings persistence, command replay, undo/redo, parser input, and ROM
serialization.

Runtime Layers
--------------

The runtime boundary lives in :mod:`foundry.gui.localization`.

``tr(context, key, fallback)``
    Looks up a stable code-facing key in the active catalog, then falls back to
    ``en.json``, and finally to the explicit fallback. All general UI strings
    use this helper; the key is catalog identity and the fallback is display
    text only.

``tr_data_name(context, source_text)``
    Translates data-backed display names through keyed ``data.*`` contexts.
    Internal ``.name`` values and data records stay English and stable.

``set_application_language(app, language_code)``
    Installs the selected JSON translator and refreshes top-level widgets that
    expose ``retranslate_ui()``.

``load_effective_catalog(language_code)``
    Builds the runtime catalog by merging bundled English, the English user
    overlay, the bundled selected-locale catalog, and the selected-locale user
    overlay, in that order. Blank normal translation values are ignored so the
    UI falls back to bundled or English text instead of showing empty labels.

``save_user_catalog(language_code, catalog)``
    Writes a partial user overlay to the writable translation directory. The
    UI uses this for imported or table-edited translations and never writes to
    ``data/translations``.

``translation_catalog_paths(language_code)``
    Reports the bundled and user overlay paths for a concrete locale code.
    The bundled path may be missing for custom user locales.

``available_languages()`` and ``language_display_name(language_code)``
    Discover built-in, bundled, and user-provided locale codes for settings
    dropdowns. Known language names come from the ``lang`` catalog context;
    custom locales may provide ``"_meta": {"display_name": "..."}``.

``validate_catalog(language_code, catalog)``
    Performs structural validation before import or save. It accepts partial
    overlays, but reports invalid JSON shape, non-string keys or values, and
    token, placeholder, HTML, or accelerator mismatches against the English
    baseline.

API Decision Guide
------------------

Localization call sites should choose the narrowest helper that matches the
display boundary:

``tr(...)``
    Use for new UI labels, tooltips, button text, table headers, status text,
    prompts, long help text, and migrated strings. The key must be stable and
    code-facing, while the English display value lives in ``en.json``.

``tr_data_name(...)``
    Use when an English name from a stable data source becomes visible to the
    user. The source text remains the lookup or parser identity. Only the
    rendered label changes.

``tr_object_name(...)``
    Use for level objects and enemy/item instances that expose a stable
    English ``name``. Do not replace the object's ``name`` attribute with the
    translated display text.

``translation_key(...)``
    Use when a stable English data/source label needs to resolve to its keyed
    catalog entry and no authored UI key exists. New UI strings should pass
    short semantic keys directly to ``tr(...)``.

``set_application_language(...)``
    Use when a user-facing language choice changes. It installs the selected
    catalog-backed translator, processes pending Qt events, and recursively
    refreshes open widgets that expose ``retranslate_ui()``.

Live Retranslation Contract
---------------------------

Live language switching is an application-level behavior, not a per-dialog
rebuild. ``set_application_language`` calls ``retranslate_application``, which
walks top-level widgets and their children. Any widget that can stay open after
a language change must expose ``retranslate_ui()`` when it owns visible text.

``retranslate_ui()`` implementations should:

- update labels, button text, titles, group titles, menu/action text, table
  headers, combo-box display text, tooltips, status text, and tab text
- be idempotent, no-argument methods that are safe to call while a parent
  window is refreshing child widgets
- preserve current selections, numeric values, stable ``Qt.UserRole`` data,
  settings values, object identities, and command payloads
- rebuild visible rows from stable backing data rather than from previously
  translated strings
- refresh model headers, status/footer labels, and data-backed labels when
  those values are visible in open tables, lists, or inspectors
- keep transient dialogs simple when appropriate; dialogs that are recreated
  after language changes may pick up the current language at construction time

The main Foundry window refreshes its high-traffic child surfaces explicitly:
menus, context menus, object dropdown/list/toolbox surfaces, level/world views,
spinner labels, jump list rows, size bars, and status/footer text. Scribe
surfaces use the same convention for menus, settings, world info, overview
status, and tool-window tables.

Catalog Shape
-------------

Every supported locale has a JSON file under ``data/translations``. English is
not implicit; ``en.json`` is the baseline catalog whose values are the source
English display strings. Target locale catalogs must have the same
``(context, key)`` pairs as English.

Users may add partial override catalogs in the app-data translation directory.
Those files use the same ``{context: {key: value}}`` shape and may include a
reserved ``"_meta"`` context with ``"display_name"`` for custom language names.
Metadata is ignored by normal translation lookup. ``"_meta"`` is merged
directly because it describes the catalog file rather than a translated UI
string; keep metadata values non-blank when they should appear in selectors.
User catalogs are overlays: they may contain only changed strings, and missing
or blank entries in normal contexts fall back through the bundled
selected-locale catalog, any English user overlay, and then bundled English.
User overlays for ``en`` are intentionally part of every effective catalog
because English remains the display baseline.

Language Discovery
------------------

Language settings store stable locale codes, never translated display names.
Known locale codes are listed first, then additional bundled or user-provided
catalog stems are sorted after them. ``system`` is available in settings as an
automatic choice, but the Translation Manager omits it because user catalog
files are saved by concrete locale code.

Locale resolution normalizes hyphens to underscores and prefers exact catalog
matches. When ``system`` is selected, the platform locale is resolved to the
nearest supported catalog: Spanish falls back through exact matches,
``es_419``, then ``es``; Portuguese falls back through exact matches, then
``pt_BR``; German, French, Italian, and English fall back to their base
catalogs. Custom user catalogs can be selected directly when their JSON file
stem appears in the user translation directory.

The user translation directory is discovered in this order:

1. the ``FOUNDRY_USER_TRANSLATION_DIR`` environment variable, when set
2. the platform application-data ``translations`` directory
3. the ``~/.smb3-foundry/translations`` compatibility fallback for older user
   catalog locations

Stable contexts are short and grouped by workflow, for example:

- ``lang`` for language names.
- ``foundry.main`` for main-window actions and help text.
- ``foundry.settings`` for settings labels and explanations.
- ``foundry.game_properties`` for ``data/game_properties.ini`` display text.
- ``scribe.main`` and ``scribe.tool_window`` for Scribe surfaces.
- ``data.level_object``, ``data.enemy_item``, ``data.stock_level``, and
  similar ``data.*`` contexts for data-backed names.

Key Naming Rules
----------------

Translation keys should describe the programming concept. They should not
mirror the whole English sentence.

Use these patterns:

- ``error.rom_path_missing`` for error messages.
- ``warning.rom_external_change`` for warnings.
- ``prompt.restore_auto_save_rom`` for prompts.
- ``help.object_list`` or ``help.jump_list`` for long HTML or ``WhatsThis``
  content.
- ``credit.hukka_workshop`` for About-dialog credit lines.
- ``command.set_next_area_object_addr`` for undo/redo command text.
- ``object_set.0xa_ship`` when a visible label intentionally carries an
  encoded hex identity.
- ``w8_bowser_castle_top_left`` or ``variant_1_platform_wire`` when a data
  label has important world or variant identity.

Avoid these patterns:

- Keys derived from HTML tags, such as ``a_href_*``, ``b_*``, ``br_*``, or
  ``p_*``.
- Long generated sentence keys.
- Placeholder-name soup such as ``world_number_world_number``.
- Accidental numeric prefixes. Numeric or hex-like prefixes must either be
  explicitly meaningful, such as ``object_set.0xf_spade_bonus``, or rewritten
  as prose, such as ``two_way_bullet_shooter``.

Data-Backed Names
-----------------

Data files remain English and stable. The localization audit extracts display
names from stable data sources and requires matching entries in keyed
``data.*`` contexts. UI surfaces translate those names only when rendering
labels, dropdown rows, tooltips, tables, and status text.

When a data label begins with a number or letter that represents game data,
the key should encode that meaning deliberately. Object-set labels use
``object_set.0x*`` keys because the visible leading value is the object-set
id. Directional map names use compass words, such as
``east_west_road_water``. Plain variants use ``variant_*`` keys when the
source data distinguishes them by variant number rather than by a better
domain name.

Quality Gates
-------------

Localization changes should pass the repository's local QA checks before a PR
is reviewed. Those checks cover catalog parity, data-name coverage,
display-option coverage, token preservation, sibling-locale key parity,
unwrapped UI literals, raw display collections, and refresh blind spots.

Key-quality review keeps stable keys maintainable. It checks for long keys,
markup-derived keys, placeholder-derived keys, generated sentence-like keys,
and numeric or hex-like prefixes that need adjudication. Current catalogs have
zero key-quality findings and keep keys below the 64-character limit.

Target-locale quality review catches deterministic wording issues such as
generated placeholders, English residue, mixed-language fragments, official
enemy-name mismatches, and strings that need contextual review.

User Catalog Editing
--------------------

Foundry settings exposes a translation manager next to the language dropdown.
The dialog is a catalog editor, not a source-data editor. It uses a Qt
model/view table backed by the same effective catalog that runtime translation
uses, and it writes only partial user overlays. The bundled files under
``data/translations`` remain read-only from the UI.

The settings dialog passes its current stable locale code into the manager.
The manager omits ``system`` from its own locale selector because user catalogs
are saved by concrete locale code. Imported filenames become locale codes, so
``custom.json`` creates or updates the ``custom`` user catalog. If that catalog
contains ``"_meta": {"display_name": "..."}``, the display name appears in
language selectors after language discovery refreshes. After import, save, or
revert, the manager emits ``catalog_changed`` so the settings dialog can
refresh available languages and reinstall the selected language when the active
locale changed.

The table shows one row per English baseline entry:

``Context``
    The catalog namespace, such as ``foundry.settings`` or
    ``data.level_object``.

``Key``
    The stable code-facing translation key.

``English``
    The English baseline value from ``en.json``.

``Translation``
    The active selected-locale value after bundled and user catalogs are
    merged. This is the only editable column.

``Status``
    A deterministic state derived from the row value and validation issues.

The manager provides search, context filtering, status filtering, sortable
columns, adjustable column widths, a fit-columns action, and a detail editor
for long strings or HTML. The detail editor is the preferred place to edit
long help text because it keeps the English source, active translation, and
validation messages visible together.

The table model deliberately separates source identity from editing state:
context, key, English, and status are read-only reference columns. Only the
translation value is editable. Filtering and sorting operate on model rows,
while saves serialize only dirty translation values into the user overlay.
Column resizing is a display preference only; it never changes catalog data.

Status values mean:

``OK``
    The active translation has no structural validation errors.

``Unchanged English``
    The active translation equals the English baseline. This can be
    intentional, especially for technical terms, but it is distinct from a
    missing selected-locale entry.

``Missing``
    The selected non-English locale has no non-blank bundled or user entry for
    the key, so the visible value is falling back to English.

``Edited``
    The row has an unsaved in-memory user override.

``Blank`` or ``Token issue``
    The edited value has a validation warning or error. Blank overlay values
    are ignored at runtime, while token issues block saving because they would
    break placeholders, percent tokens, HTML tags, or keyboard accelerators.

Import, export, save, and revert follow the same overlay model:

- Import validates a JSON catalog and writes it to the user translation
  directory under the file stem locale code.
- Export writes the effective catalog for the selected locale, including
  fallback values, so translators can start from a complete file.
- Save writes only dirty rows edited in the dialog into the selected locale's
  user overlay. Blank edited values remove the key from that overlay.
- Revert removes the selected locale's user overlay and falls back to bundled
  or English text.

Validation is intentionally structural and deterministic. Imported or edited
catalogs must keep placeholders, percent tokens, HTML tags, and keyboard
accelerators compatible with the English baseline before they can be saved.
The root must be an object, each context must be an object, and normal
translation keys and values must be strings. ``"_meta"`` is allowed for catalog
metadata and is skipped by placeholder/token checks. Warnings such as blank or
unchanged-English text are allowed because partial overlays are useful during
translation work. Runtime identities remain English and stable: locale codes
are still stored in settings, and translated labels are never promoted into
ROM data, object lookup, parser identifiers, undo/replay, or persistence
contracts.

Control Flow
------------

Startup and language changes follow one path:

1. Settings provide either ``system`` or a stable concrete locale code.
2. The locale code is resolved to a catalog, including user catalog discovery.
3. ``install_language`` installs a JSON-backed Qt translator and records the
   effective catalog used by ``tr``.
4. ``set_application_language`` processes pending Qt events and calls
   ``retranslate_application``.
5. Open widgets refresh themselves through ``retranslate_ui()`` without
   changing backing state.

Translation Manager edits follow a separate overlay path:

1. Import reads a JSON file, validates it, and writes it to the user catalog
   directory using the file stem as the locale code.
2. Table edits update in-memory row state and validation messages immediately.
3. Save writes only dirty, non-blank translation values into the selected
   locale's user overlay; blank edited values remove the override key.
4. Revert deletes the selected locale's user overlay.
5. Import, save, and revert emit ``catalog_changed`` so settings can refresh
   language choices and reinstall the active catalog when needed.

Major Decisions
---------------

- Catalogs are JSON dictionaries rather than Qt ``.qm`` files so bundled and
  user-edited catalogs can share one validation and audit path.
- English is a real catalog-backed locale. This keeps fallback behavior
  testable and lets English user overlays participate in every effective
  catalog.
- User catalogs are partial overlays, not replacements. This makes community
  translation work incremental and keeps missing strings safe.
- Blank normal overlay values are treated as absent at runtime. The UI should
  fall back rather than render empty labels.
- ``"_meta"`` is reserved for catalog metadata and is not part of normal
  translation lookup.
- Stable keys are preferred over literal English catalog indexes. Legacy
  ``tr(...)`` remains only as a migration bridge.
- Live switching uses ``retranslate_ui()`` hooks instead of reconstructing
  windows. This preserves selections, stable item data, and editor state.

Translator Workflow
-------------------

For bundled locales, contributors normally work in the repository:

1. Add or migrate UI strings with stable keys and English values in
   ``data/translations/en.json``.
2. Add matching keys to every supported target catalog.
3. Run local catalog-parity and key-quality checks for ``en`` and all target
   locales.
4. Run local target-locale quality checks for changed catalogs.
5. Exercise live switching on the UI surfaces touched by the change.

For user or community catalogs, translators can work from the Translation
Manager:

1. Open Foundry settings and use the button next to the language dropdown.
2. Export the effective catalog for a complete starting JSON file.
3. Edit in the dialog or import a JSON file named for the target locale code.
4. Use ``"_meta": {"display_name": "..."}`` for custom locale display names.
5. Save the overlay and switch languages to verify the result live.

User overlays are intentionally partial. They can override one string, a whole
context, or a complete locale. Missing entries fall back through the effective
catalog chain, and blank values are ignored during runtime merge so they do not
render empty labels.

Maintainer Checklist
--------------------

When changing localization plumbing or the Translation Manager:

- keep ``en.json`` and every supported locale in exact key parity
- add new manager UI strings under ``foundry.translation_manager``
- preserve the bundled English -> English user overlay -> bundled selected
  locale -> selected user overlay merge order
- keep missing and unchanged-English statuses distinct
- keep only translation values editable in the manager
- keep user catalog locale codes in item data and settings values
- verify import, export, save, revert, filtering, validation, and live refresh
  with tests
- run local catalog, key-quality, and target-locale quality checks for every
  supported locale touched by the change
- run Sphinx validation when localization docs or API routes change
- update this page when user-facing catalog workflows or invariants change

Native-Quality Review
---------------------

Passing local QA checks makes a locale a production candidate. It does not make
the locale native-reviewed. Human-style review should group findings by UI
surface and classify them as accepted, needs rewrite, needs context, official
name verified, or domain term intentionally preserved.

Read This Next
--------------

- Start with :mod:`foundry.gui.localization` for runtime catalog loading,
  fallback, and live refresh.
- Use :class:`foundry.gui.dialogs.TranslationManagerDialog.TranslationManagerDialog`
  for the user-overlay catalog editor.
- Use :class:`foundry.gui.dialogs.SettingsDialog.SettingsDialog` for the
  language dropdown and Translation Manager entry point.
- Read :doc:`/user_guide/foundry_manual` for the user-facing settings path to
  the Translation Manager.
- Use :doc:`foundry_gui_architecture` for the surrounding Qt ownership model.
- Use :doc:`scribe_gui_architecture` when localization touches Scribe menus,
  world info, overview status, or tool-window tables.
