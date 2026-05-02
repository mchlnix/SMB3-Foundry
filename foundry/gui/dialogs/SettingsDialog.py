"""Edit persisted Foundry settings, emulator options, and instaplay defaults.

This module owns the large settings dialog that maps Qt controls onto the
persisted ``Settings`` keys used by startup behavior, mouse and GUI options,
ROM-management prompts, emulator launch configuration, and instaplay defaults.
It is the dialog-layer bridge between individual controls, the shared settings
store, and the derived UI state that must update after each write.

See Also
--------
foundry.gui.settings
    Defines the persisted setting keys and related enums consumed here.
foundry.gui.rom_settings.rom_settings_dialog
    Separate ROM-specific settings dialog that complements these editor-wide
    preferences.
foundry.gui.dialogs.level_selector.LevelSelector
    One of the editor surfaces affected by preview and highlight settings.
"""

from dataclasses import dataclass

from PySide6.QtCore import QCoreApplication, QStandardPaths, Signal, SignalInstance
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from foundry import data_dir, icon
from foundry.game.gfx.drawable import load_from_object_sprite_sheet
from foundry.gui import label_and_widget
from foundry.gui.dialogs.CustomDialog import CustomDialog
from foundry.gui.dialogs.TranslationManagerDialog import TranslationManagerDialog
from foundry.gui.localization import (
    available_languages,
    language_display_name,
    set_application_language,
    tr,
)
from foundry.gui.settings import (
    GUI_STYLE,
    RESIZE_LEFT_CLICK,
    RESIZE_RIGHT_CLICK,
    Settings,
)
from foundry.gui.widgets.HorizontalLine import HorizontalLine
from smb3parse.constants import (
    POWERUP_FIREFLOWER,
    POWERUP_FROG,
    POWERUP_HAMMER,
    POWERUP_MUSHROOM,
    POWERUP_NONE,
    POWERUP_RACCOON,
    POWERUP_TANOOKI,
)


@dataclass
class PowerupEntry:
    """Describe one instaplay Mario power-up option.

    The settings dialog stores a display label, sprite-sheet coordinates, SMB3
    power-up code, and whether the P-Wing flag should be applied when launching
    a level through instaplay.

    Attributes
    ----------
    description : str
        Stable translation key for the power-up dropdown label.
    has_p_wing : bool
        Whether instaplay should set the P-Wing state.
    png_x : int
        Sprite-sheet tile x coordinate for the dropdown icon.
    png_y : int
        Sprite-sheet tile y coordinate for the dropdown icon.
    power_up_code : int
        SMB3 power-up code written to instaplay settings.
    """

    description: str
    png_x: int
    png_y: int
    power_up_code: int
    has_p_wing: bool

    def to_tuple(self):
        """Expose the instaplay metadata in the legacy tuple contract.

        Older dropdown-population and unpacking code still expects the
        five-field tuple order used before ``PowerupEntry`` became a dataclass.
        This helper preserves that boundary so the settings dialog can keep the
        stronger named representation internally while still handing off sprite
        coordinates, SMB3 power-up code, and the P-Wing flag in the order that
        the instaplay UI helpers already consume.

        Returns
        -------
        tuple[str, int, int, int, bool]
            Translation key, icon x, icon y, power-up code, and P-Wing flag.
        """
        return self.description, self.png_x, self.png_y, self.power_up_code, self.has_p_wing

    def __iter__(self):
        """Iterate over the legacy tuple representation.

        The settings dialog still has loops that unpack entries directly while
        building the power-up dropdown and related icon state. Iteration keeps
        those Qt UI-building paths compatible with the dataclass form without
        forcing them to know about field names first.

        Returns
        -------
        iterator
            Iterator over ``to_tuple()``.
        """
        return iter(self.to_tuple())


TR_KEY_CONTEXT = "foundry.settings"

SETTINGS_LABELS = {
    "asm_loading.ask_if_needed": "Ask if needed",
    "asm_loading.dont_ask": "Don't ask",
    "asm_loading.load_if_available": "Load if available",
    "default_dir.custom": "Custom",
    "default_dir.desktop": "Desktop",
    "default_dir.documents": "Documents",
    "default_dir.downloads": "Downloads",
    "default_dir.user": "User",
    "level_preview.dont_show": "Don't show",
    "level_preview.show_on_click": "Show on click",
    "level_preview.show_on_hover": "Show on hover",
    "powerup.big_mario": "Big Mario",
    "powerup.fire_mario": "Fire Mario",
    "powerup.frog_mario": "Frog Mario",
    "powerup.hammer_mario": "Hammer Mario",
    "powerup.raccoon_mario": "Raccoon Mario",
    "powerup.raccoon_mario_p_wing": "Raccoon Mario with P-Wing",
    "powerup.small_mario": "Small Mario",
    "powerup.tanooki_mario": "Tanooki Mario",
    "powerup.tanooki_mario_p_wing": "Tanooki Mario with P-Wing",
    "release_channel.also_nightly": "Also nightly versions",
    "release_channel.dont_check": "Don't check",
    "release_channel.only_stable": "Only stable versions",
    "style.dracula": "Dracula",
    "style.retro": "Retro",
}


def _settings_text(key: str) -> str:
    """Resolve a settings UI string from a stable catalog key.

    The settings dialog uses this helper at display boundaries for row labels,
    grouped options, and shared Scribe/Foundry settings wording. The state
    flow is key-to-display: callers pass stable settings/catalog keys and Qt
    widgets receive only localized labels.

    Parameters
    ----------
    key : str
        Code-facing key inside ``SETTINGS_LABELS`` and the
        ``foundry.settings`` catalog context.

    Returns
    -------
    str
        Localized display text. The returned value is never used as a settings
        key or persisted preference value.
    """
    return tr(TR_KEY_CONTEXT, key, SETTINGS_LABELS[key])


def settings_display_text(key: str) -> str:
    """Resolve shared Foundry/Scribe settings option text.

    Shared settings surfaces call this wrapper so both applications use the
    same catalog context while still storing their own stable settings keys.
    It keeps cross-application option text in one display boundary.

    Parameters
    ----------
    key : str
        Stable settings option key used by Foundry and Scribe settings UIs.

    Returns
    -------
    str
        Localized display label for the option.
    """
    return _settings_text(key)


def gui_style_display_text(style_key: str) -> str:
    """Resolve display text for a persisted GUI style identifier.

    Foundry stores the style key in settings and uses this helper only when
    drawing Qt style radio buttons. The state flow is stored style id to
    localized display label.

    Parameters
    ----------
    style_key : str
        Persisted GUI style identifier such as ``RETRO`` or ``DRACULA``.

    Returns
    -------
    str
        Localized radio-button label. The style identifier remains the stored
        settings value.
    """
    return _settings_text(f"style.{style_key.lower()}")


POWERUPS = [
    PowerupEntry("powerup.small_mario", 32, 53, POWERUP_NONE, False),
    PowerupEntry("powerup.big_mario", 6, 48, POWERUP_MUSHROOM, False),
    PowerupEntry("powerup.raccoon_mario", 57, 53, POWERUP_RACCOON, False),
    PowerupEntry("powerup.fire_mario", 16, 53, POWERUP_FIREFLOWER, False),
    PowerupEntry("powerup.tanooki_mario", 54, 53, POWERUP_TANOOKI, False),
    PowerupEntry("powerup.frog_mario", 56, 53, POWERUP_FROG, False),
    PowerupEntry("powerup.hammer_mario", 58, 53, POWERUP_HAMMER, False),
    # Even though P-Wing can *technically* be combined, it only really works with Raccoon and Tanooki suit
    PowerupEntry("powerup.raccoon_mario_p_wing", 55, 53, POWERUP_RACCOON, True),
    PowerupEntry("powerup.tanooki_mario_p_wing", 55, 53, POWERUP_TANOOKI, True),
]

png = QImage(str(data_dir / "gfx.png"))
png.convertTo(QImage.Format.Format_RGB888)


default_dirs = {
    "User": QStandardPaths.writableLocation(QStandardPaths.StandardLocation.HomeLocation),
    "Desktop": QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation),
    "Documents": QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation),
    "Downloads": QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadLocation),
    "Custom": "",
}
DEFAULT_DIR_LABEL_KEYS = {
    "User": "default_dir.user",
    "Desktop": "default_dir.desktop",
    "Documents": "default_dir.documents",
    "Downloads": "default_dir.downloads",
    "Custom": "default_dir.custom",
}


def default_dir_display_name(default_dir_key: str) -> str:
    """Resolve display text for a default-directory option.

    The dropdown stores a directory key, then maps that key through
    ``default_dirs`` when choosing filesystem paths. The state flow is
    key-to-path for settings and key-to-label for display.

    Parameters
    ----------
    default_dir_key : str
        Stable key in ``default_dirs`` and ``DEFAULT_DIR_LABEL_KEYS``.

    Returns
    -------
    str
        Localized display name for the directory choice. The key, not this
        text, is used to look up the actual filesystem path.
    """
    return _settings_text(DEFAULT_DIR_LABEL_KEYS[default_dir_key])


asm_action_choices = ["asm_loading.dont_ask", "asm_loading.ask_if_needed", "asm_loading.load_if_available"]
release_channel_choices = [
    "release_channel.dont_check",
    "release_channel.only_stable",
    "release_channel.also_nightly",
]
level_preview_choices = ["level_preview.dont_show", "level_preview.show_on_hover", "level_preview.show_on_click"]
LANGUAGE_CHANGE_NOTE = "Language changes apply immediately."


class SettingsDialog(CustomDialog):
    """Edit persisted application and editor preferences.

    The dialog is a live view over ``Settings``. Most controls write their key
    immediately through ``_update_settings``; derived UI, such as the instaplay
    command preview and level-preview refresh signal, is updated after each
    write.

    The language row is also the entry point for localization management. Its
    dropdown stores stable locale codes in item data, while the adjacent
    Translation Manager button edits user catalog overlays. When a catalog or
    language changes, the dialog refreshes labels in place and asks the
    application localization layer to retranslate open widgets.

    Parameters
    ----------
    settings : Settings
        Application settings used to configure the widget behavior.
    parent : object, optional
        Parent Qt widget that owns this object.

    Attributes
    ----------
    _other_settings_box : QGroupBox
        Miscellaneous settings section.
    _release_channel_dropdown : QComboBox
        Startup update-channel selector.
    _restore_last_opened_level_cb : QCheckBox
        Toggle for reopening the last ROM and level on startup.
    _command_arguments_label : QLabel
        Label for the instaplay argument-template field, retained for live
        translation of the emulator section.
    _command_used_label : QLabel
        Label for the read-only instaplay command preview.
    _default_path_label : QLabel
        Label for the default ROM directory selector.
    _emulator_command_label : QLabel
        Label for the emulator executable or command field.
    _powerup_label : QLabel
        Label for the instaplay Mario power-up selector.
    _selected_language : str
        Stable locale code currently selected in the language dropdown. Display
        names are refreshed from catalogs and are not persisted.
    _scroll_cb : QCheckBox
        Toggle for mouse-wheel object type changes.
    _translated_rows : list[tuple[QLabel, str, str, str]]
        Label/control metadata staged for live retranslation. Each tuple keeps
        the label widget, translation key, fallback text, and tooltip text so
        ``retranslate_ui`` can refresh display-only strings without changing
        persisted setting keys or control values.
    _tooltip_cb : QCheckBox
        Toggle for level-view object-name tooltips.
    _when_open_rom_box : QGroupBox
        Settings section applied when opening ROMs.
    ask_for_level_management_cb : QCheckBox
        Toggle for prompting about automatic level management.
    asm_loading_dropdown : QComboBox
        Selector for ASM sidecar loading behavior.
    auto_save_cb : QCheckBox
        Toggle for crash-recovery autosave files.
    command_arguments_input : QLineEdit
        Instaplay command arguments template.
    command_label : QLabel
        Preview of the command used for instaplay.
    default_dir_button : QPushButton
        Button that chooses a custom default ROM directory.
    default_dir_label : QLabel
        Resolved default ROM directory path.
    emulator_command_input : QLineEdit
        Emulator executable or command field.
    emulator_path_button : QPushButton
        Button that chooses an emulator executable.
    gui_box : QGroupBox
        Visual style and selector-display settings section.
    level_highlight_cb : QCheckBox
        Toggle for highlighting level pointers in world-map selectors.
    level_preview_dropdown : QComboBox
        Selector for level preview behavior in the level selector.
    language_dropdown : QComboBox
        Language selector whose row data stores stable locale codes.
    language_changed : SignalInstance
        Emitted with the concrete locale code after the language dropdown
        writes a new setting. The signal is display-only plumbing for live
        retranslation; the locale code remains the stable persisted payload.
    lmb_radio : QRadioButton
        Resize-mode radio button for left-click resizing.
    monitor_rom_cb : QCheckBox
        Toggle for external ROM-change monitoring.
    needs_level_update : SignalInstance
        Needs level update used for dialog UI state.
    path_dropdown : QComboBox
        Selector for predefined or custom default directories.
    powerup_combo_box : QComboBox
        Default Mario power-up selector for instaplay.
    settings : Settings
        Persisted application settings object.
    skip_title_screen_cb : QCheckBox
        Toggle for skipping the title screen during instaplay.
    starman_checkbox : QCheckBox
        Toggle for starting instaplay with Starman active.
    rmb_radio : QRadioButton
        Resize-mode radio button for right-click resizing.
    translation_manager_button : QPushButton
        Button that opens the user catalog overlay editor without modifying
        bundled translation files.
    """

    needs_level_update: SignalInstance = Signal()
    language_changed: SignalInstance = Signal(str)

    def __init__(self, settings: Settings, parent=None):
        """Build controls from persisted settings.

        Construction proceeds in five phases. It first builds the startup and
        mouse controls, then the ROM-opening prompts, then the GUI and
        directory controls, then the emulator and instaplay controls, and
        finally resolves the default-directory display and derived preview state
        by calling ``on_dropdown`` and ``update``. Within each phase the dialog
        follows the same staging rule: create the widget, hydrate it from the
        persisted ``Settings`` value, connect its Qt signal back to
        ``_update_settings`` or a narrower helper, and then place it into the
        section layout that groups related settings together. That setup order
        matters because most controls are write-through editors; by the time
        the dialog becomes visible, every widget already mirrors persisted
        state, every signal path already knows how to persist follow-on edits,
        and the final synchronization pass has rebuilt dependent UI such as the
        emulator command preview and the level-refresh signal consumed by open
        editor surfaces. This keeps one constructor responsible for both
        bootstrapping the settings UI and reattaching all of the live update
        paths that those settings trigger afterward.

        Parameters
        ----------
        settings : Settings
            Application settings used to configure the widget behavior.
        parent : object, optional
            Parent Qt widget that owns this object.
        """
        super(SettingsDialog, self).__init__(parent, tr("SettingsDialog", "settings", "Settings"))

        self.settings = settings
        self._translated_rows: list[tuple[QLabel, str, str, str, str, str]] = []

        # On Startup
        # -----------------------------------------------

        self._startup_box = QGroupBox(tr("SettingsDialog", "start_up", "Start Up"), self)
        layout = QVBoxLayout()
        self._startup_box.setLayout(layout)

        self._release_channel_dropdown = QComboBox()
        self._release_channel_dropdown.addItems([_settings_text(choice) for choice in release_channel_choices])
        self._release_channel_dropdown.setCurrentIndex(self.settings.value("editor/release_channel"))
        self._release_channel_dropdown.currentTextChanged.connect(self._update_settings)

        layout.addLayout(
            self._settings_row(
                "Check for Updates on Startup:",
                self._release_channel_dropdown,
                label_key="check_for_updates_on_startup",
                tooltip_key="help.update_check",
                tooltip_source=(
                    "Checks the Repository for a new version when the Editor is started. Nightly versions are "
                    "untested, but have the latest fixes."
                ),
            )
        )

        self.auto_save_cb = QCheckBox(tr("Common", "enabled", "Enabled"))
        self.auto_save_cb.setChecked(self.settings.value("editor/auto_save_enabled"))
        self.auto_save_cb.stateChanged.connect(self._update_settings)

        layout.addLayout(
            self._settings_row(
                "Ask if Backup should be restored, after crash:",
                self.auto_save_cb,
                label_key="label.restore_crash_backup",
                tooltip_key="help.auto_save_recovery",
                tooltip_source=(
                    "Should the editor keep a copy of the current ROM with unsaved changes, so that if it crashes, "
                    "the ROM and changed level can be restored?"
                ),
            )
        )

        self._restore_last_opened_level_cb = QCheckBox(tr("Common", "enabled", "Enabled"))
        self._restore_last_opened_level_cb.setChecked(self.settings.value("editor/remember_last_level"))
        self._restore_last_opened_level_cb.stateChanged.connect(self._update_settings)

        layout.addLayout(
            self._settings_row(
                "Reopen last opened ROM and level:",
                self._restore_last_opened_level_cb,
                label_key="reopen_last_opened_rom_and_level",
                tooltip_key="help.reopen_last_rom",
                tooltip_source="Should Foundry remember the last opened ROM and level and open them automatically on startup?",
            )
        )

        # Mouse Section
        # -----------------------------------------------

        self._mouse_box = QGroupBox(tr("SettingsDialog", "mouse", "Mouse"), self)
        layout = QVBoxLayout()
        self._mouse_box.setLayout(layout)

        self._scroll_cb = QCheckBox(tr("Common", "enabled", "Enabled"))
        self._scroll_cb.setChecked(self.settings.value("editor/object_scroll_enabled"))
        self._scroll_cb.toggled.connect(self._update_settings)

        layout.addLayout(
            self._settings_row(
                "Scroll objects with mouse wheel:",
                self._scroll_cb,
                label_key="scroll_objects_with_mouse_wheel",
                tooltip_key="help.object_scroll_type",
                tooltip_source="Select an object and scroll up and down to change its type.",
            )
        )

        self._tooltip_cb = QCheckBox(tr("Common", "enabled", "Enabled"))
        self._tooltip_cb.setChecked(self.settings.value("level_view/object_tooltip_enabled"))
        self._tooltip_cb.toggled.connect(self._update_settings)

        layout.addLayout(
            self._settings_row(
                "Show object names on hover:",
                self._tooltip_cb,
                label_key="show_object_names_on_hover",
                tooltip_key="help.object_hover_tooltip",
                tooltip_source=(
                    "When hovering your cursor over an object in a level, its name and position is shown in a "
                    "tooltip."
                ),
            )
        )

        self.lmb_radio = QRadioButton(tr("SettingsDialog", "left_mouse_button", "Left Mouse Button"))
        self.rmb_radio = QRadioButton(tr("SettingsDialog", "right_mouse_button", "Right Mouse Button"))

        self.lmb_radio.setChecked(self.settings.value("editor/resize_mode") == RESIZE_LEFT_CLICK)
        self.rmb_radio.setChecked(self.settings.value("editor/resize_mode") == RESIZE_RIGHT_CLICK)

        self.lmb_radio.toggled.connect(self._update_settings)

        self._resize_radio_group = QButtonGroup()
        self._resize_radio_group.addButton(self.lmb_radio)
        self._resize_radio_group.addButton(self.rmb_radio)

        resize_layout = self._settings_row(
            "Object resize mode:", self.lmb_radio, self.rmb_radio, label_key="object_resize_mode"
        )
        layout.addLayout(resize_layout)

        # When Opening a ROM Section
        # -----------------------------------------------
        self._when_open_rom_box = QGroupBox(tr("SettingsDialog", "when_opening_a_rom", "When opening a ROM"), self)
        layout = QVBoxLayout()
        self._when_open_rom_box.setLayout(layout)

        self.ask_for_level_management_cb = QCheckBox(tr("Common", "enabled", "Enabled"))
        self.ask_for_level_management_cb.setChecked(self.settings.value("editor/ask_for_level_management"))
        self.ask_for_level_management_cb.stateChanged.connect(self._update_settings)

        layout.addLayout(
            self._settings_row(
                "Ask for Automatic Level Management:",
                self.ask_for_level_management_cb,
                label_key="ask_for_automatic_level_management",
                tooltip_key="help.ask_auto_level_management",
                tooltip_source=(
                    "Should the editor ask to enable Automatic Level Management when opening a new ROM that isn't "
                    "managed yet?"
                ),
            )
        )

        self.asm_loading_dropdown = QComboBox()
        self.asm_loading_dropdown.addItems([_settings_text(choice) for choice in asm_action_choices])
        self.asm_loading_dropdown.setCurrentIndex(self.settings.value("editor/asm_loading_behavior"))
        self.asm_loading_dropdown.currentTextChanged.connect(self._update_settings)

        layout.addLayout(
            self._settings_row(
                "How to handle ASM files:",
                self.asm_loading_dropdown,
                label_key="how_to_handle_asm_files",
                tooltip_key="help.asm_file_handling",
                tooltip_source="What should the editor do, when a ROM needs ASM files, or has them in its directory?",
            )
        )

        # Other Section
        # -----------------------------------------------
        self._other_settings_box = QGroupBox(tr("SettingsDialog", "miscellaneous", "Miscellaneous"), self)
        layout = QVBoxLayout()
        self._other_settings_box.setLayout(layout)

        self.monitor_rom_cb = QCheckBox(tr("Common", "enabled", "Enabled"))
        self.monitor_rom_cb.setChecked(self.settings.value("editor/monitor_rom_for_changes"))
        self.monitor_rom_cb.stateChanged.connect(self._update_settings)

        layout.addLayout(
            self._settings_row(
                "Offer to reload the ROM, if an outside change is detected:",
                self.monitor_rom_cb,
                label_key="label.reload_external_changes",
                tooltip_key="help.reload_external_rom_changes",
                tooltip_source="Should the editor prompt you to reload the ROM, if it is changed by an external program?",
            )
        )

        # GUI Section
        # -----------------------------------------------

        self.gui_box = QGroupBox(tr("SettingsDialog", "gui", "GUI"), self)
        layout = QVBoxLayout()
        self.gui_box.setLayout(layout)

        self.level_highlight_cb = QCheckBox(tr("Common", "enabled", "Enabled"))
        self.level_highlight_cb.setChecked(self.settings.value("world_view/show_level_pointers"))
        self.level_highlight_cb.stateChanged.connect(self._update_settings)

        level_highlight_layout = self._settings_row(
            "Highlight LevelPointers in LevelSelector World Maps:",
            self.level_highlight_cb,
            label_key="label.highlight_level_pointers",
            tooltip_key="help.highlight_level_pointers",
            tooltip_source="Should the Level Pointers be outlined by a red square in the Level Selector?",
        )
        layout.addLayout(level_highlight_layout)

        self.level_preview_dropdown = QComboBox()
        self.level_preview_dropdown.addItems([_settings_text(choice) for choice in level_preview_choices])
        self.level_preview_dropdown.setCurrentIndex(self.settings.value("editor/level_preview_type"))
        self.level_preview_dropdown.currentTextChanged.connect(self._update_settings)

        level_preview_layout = self._settings_row(
            "Level preview in Level Selector:",
            self.level_preview_dropdown,
            label_key="level_preview_in_level_selector",
            tooltip_key="help.level_preview_mode",
            tooltip_source=(
                "How the Level Selector should show the level preview. In a tooltip on hover, in the widget when "
                "after clicking a level, or not at all."
            ),
        )
        layout.addLayout(level_preview_layout)

        self.language_dropdown = QComboBox()
        for language_code in available_languages():
            self.language_dropdown.addItem(language_display_name(language_code), language_code)
        selected_language = self.settings.value("editor/language")
        self._selected_language = selected_language
        self.language_dropdown.setCurrentIndex(max(0, self.language_dropdown.findData(selected_language)))
        self.language_dropdown.currentIndexChanged.connect(self._update_settings)
        self.translation_manager_button = QPushButton(tr("SettingsDialog", "translations", "Translations..."), self)
        self.translation_manager_button.clicked.connect(self._open_translation_manager)

        language_layout = self._settings_row(
            "Language:",
            self.language_dropdown,
            self.translation_manager_button,
            label_key="language",
            tooltip_key="language_changes_apply_immediately",
            tooltip_source=LANGUAGE_CHANGE_NOTE,
        )
        layout.addLayout(language_layout)

        self._style_radio_buttons = []

        for gui_style in GUI_STYLE.keys():
            style_radio_button = QRadioButton(gui_style_display_text(gui_style))
            style_radio_button.setProperty("gui_style_key", gui_style)
            style_radio_button.setChecked(self.settings.value("editor/gui_style") == GUI_STYLE[gui_style]())
            style_radio_button.toggled.connect(self._update_settings)

            self._style_radio_buttons.append(style_radio_button)

        style_layout = self._settings_row("Style:", *self._style_radio_buttons, label_key="style")
        layout.addLayout(style_layout)

        path_layout = QHBoxLayout()

        self.path_dropdown = QComboBox(self)
        for default_dir_key in default_dirs:
            self.path_dropdown.addItem(default_dir_display_name(default_dir_key), default_dir_key)
        self.path_dropdown.setCurrentIndex(
            max(0, self.path_dropdown.findData(self.settings.value("editor/default_dir")))
        )
        self.path_dropdown.currentIndexChanged.connect(self.on_dropdown)

        self._default_path_label = QLabel(tr("SettingsDialog", "default_path", "Default path:"))
        path_layout.addWidget(self._default_path_label)
        path_layout.addWidget(self.path_dropdown)

        layout.addLayout(path_layout)

        default_dir_layout = QHBoxLayout()

        self.default_dir_label = QLabel()

        self.default_dir_button = QPushButton(icon("folder.svg"), "", self)
        self.default_dir_button.clicked.connect(self._get_default_dir)

        default_dir_layout.addWidget(self.default_dir_label, stretch=1)
        default_dir_layout.addWidget(self.default_dir_button)

        layout.addLayout(default_dir_layout)

        # Emulator Command Section
        # -----------------------------------------------

        self.emulator_command_input = QLineEdit(self)
        self.emulator_command_input.setPlaceholderText(tr("SettingsDialog", "path_to_emulator", "Path to emulator"))
        self.emulator_command_input.setText(self.settings.value("editor/instaplay_emulator"))

        self.emulator_command_input.textChanged.connect(self._update_settings)

        self.emulator_path_button = QPushButton(icon("folder.svg"), "", self)
        self.emulator_path_button.clicked.connect(self._get_emulator_path)

        self.command_arguments_input = QLineEdit(self)
        self.command_arguments_input.setPlaceholderText("%f")
        self.command_arguments_input.setText(self.settings.value("editor/instaplay_arguments"))

        self.command_arguments_input.textEdited.connect(self._update_settings)

        self.command_label = QLabel()

        self._command_box = QGroupBox(tr("SettingsDialog", "emulator", "Emulator"), self)
        command_layout = QVBoxLayout(self._command_box)

        self._emulator_command_label = QLabel(
            tr("SettingsDialog", "emulator_command_or_path_to_exe", 'Emulator command or "path to exe":')
        )
        command_layout.addWidget(self._emulator_command_label)

        command_input_layout = QHBoxLayout()
        command_input_layout.addWidget(self.emulator_command_input)
        command_input_layout.addWidget(self.emulator_path_button)

        command_layout.addLayout(command_input_layout)
        self._command_arguments_label = QLabel(
            tr("SettingsDialog", "label.emulator_args", "Command arguments (%f will be replaced with rom path):")
        )
        command_layout.addWidget(self._command_arguments_label)
        command_layout.addWidget(self.command_arguments_input)
        self._command_used_label = QLabel(
            tr("SettingsDialog", "command_used_to_play_the_rom", "Command used to play the rom:")
        )
        command_layout.addWidget(self._command_used_label)
        command_layout.addWidget(self.command_label)

        command_layout.addWidget(HorizontalLine())

        self._powerup_label = QLabel(
            tr("SettingsDialog", "power_up_of_mario_when_playing_level", "Power up of Mario when playing level:")
        )
        command_layout.addWidget(self._powerup_label)
        self.powerup_combo_box = QComboBox()

        for name, x, y, value, p_wing in POWERUPS:
            powerup_icon = self._icon_from_png(x, y)

            self.powerup_combo_box.addItem(powerup_icon, _settings_text(name))

        self.powerup_combo_box.setCurrentIndex(self.settings.value("editor/default_powerup"))
        self.powerup_combo_box.currentIndexChanged.connect(self._update_settings)

        self.starman_checkbox = QCheckBox()
        self.starman_checkbox.setIcon(self._icon_from_png(18, 53))
        self.starman_checkbox.setChecked(self.settings.value("editor/powerup_starman"))
        self.starman_checkbox.stateChanged.connect(self._update_settings)

        powerup_layout = QHBoxLayout()

        powerup_layout.addWidget(self.powerup_combo_box, stretch=1)
        powerup_layout.addWidget(self.starman_checkbox)

        command_layout.addLayout(powerup_layout)

        self.skip_title_screen_cb = QCheckBox(tr("Common", "enabled", "Enabled"))
        self.skip_title_screen_cb.setChecked(self.settings.value("editor/instaplay_skip_title_screen"))
        self.skip_title_screen_cb.stateChanged.connect(self._update_settings)

        command_layout.addLayout(
            self._settings_row(
                "Instaplay skips Title Screen",
                self.skip_title_screen_cb,
                label_key="instaplay_skips_title_screen",
            )
        )

        # -----------------------------------------------

        left_layout = QVBoxLayout()
        left_layout.addWidget(self._startup_box)
        left_layout.addWidget(self._mouse_box)
        left_layout.addWidget(self._when_open_rom_box)
        left_layout.addWidget(self._other_settings_box)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.gui_box)
        right_layout.addWidget(self._command_box)

        main_layout = QHBoxLayout(self)
        main_layout.addLayout(left_layout, stretch=1)
        main_layout.addSpacing(10)
        main_layout.addLayout(right_layout, stretch=1)

        self.on_dropdown(self.path_dropdown.currentText())
        self.update()

    def _settings_row(
        self,
        label_source: str,
        widget: QWidget,
        *widgets: QWidget,
        label_key: str,
        add_stretch: bool = True,
        tooltip_key: str = "",
        tooltip_source: str = "",
        context: str = "SettingsDialog",
    ) -> QHBoxLayout:
        """Build and remember a translated settings row.

        The shared ``label_and_widget`` helper returns a layout, so settings
        rows that need live language switching have to retain the label widget,
        catalog key, and fallback source text here. The stored tuple is display metadata only;
        settings keys and active widget values continue to live in
        ``Settings`` or Qt widget item data. The state flow is row-source text
        to translated Qt label; no persisted editor preference is derived from
        the label.

        Parameters
        ----------
        label_source : str
            English fallback string used if the catalog key is missing.
        widget : QWidget
            Primary settings control paired with the translated label.
        *widgets : QWidget
            Optional extra controls placed on the same row.
        label_key : str
            Stable settings-dialog catalog key for the row label.
        add_stretch : bool, optional
            Whether the row helper should insert stretch after the controls.
        tooltip_key : str, optional
            Stable settings-dialog catalog key for the row tooltip.
        tooltip_source : str, optional
            English fallback string for the row tooltip.
        context : str, optional
            Translation context that owns ``label_key`` and ``tooltip_key``.

        Returns
        -------
        QHBoxLayout
            Row layout ready to insert into a settings section.
        """
        tooltip = tr(context, tooltip_key, tooltip_source) if tooltip_key and tooltip_source else ""
        layout = label_and_widget(
            tr(context, label_key, label_source),
            widget,
            *widgets,
            add_stretch=add_stretch,
            tooltip=tooltip,
        )
        label_item = layout.itemAt(0)
        if label_item is not None and isinstance(label_item.widget(), QLabel):
            self._translated_rows.append(
                (label_item.widget(), context, label_key, label_source, tooltip_key, tooltip_source)
            )
        return layout

    def update(self):
        """Refresh derived settings UI.

        The command preview reflects the selected emulator path and argument
        template. ``needs_level_update`` lets open level views react to staged
        settings such as preview or tooltip behavior after the dialog writes
        settings back to ``Settings``.
        """
        self.command_label.setText(
            f" > {self.settings.value('editor/instaplay_emulator')} {self.settings.value('editor/instaplay_arguments')}"
        )

        self.needs_level_update.emit()

    def retranslate_ui(self) -> None:
        """Refresh visible settings labels that can change in place.

        This method updates section titles, row labels, checkboxes, option
        labels, placeholders, and language names without changing persisted
        settings values. Its workflow mirrors construction: startup choices,
        mouse behavior, ROM-open prompts, GUI options, directory choices, and
        emulator/instaplay controls are refreshed in order. Index-backed combo
        boxes keep their numeric indexes, and the language dropdown preserves
        the stable locale code stored in item data.
        """
        self.setWindowTitle(tr("SettingsDialog", "settings", "Settings"))
        self._startup_box.setTitle(tr("SettingsDialog", "start_up", "Start Up"))
        self._mouse_box.setTitle(tr("SettingsDialog", "mouse", "Mouse"))
        self._when_open_rom_box.setTitle(tr("SettingsDialog", "when_opening_a_rom", "When opening a ROM"))
        self._other_settings_box.setTitle(tr("SettingsDialog", "miscellaneous", "Miscellaneous"))
        self.gui_box.setTitle(tr("SettingsDialog", "gui", "GUI"))
        self._command_box.setTitle(tr("SettingsDialog", "emulator", "Emulator"))

        for label, context, label_key, source, tooltip_key, tooltip_source in self._translated_rows:
            label.setText(tr(context, label_key, source))
            label.setToolTip(tr(context, tooltip_key, tooltip_source) if tooltip_key and tooltip_source else "")

        for checkbox in (
            self.auto_save_cb,
            self._restore_last_opened_level_cb,
            self._scroll_cb,
            self._tooltip_cb,
            self.ask_for_level_management_cb,
            self.monitor_rom_cb,
            self.level_highlight_cb,
            self.skip_title_screen_cb,
        ):
            checkbox.setText(tr("Common", "enabled", "Enabled"))

        self.lmb_radio.setText(tr("SettingsDialog", "left_mouse_button", "Left Mouse Button"))
        self.rmb_radio.setText(tr("SettingsDialog", "right_mouse_button", "Right Mouse Button"))
        self._default_path_label.setText(tr("SettingsDialog", "default_path", "Default path:"))
        self._emulator_command_label.setText(
            tr("SettingsDialog", "emulator_command_or_path_to_exe", 'Emulator command or "path to exe":')
        )
        self._command_arguments_label.setText(
            tr("SettingsDialog", "label.emulator_args", "Command arguments (%f will be replaced with rom path):")
        )
        self._command_used_label.setText(
            tr("SettingsDialog", "command_used_to_play_the_rom", "Command used to play the rom:")
        )
        self._powerup_label.setText(
            tr("SettingsDialog", "power_up_of_mario_when_playing_level", "Power up of Mario when playing level:")
        )
        self.translation_manager_button.setText(tr("SettingsDialog", "translations", "Translations..."))
        self.emulator_command_input.setPlaceholderText(tr("SettingsDialog", "path_to_emulator", "Path to emulator"))

        self._retranslate_indexed_combo(self._release_channel_dropdown, release_channel_choices)
        self._retranslate_indexed_combo(self.asm_loading_dropdown, asm_action_choices)
        self._retranslate_indexed_combo(self.level_preview_dropdown, level_preview_choices)
        for style_radio_button in self._style_radio_buttons:
            style_key = style_radio_button.property("gui_style_key")
            if isinstance(style_key, str):
                style_radio_button.setText(gui_style_display_text(style_key))

        self._refresh_language_dropdown(str(self.language_dropdown.currentData() or self._selected_language))
        current_default_dir = self.path_dropdown.currentData()
        self.path_dropdown.blockSignals(True)
        for index in range(self.path_dropdown.count()):
            default_dir_key = self.path_dropdown.itemData(index)
            self.path_dropdown.setItemText(index, default_dir_display_name(default_dir_key))
        self.path_dropdown.setCurrentIndex(max(0, self.path_dropdown.findData(current_default_dir)))
        self.path_dropdown.blockSignals(False)

        current_powerup = self.powerup_combo_box.currentIndex()
        self.powerup_combo_box.blockSignals(True)
        for index, powerup in enumerate(POWERUPS):
            self.powerup_combo_box.setItemText(index, _settings_text(powerup.description))
        self.powerup_combo_box.setCurrentIndex(current_powerup)
        self.powerup_combo_box.blockSignals(False)
        self.update()

    def _refresh_language_dropdown(self, selected_language: str) -> None:
        """Rebuild language choices while preserving stable locale-code data.

        The language list can change after a user imports or reverts an
        override catalog. This Foundry localization workflow re-reads catalog
        discovery, stores locale codes in row data, and restores the chosen
        selection without using translated language names as persisted values.
        Because user catalogs can add languages at runtime, the dropdown is
        rebuilt as part of the catalog-change state flow.

        Parameters
        ----------
        selected_language : str
            Locale code that should remain selected after language discovery
            refreshes bundled and user catalogs for Qt translation.
        """
        self.language_dropdown.blockSignals(True)
        self.language_dropdown.clear()
        for language_code in available_languages():
            self.language_dropdown.addItem(language_display_name(language_code), language_code)
        selected_index = self.language_dropdown.findData(selected_language)
        if selected_index < 0:
            selected_index = self.language_dropdown.findData("en")
        self.language_dropdown.setCurrentIndex(max(0, selected_index))
        self.language_dropdown.blockSignals(False)

    def _retranslate_indexed_combo(self, combo_box: QComboBox, source_labels: list[str]) -> None:
        """Refresh an index-backed combo box without changing its value.

        The Foundry settings schema stores these controls by index, so live
        Qt translation must replace only the visible item text and then restore
        the same index. This preserves the persisted settings payload while
        letting visible option text follow the active catalog.

        Parameters
        ----------
        combo_box : QComboBox
            Combo box whose row indexes are persisted settings values.
        source_labels : list[str]
            Stable label keys ordered to match the persisted indexes.
        """
        current_index = combo_box.currentIndex()
        combo_box.blockSignals(True)
        for index, source_label in enumerate(source_labels):
            combo_box.setItemText(index, _settings_text(source_label))
        combo_box.setCurrentIndex(current_index)
        combo_box.blockSignals(False)

    def _open_translation_manager(self) -> None:
        """Open the user translation catalog manager dialog.

        The manager receives the selected language-dropdown code and writes only
        user overlay catalogs. If that code is ``system``, the manager's own
        selector falls back to a concrete editable locale because overlay files
        are stored by concrete code. Its ``catalog_changed`` signal lets this
        dialog refresh language discovery and reinstall the active translator
        when necessary.
        """
        dialog = TranslationManagerDialog(str(self.language_dropdown.currentData() or "en"), self)
        dialog.catalog_changed.connect(self._on_translation_catalog_changed)
        dialog.exec()

    def _on_translation_catalog_changed(self, changed_locale: str) -> None:
        """Refresh language choices and active UI after a user catalog changes.

        Imported or reverted catalogs can add, remove, or rename visible
        language choices, so the dropdown is rebuilt first while preserving its
        stable locale-code payload. If the edited catalog is the active
        concrete locale, the application translator is reinstalled and the
        recursive live-refresh path updates open widgets; otherwise this dialog
        refreshes only its own labels.

        Parameters
        ----------
        changed_locale : str
            Concrete locale code whose user overlay was imported, saved, or
            reverted.
        """
        selected_language = str(self.language_dropdown.currentData() or self._selected_language)
        self._refresh_language_dropdown(selected_language)
        if selected_language == changed_locale:
            qt_app = QCoreApplication.instance()
            if qt_app is not None:
                set_application_language(qt_app, selected_language)
                return
        self.retranslate_ui()

    def _update_settings(self, _=None):
        """Persist the staged widget state to ``Settings``.

        The method is intentionally broad because many Qt signals share the same
        handler. It writes all settings keys from their controls, applies the
        selected style sheet immediately, and refreshes derived UI afterward.
        Language persistence uses the stable locale code stored in the dropdown
        item data, never the translated display name; changing that code emits
        ``language_changed`` so the application can live-retranslate open UI.

        Parameters
        ----------
        _ : object, optional
            Ignored Qt signal payload.
        """
        self.settings.setValue("editor/instaplay_emulator", self.emulator_command_input.text())
        self.settings.setValue("editor/instaplay_arguments", self.command_arguments_input.text())
        self.settings.setValue("editor/instaplay_skip_title_screen", self.skip_title_screen_cb.isChecked())

        if self.lmb_radio.isChecked():
            self.settings.setValue("editor/resize_mode", RESIZE_LEFT_CLICK)
        else:
            self.settings.setValue("editor/resize_mode", RESIZE_RIGHT_CLICK)

        self.settings.setValue("editor/monitor_rom_for_changes", self.monitor_rom_cb.isChecked())
        self.settings.setValue("editor/ask_for_level_management", self.ask_for_level_management_cb.isChecked())
        self.settings.setValue("editor/auto_save_enabled", self.auto_save_cb.isChecked())
        self.settings.setValue("editor/remember_last_level", self._restore_last_opened_level_cb.isChecked())
        self.settings.setValue("editor/asm_loading_behavior", self.asm_loading_dropdown.currentIndex())
        self.settings.setValue("world_view/show_level_pointers", self.level_highlight_cb.isChecked())

        self.settings.setValue("editor/level_preview_type", self.level_preview_dropdown.currentIndex())
        selected_language = self.language_dropdown.currentData()
        self.settings.setValue("editor/language", selected_language)
        if selected_language != self._selected_language:
            self._selected_language = selected_language
            self.language_changed.emit(selected_language)

        # set up style sheets
        for child_widget in self.gui_box.children():
            if isinstance(child_widget, QRadioButton):
                if child_widget.isChecked():
                    selected_gui_style = child_widget.property("gui_style_key")

                    if not isinstance(selected_gui_style, str) or selected_gui_style not in GUI_STYLE:
                        continue

                    loaded_style_sheet = GUI_STYLE[selected_gui_style]()
                    self.settings.setValue("editor/gui_style", loaded_style_sheet)

                    self.parent().setStyleSheet(self.settings.value("editor/gui_style"))
                    break

        selected_default_dir = self.path_dropdown.currentData()
        self.settings.setValue("editor/default_dir", selected_default_dir)
        if selected_default_dir == "Custom":
            self.settings.setValue("editor/custom_default_dir_path", self.default_dir_label.text())

        self.settings.setValue("editor/default_dir_path", self.default_dir_label.text())

        self.settings.setValue("editor/release_channel", self._release_channel_dropdown.currentIndex())
        self.settings.setValue("editor/object_scroll_enabled", self._scroll_cb.isChecked())
        self.settings.setValue("level_view/object_tooltip_enabled", self._tooltip_cb.isChecked())

        self.settings.setValue("editor/default_powerup", self.powerup_combo_box.currentIndex())
        self.settings.setValue("editor/powerup_starman", self.starman_checkbox.isChecked())

        self.update()

    def _get_emulator_path(self):
        """Prompt for an emulator executable and store it in the command field.

        Selecting a file updates the line edit, which then flows through the
        normal settings update path.
        """
        path_to_emulator, _ = QFileDialog.getOpenFileName(
            self,
            caption=tr("SettingsDialog", "select_emulator_executable", "Select emulator executable"),
            dir=QStandardPaths.writableLocation(QStandardPaths.StandardLocation.ApplicationsLocation),
        )

        if not path_to_emulator:
            return

        self.emulator_command_input.setText(path_to_emulator)

    def _get_default_dir(self):
        """Prompt for a custom default ROM directory.

        Selecting a directory switches the path dropdown to ``Custom`` and
        persists both the display label and resolved path.
        """
        path_to_roms = QFileDialog.getExistingDirectory(
            self,
            caption=tr("SettingsDialog", "select_rom_directory", "Select Rom directory"),
            dir=QStandardPaths.writableLocation(QStandardPaths.StandardLocation.HomeLocation),
        )

        if not path_to_roms:
            return

        self.path_dropdown.setCurrentIndex(max(0, self.path_dropdown.findData("Custom")))
        self.default_dir_label.setText(path_to_roms)

        self._update_settings()

    def on_dropdown(self, _=None):
        """Resolve a default-directory dropdown choice.

        Built-in choices map through ``default_dirs``. ``Custom`` reuses the
        saved custom path so the user can switch away and back without losing it.

        Parameters
        ----------
        _ : object, optional
            Ignored Qt signal payload.
        """
        selected_default_dir = self.path_dropdown.currentData()
        if selected_default_dir == "Custom":
            self.default_dir_label.setText(self.settings.value("editor/custom_default_dir_path"))
        elif selected_default_dir in default_dirs:
            self.default_dir_label.setText(default_dirs[selected_default_dir])

        self._update_settings()

    @staticmethod
    def _icon_from_png(x: int, y: int) -> QIcon:
        """Create a dropdown icon from the object sprite sheet.

        The settings dialog uses this helper to turn sprite-sheet coordinates
        into icons for instaplay power-up choices and the Starman toggle.

        Parameters
        ----------
        x : int
            Sprite-sheet tile column.
        y : int
            Sprite-sheet tile row.

        Returns
        -------
        QIcon
            Icon created from the PNG bytes.
        """
        image = load_from_object_sprite_sheet(x, y)

        pixmap = QPixmap.fromImage(image)
        icon_from_png = QIcon(pixmap)

        return icon_from_png

    def on_exit(self):
        """Flush settings and close the dialog.

        Explicit sync keeps the underlying settings store current before the
        dialog delegates to ``CustomDialog`` cleanup.
        """
        self.settings.sync()

        super(SettingsDialog, self).on_exit()
