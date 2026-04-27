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

from PySide6.QtCore import QStandardPaths, Signal, SignalInstance
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
)

from foundry import data_dir, icon
from foundry.game.gfx.drawable import load_from_object_sprite_sheet
from foundry.gui import label_and_widget
from foundry.gui.dialogs.CustomDialog import CustomDialog
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
        Display text shown in the power-up dropdown.
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
            Description, icon x, icon y, power-up code, and P-Wing flag.
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


POWERUPS = [
    PowerupEntry("Small Mario", 32, 53, POWERUP_NONE, False),
    PowerupEntry("Big Mario", 6, 48, POWERUP_MUSHROOM, False),
    PowerupEntry("Raccoon Mario", 57, 53, POWERUP_RACCOON, False),
    PowerupEntry("Fire Mario", 16, 53, POWERUP_FIREFLOWER, False),
    PowerupEntry("Tanooki Mario", 54, 53, POWERUP_TANOOKI, False),
    PowerupEntry("Frog Mario", 56, 53, POWERUP_FROG, False),
    PowerupEntry("Hammer Mario", 58, 53, POWERUP_HAMMER, False),
    # Even though P-Wing can *technically* be combined, it only really works with Raccoon and Tanooki suit
    PowerupEntry("Raccoon Mario with P-Wing", 55, 53, POWERUP_RACCOON, True),
    PowerupEntry("Tanooki Mario with P-Wing", 55, 53, POWERUP_TANOOKI, True),
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

asm_action_choices = ["Don't ask", "Ask if needed", "Load if available"]
release_channel_choices = ["Don't check", "Only stable versions", "Also nightly versions"]
level_preview_choices = ["Don't show", "Show on hover", "Show on click"]


class SettingsDialog(CustomDialog):
    """Edit persisted application and editor preferences.

    The dialog is a live view over ``Settings``. Most controls write their key
    immediately through ``_update_settings``; derived UI, such as the instaplay
    command preview and level-preview refresh signal, is updated after each
    write.

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
    _scroll_cb : QCheckBox
        Toggle for mouse-wheel object type changes.
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
    """

    needs_level_update: SignalInstance = Signal()

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
        super(SettingsDialog, self).__init__(parent, "Settings")

        self.settings = settings

        # On Startup
        # -----------------------------------------------

        on_start_up_box = QGroupBox("Start Up", self)
        layout = QVBoxLayout()
        on_start_up_box.setLayout(layout)

        self._release_channel_dropdown = QComboBox()
        self._release_channel_dropdown.addItems(release_channel_choices)
        self._release_channel_dropdown.setCurrentIndex(self.settings.value("editor/release_channel"))
        self._release_channel_dropdown.currentTextChanged.connect(self._update_settings)

        layout.addLayout(
            label_and_widget(
                "Check for Updates on Startup:",
                self._release_channel_dropdown,
                tooltip="Checks the Repository for a new version when the Editor is started. Nightly versions are "
                "untested, but have the latest fixes.",
            )
        )

        self.auto_save_cb = QCheckBox("Enabled")
        self.auto_save_cb.setChecked(self.settings.value("editor/auto_save_enabled"))
        self.auto_save_cb.stateChanged.connect(self._update_settings)

        layout.addLayout(
            label_and_widget(
                "Ask if Backup should be restored, after crash:",
                self.auto_save_cb,
                tooltip="Should the editor keep a copy of the current ROM with unsaved changes, so that if it crashes, "
                "the ROM and changed level can be restored?",
            )
        )

        self._restore_last_opened_level_cb = QCheckBox("Enabled")
        self._restore_last_opened_level_cb.setChecked(self.settings.value("editor/remember_last_level"))
        self._restore_last_opened_level_cb.stateChanged.connect(self._update_settings)

        layout.addLayout(
            label_and_widget(
                "Reopen last opened ROM and level:",
                self._restore_last_opened_level_cb,
                tooltip="Should Foundry remember the last opened ROM and level and open them automatically on startup?",
            )
        )

        # Mouse Section
        # -----------------------------------------------

        mouse_box = QGroupBox("Mouse", self)
        layout = QVBoxLayout()
        mouse_box.setLayout(layout)

        self._scroll_cb = QCheckBox("Enabled")
        self._scroll_cb.setChecked(self.settings.value("editor/object_scroll_enabled"))
        self._scroll_cb.toggled.connect(self._update_settings)

        layout.addLayout(
            label_and_widget(
                "Scroll objects with mouse wheel:",
                self._scroll_cb,
                tooltip="Select an object and scroll up and down to change its type.",
            )
        )

        self._tooltip_cb = QCheckBox("Enabled")
        self._tooltip_cb.setChecked(self.settings.value("level_view/object_tooltip_enabled"))
        self._tooltip_cb.toggled.connect(self._update_settings)

        layout.addLayout(
            label_and_widget(
                "Show object names on hover:",
                self._tooltip_cb,
                tooltip="When hovering your cursor over an object in a level, its name and position is shown in a "
                "tooltip.",
            )
        )

        self.lmb_radio = QRadioButton("Left Mouse Button")
        rmb_radio = QRadioButton("Right Mouse Button")

        self.lmb_radio.setChecked(self.settings.value("editor/resize_mode") == RESIZE_LEFT_CLICK)
        rmb_radio.setChecked(self.settings.value("editor/resize_mode") == RESIZE_RIGHT_CLICK)

        self.lmb_radio.toggled.connect(self._update_settings)

        radio_group = QButtonGroup()
        radio_group.addButton(self.lmb_radio)
        radio_group.addButton(rmb_radio)

        resize_layout = label_and_widget("Object resize mode:", self.lmb_radio, rmb_radio)
        layout.addLayout(resize_layout)

        # When Opening a ROM Section
        # -----------------------------------------------
        self._when_open_rom_box = QGroupBox("When opening a ROM", self)
        layout = QVBoxLayout()
        self._when_open_rom_box.setLayout(layout)

        self.ask_for_level_management_cb = QCheckBox("Enabled")
        self.ask_for_level_management_cb.setChecked(self.settings.value("editor/ask_for_level_management"))
        self.ask_for_level_management_cb.stateChanged.connect(self._update_settings)

        layout.addLayout(
            label_and_widget(
                "Ask for Automatic Level Management:",
                self.ask_for_level_management_cb,
                tooltip="Should the editor ask to enable Automatic Level Management when opening a new ROM that isn't "
                "managed yet?",
            )
        )

        self.asm_loading_dropdown = QComboBox()
        self.asm_loading_dropdown.addItems(asm_action_choices)
        self.asm_loading_dropdown.setCurrentIndex(self.settings.value("editor/asm_loading_behavior"))
        self.asm_loading_dropdown.currentTextChanged.connect(self._update_settings)

        layout.addLayout(
            label_and_widget(
                "How to handle ASM files:",
                self.asm_loading_dropdown,
                tooltip="What should the editor do, when a ROM needs ASM files, or has them in its directory?",
            )
        )

        # Other Section
        # -----------------------------------------------
        self._other_settings_box = QGroupBox("Miscellaneous", self)
        layout = QVBoxLayout()
        self._other_settings_box.setLayout(layout)

        self.monitor_rom_cb = QCheckBox("Enabled")
        self.monitor_rom_cb.setChecked(self.settings.value("editor/monitor_rom_for_changes"))
        self.monitor_rom_cb.stateChanged.connect(self._update_settings)

        layout.addLayout(
            label_and_widget(
                "Offer to reload the ROM, if an outside change is detected:",
                self.monitor_rom_cb,
                tooltip="Should the editor prompt you to reload the ROM, if it is changed by an external program?",
            )
        )

        # GUI Section
        # -----------------------------------------------

        self.gui_box = QGroupBox("GUI", self)
        layout = QVBoxLayout()
        self.gui_box.setLayout(layout)

        self.level_highlight_cb = QCheckBox("Enabled")
        self.level_highlight_cb.setChecked(self.settings.value("world_view/show_level_pointers"))
        self.level_highlight_cb.stateChanged.connect(self._update_settings)

        level_highlight_layout = label_and_widget(
            "Highlight LevelPointers in LevelSelector World Maps:",
            self.level_highlight_cb,
            tooltip="Should the Level Pointers be outlined by a red square in the Level Selector?",
        )
        layout.addLayout(level_highlight_layout)

        self.level_preview_dropdown = QComboBox()
        self.level_preview_dropdown.addItems(level_preview_choices)
        self.level_preview_dropdown.setCurrentIndex(self.settings.value("editor/level_preview_type"))
        self.level_preview_dropdown.currentTextChanged.connect(self._update_settings)

        level_preview_layout = label_and_widget(
            "Level preview in Level Selector:",
            self.level_preview_dropdown,
            tooltip="How the Level Selector should show the level preview. In a tooltip on hover, in the widget when "
            "after clicking a level, or not at all.",
        )
        layout.addLayout(level_preview_layout)

        style_choices = []

        for gui_style in GUI_STYLE.keys():
            gui_style = gui_style.capitalize()

            style_radio_button = QRadioButton(gui_style)
            style_radio_button.setChecked(self.settings.value("editor/gui_style") == GUI_STYLE[gui_style.upper()]())
            style_radio_button.toggled.connect(self._update_settings)

            style_choices.append(style_radio_button)

        style_layout = label_and_widget("Style:", *style_choices)
        layout.addLayout(style_layout)

        path_layout = QHBoxLayout()

        self.path_dropdown = QComboBox(self)
        self.path_dropdown.addItems(default_dirs.keys())
        self.path_dropdown.setCurrentText(self.settings.value("editor/default_dir"))
        self.path_dropdown.currentTextChanged.connect(self.on_dropdown)

        path_layout.addWidget(QLabel("Default path:"))
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
        self.emulator_command_input.setPlaceholderText("Path to emulator")
        self.emulator_command_input.setText(self.settings.value("editor/instaplay_emulator"))

        self.emulator_command_input.textChanged.connect(self._update_settings)

        self.emulator_path_button = QPushButton(icon("folder.svg"), "", self)
        self.emulator_path_button.clicked.connect(self._get_emulator_path)

        self.command_arguments_input = QLineEdit(self)
        self.command_arguments_input.setPlaceholderText("%f")
        self.command_arguments_input.setText(self.settings.value("editor/instaplay_arguments"))

        self.command_arguments_input.textEdited.connect(self._update_settings)

        self.command_label = QLabel()

        command_box = QGroupBox("Emulator", self)
        command_layout = QVBoxLayout(command_box)

        command_layout.addWidget(QLabel('Emulator command or "path to exe":'))

        command_input_layout = QHBoxLayout()
        command_input_layout.addWidget(self.emulator_command_input)
        command_input_layout.addWidget(self.emulator_path_button)

        command_layout.addLayout(command_input_layout)
        command_layout.addWidget(QLabel("Command arguments (%f will be replaced with rom path):"))
        command_layout.addWidget(self.command_arguments_input)
        command_layout.addWidget(QLabel("Command used to play the rom:"))
        command_layout.addWidget(self.command_label)

        command_layout.addWidget(HorizontalLine())

        command_layout.addWidget(QLabel("Power up of Mario when playing level:"))
        self.powerup_combo_box = QComboBox()

        for name, x, y, value, p_wing in POWERUPS:
            powerup_icon = self._icon_from_png(x, y)

            self.powerup_combo_box.addItem(powerup_icon, name)

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

        self.skip_title_screen_cb = QCheckBox("Enabled")
        self.skip_title_screen_cb.setChecked(self.settings.value("editor/instaplay_skip_title_screen"))
        self.skip_title_screen_cb.stateChanged.connect(self._update_settings)

        command_layout.addLayout(label_and_widget("Instaplay skips Title Screen", self.skip_title_screen_cb))

        # -----------------------------------------------

        left_layout = QVBoxLayout()
        left_layout.addWidget(on_start_up_box)
        left_layout.addWidget(mouse_box)
        left_layout.addWidget(self._when_open_rom_box)
        left_layout.addWidget(self._other_settings_box)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.gui_box)
        right_layout.addWidget(command_box)

        main_layout = QHBoxLayout(self)
        main_layout.addLayout(left_layout, stretch=1)
        main_layout.addSpacing(10)
        main_layout.addLayout(right_layout, stretch=1)

        self.on_dropdown(self.path_dropdown.currentText())
        self.update()

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

    def _update_settings(self, _=None):
        """Persist the staged widget state to ``Settings``.

        The method is intentionally broad because many Qt signals share the same
        handler. It writes all settings keys from their controls, applies the
        selected style sheet immediately, and refreshes derived UI afterward.

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

        # set up style sheets
        for child_widget in self.gui_box.children():
            if isinstance(child_widget, QRadioButton):
                if child_widget.isChecked():
                    selected_gui_style = child_widget.text().upper()

                    loaded_style_sheet = GUI_STYLE[selected_gui_style]()
                    self.settings.setValue("editor/gui_style", loaded_style_sheet)

                    self.parent().setStyleSheet(self.settings.value("editor/gui_style"))
                    break

        self.settings.setValue("editor/default_dir", self.path_dropdown.currentText())
        if self.path_dropdown.currentText() == "Custom":
            self.settings.setValue("editor/custom_default_dir_path", self.default_dir_label.text())

        self.settings.setValue("editor/default_dir_path", self.default_dir_label.text())

        self.settings.setValue(
            "editor/release_channel", release_channel_choices.index(self._release_channel_dropdown.currentText())
        )
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
            caption="Select emulator executable",
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
            caption="Select Rom directory",
            dir=QStandardPaths.writableLocation(QStandardPaths.StandardLocation.HomeLocation),
        )

        if not path_to_roms:
            return

        self.path_dropdown.setCurrentText("Custom")
        self.default_dir_label.setText(path_to_roms)

        self._update_settings()

    def on_dropdown(self, new_text):
        """Resolve a default-directory dropdown choice.

        Built-in choices map through ``default_dirs``. ``Custom`` reuses the
        saved custom path so the user can switch away and back without losing it.

        Parameters
        ----------
        new_text : str
            Selected directory option label.
        """
        if new_text == "Custom":
            self.default_dir_label.setText(self.settings.value("editor/custom_default_dir_path"))
        elif new_text in default_dirs:
            self.default_dir_label.setText(default_dirs[new_text])

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
