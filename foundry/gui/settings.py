"""Persisted editor settings and the small enums that describe them.

This module defines Foundry's persisted settings vocabulary, default values,
and the ``Settings`` wrapper that turns raw ``QSettings`` entries into stable
editor-facing policy. It is the bridge between Qt persistence, startup/update
workflow choices, and view-level rendering preferences.

See Also
--------
foundry.features.online_updates
    Consumes release-channel and ignored-version settings during update checks.
foundry.gui.MainWindow
    Reads persisted editor preferences while loading ROMs and launching tools.
"""

from typing import Callable

import qdarkstyle
from PySide6.QtCore import QSettings

RESIZE_LEFT_CLICK = "LMB"
RESIZE_RIGHT_CLICK = "RMB"

GUI_STYLE: dict[str, Callable] = {
    "RETRO": lambda: "",  # noqa
    "DRACULA": qdarkstyle.load_stylesheet_pyside6,
}


class ASMLoadingBehavior:
    """Name the supported policies for loading ASM companion files.

    These constants are stored in ``Settings`` and used by startup and ROM-load
    workflows to decide whether Foundry should ignore, prompt for, or
    automatically load available ASM metadata.

    Attributes
    ----------
    ASK_IF_NEEDED : int
        Prompt when ASM data would materially affect the editor state.
    DONT_ASK : int
        Never prompt or auto-load ASM data.
    LOAD_IF_AVAILABLE : int
        Automatically load ASM data when it is present.
    """

    DONT_ASK = 0
    ASK_IF_NEEDED = 1
    LOAD_IF_AVAILABLE = 2


class ReleaseChannel:
    """Name the supported update channels for Foundry releases.

    ``Settings`` stores one of these values to control whether update checks in
    the Qt UI are disabled or target stable or nightly builds. These constants
    are part of the contract between persisted preferences, startup update
    checks, and the manual update dialog, so the rest of the UI can reason
    about release policy without hard-coding string values.

    Attributes
    ----------
    NIGHTLY : int
        Follow nightly builds, including development snapshots.
    NONE : int
        Disable update checks entirely.
    STABLE : int
        Follow stable releases only.

    See Also
    --------
    Settings
        Persists the selected release channel and migrates older update
        preferences into this policy.
    """

    NONE = 0
    STABLE = 1
    NIGHTLY = 2


class LevelPreviewType:
    """Name the supported level-preview presentation modes.

    The level selector and world-view preview features read this setting to
    decide whether previews are disabled, shown in tooltips, or rendered in a
    dedicated widget. That makes this class the shared vocabulary for preview
    presentation across several editor surfaces, rather than a one-off flag for
    a single dialog.

    Attributes
    ----------
    NONE : int
        Disable level previews.
    TOOLTIP : int
        Show previews in hover tooltips and similar transient UI surfaces.
    WIDGET : int
        Show previews in a dedicated embedded widget.

    See Also
    --------
    Settings
        Stores the active preview mode for selector and world-view workflows.
    """

    NONE = 0
    TOOLTIP = 1
    WIDGET = 2


# TODO Make into an enum?
SETTINGS: dict[str, str | int | float | bool] = dict()
SETTINGS["editor/instaplay_emulator"] = "fceux"
SETTINGS["editor/instaplay_arguments"] = "%f"
SETTINGS["editor/instaplay_skip_title_screen"] = True

SETTINGS["editor/default_powerup"] = 0
SETTINGS["editor/powerup_starman"] = False

SETTINGS["editor/object_scroll_enabled"] = False

SETTINGS["editor/resize_mode"] = RESIZE_LEFT_CLICK
SETTINGS["editor/gui_style"] = ""  # initially blank, since we can't call load_stylesheet until the app is started
SETTINGS["editor/level_preview_type"] = LevelPreviewType.WIDGET

SETTINGS["editor/default_dir"] = "User"
SETTINGS["editor/default_dir_path"] = ""
SETTINGS["editor/custom_default_dir_path"] = ""

SETTINGS["editor/show_block_item_in_toolbar"] = True
SETTINGS["editor/ask_for_level_management"] = True
SETTINGS["editor/auto_save_enabled"] = True
SETTINGS["editor/asm_loading_behavior"] = ASMLoadingBehavior.ASK_IF_NEEDED

SETTINGS["editor/remember_last_level"] = False
SETTINGS["editor/remember_last_level_path"] = ""
SETTINGS["editor/remember_last_level_object_set"] = 0
SETTINGS["editor/remember_last_level_lvl_address"] = 0
SETTINGS["editor/remember_last_level_enemy_address"] = 0
SETTINGS["editor/remember_last_level_world_number"] = 1

SETTINGS["editor/monitor_rom_for_changes"] = True

SETTINGS["editor/asked_for_startup"] = False
SETTINGS["editor/release_channel"] = ReleaseChannel.NIGHTLY
SETTINGS["editor/version_to_ignore"] = ""

SETTINGS["editor/settings_version"] = 0

SETTINGS["level_view/draw_mario"] = True
SETTINGS["level_view/draw_jumps"] = False
SETTINGS["level_view/draw_grid"] = False
SETTINGS["level_view/draw_grid_coordinates"] = False
SETTINGS["level_view/draw_expansion"] = False
SETTINGS["level_view/draw_jump_on_objects"] = True
SETTINGS["level_view/draw_items_in_blocks"] = True
SETTINGS["level_view/draw_invisible_items"] = True
SETTINGS["level_view/draw_autoscroll"] = False
SETTINGS["level_view/block_transparency"] = True
SETTINGS["level_view/block_animation"] = True
SETTINGS["level_view/special_background"] = True
SETTINGS["level_view/object_tooltip_enabled"] = True
SETTINGS["level_view/last_zoom_factor"] = 1.0


_settings: dict[str, str | int | float | bool] = {
    "world_view/show_grid": False,
    "world_view/show_border": False,
    "world_view/animated_tiles": True,
    "world_view/show_level_pointers": True,
    "world_view/show_level_previews": False,
    "world_view/show_sprites": True,
    "world_view/show_start_position": False,
    "world_view/show_airship_paths": 0,
    "world_view/show_pipes": False,
    "world_view/show_locks": False,
}
_settings.update(SETTINGS)


class Settings(QSettings):
    """Persist and migrate Foundry's editor settings.

    ``Settings`` wraps Qt's key-value store with Foundry's default values,
    type restoration, and versioned migrations. It is the boundary between raw
    persisted settings data and the strongly expected values used by editor,
    viewer, and update workflows.

    Parameters
    ----------
    organization : str, optional
        Qt settings organization name.
    application : str, optional
        Qt settings application name.

    Notes
    -----
    This class is the persistence-oriented configuration service for Foundry.
    It centralizes defaults, type coercion, and settings-version upgrades so
    the rest of the application can consume stable configuration values instead
    of raw ``QSettings`` strings.
    """

    def __init__(self, organization="mchlnix", application="default"):
        """Initialize persisted settings, defaults, and migrations.

        Construction hydrates missing keys from Foundry's defaults and then
        applies any versioned migrations required by the selected application.

        Parameters
        ----------
        organization : str, optional
            Qt settings organization name.
        application : str, optional
            Qt settings application name.
        """
        super(Settings, self).__init__(organization, application)

        for key, default_value in _settings.items():
            if self.value(key) is None or self.is_default:
                self.setValue(key, default_value)

        self.sync()

        self.update_by_version()

    @property
    def is_default(self):
        """Whether this instance targets the default placeholder store.

        The placeholder store is used when callers want default values and type
        information during startup, migration planning, or settings-schema
        queries without writing to the user's real settings backend or
        triggering persistence side effects. ``setValue`` and ``sync`` both
        branch on this property to keep those read-mostly workflows from
        mutating disk-backed settings state.

        Returns
        -------
        bool
            ``True`` when the settings object uses the default organization and
            application names.
        """
        return self.organizationName() == "mchlnix" and self.applicationName() == "default"

    def value(self, key: str, default_value=None, type_=None):
        """Read a setting with Foundry's type restoration rules.

        This wrapper turns Qt's loosely typed storage back into the concrete
        booleans, integers, floats, and strings that editor workflows expect.

        Parameters
        ----------
        key : str
            Settings key to read.
        default_value : object, optional
            Fallback value when the key has not been stored.
        type_ : type, optional
            Explicit type coercion to apply to the stored value.

        Returns
        -------
        object
            Stored value coerced to the expected Python type when possible.
        """
        if key in _settings and type_ is None:
            type_ = type(_settings[key])

        returned_value = super(Settings, self).value(key, default_value)

        if returned_value is None:
            return returned_value
        elif type_ is bool and isinstance(returned_value, str):
            # boolean values loaded from disk are returned as strings for some reason
            return returned_value.lower() == "true"
        elif type_ is None:
            return returned_value
        else:
            return type_(returned_value)

    def setValue(self, key: str, value):
        """Store a setting value in the underlying Qt store.

        Writing goes through this override so callers keep using the same API
        that ``value``, startup hydration, and versioned migration code expect
        while updating Foundry's settings store. The same call path is used
        when startup code seeds missing defaults, when settings dialogs commit
        user edits, and when migrations rewrite legacy keys, so every persisted
        change reaches Qt through one normalization boundary before a later
        ``sync`` flushes it to disk.

        Parameters
        ----------
        key : str
            Settings key to update.
        value : object
            Value to persist.

        Returns
        -------
        object
            Result returned by ``QSettings.setValue``.
        """
        return super(Settings, self).setValue(key, value)

    def sync(self):
        """Flush pending settings to disk when a real store is in use.

        The default placeholder instance never writes to disk, which lets the
        rest of the settings code reuse the same methods for defaults lookup,
        migration planning, and type probing. Real ``foundry`` settings
        instances accumulate writes through ``setValue`` while startup code
        seeds defaults, settings dialogs commit edits, and migrations rewrite
        legacy keys. This method is the durability boundary for that staged
        work: placeholder stores stop here, while real stores hand the pending
        changes to Qt so later sessions observe normalized keys and upgraded
        values.

        Returns
        -------
        object | None
            Result from ``QSettings.sync``, or ``None`` for the default store.
        """
        if self.is_default:
            return None

        return super(Settings, self).sync()

    def update_by_version(self):
        """Run application-specific settings migrations."""
        if self.applicationName() == "foundry":
            self._update_foundry_by_version()

    def _update_foundry_by_version(self):
        """Apply incremental migrations for persisted Foundry settings."""
        while True:
            settings_version = self.value("editor/settings_version")

            if settings_version == 0:
                self.setValue("world_view/show_level_pointers", True)

                self.setValue("editor/settings_version", settings_version + 1)
                continue

            if settings_version == 1:
                self.setValue("editor/settings_version", settings_version + 1)

                for key in self.allKeys():
                    if " " not in key:
                        continue

                    underscore_key = key.replace(" ", "_")

                    if underscore_key in _settings:
                        self.setValue(underscore_key, self.value(key))

                    self.remove(key)

            if settings_version == 2:
                self.setValue("editor/settings_version", settings_version + 1)

                # preserve the setting to not check updates on startup
                if not self.value("editor/update_on_startup", default_value=True):
                    self.setValue("editor/release_channel", ReleaseChannel.NONE)

                self.remove("editor/update_on_startup")
                continue
            break
