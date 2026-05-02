"""Configure Scribe editor startup, path, and emulator preferences.

This dialog gathers the persistent editor settings that affect update checks,
default ROM browsing locations, and the emulator command used by Instaplay.
The widget reads values from :class:`foundry.gui.settings.Settings`, stages
editable Qt controls for each setting family, and writes changes back as the
user adjusts fields so the rest of the GUI can observe the updated values.

See Also
--------
foundry.gui.dialogs.SettingsDialog : Foundry's broader editor settings dialog
    that provides the shared release-channel and default-directory option
    tables reused here.
foundry.gui.settings.Settings : Persistent storage wrapper that backs the
    dialog state.
scribe.gui.main_window : Main window that launches the dialog and consumes the
    synchronized settings values.
"""

from PySide6.QtCore import QStandardPaths, Signal, SignalInstance
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from foundry import icon
from foundry.gui.dialogs.CustomDialog import CustomDialog
from foundry.gui.dialogs.SettingsDialog import (
    default_dir_display_name,
    default_dirs,
    release_channel_choices,
    settings_display_text,
)
from foundry.gui.localization import available_languages, language_display_name, tr
from foundry.gui.settings import Settings

TR_CONTEXT = "ScribeSettingsDialog"


class SettingsDialog(CustomDialog):
    """Edit persistent Scribe settings that shape editor startup behavior.

    The dialog groups settings by workflow rather than by raw key name. One
    section controls how aggressively Scribe checks for updates, another picks
    the default directory used when opening ROM-related files, and the last
    section assembles the emulator command line used by Instaplay. Each control
    writes through to :class:`foundry.gui.settings.Settings` as soon as the
    user changes it so later actions in the main window see the same persisted
    values that this dialog previews.

    Parameters
    ----------
    settings : Settings
        Settings store that provides the initial values and receives every
        change made through the dialog widgets.
    parent : QWidget, optional
        Parent widget that owns the dialog lifetime and window stacking.

    Attributes
    ----------
    settings : Settings
        Persistent settings store shared with the rest of the Scribe GUI.
    language_changed : SignalInstance
        Emitted with the selected locale code after the language setting is
        persisted so open widgets can refresh through ``retranslate_ui``.
    online_box : QGroupBox
        Section containing the release-channel selector.
    _release_channel_dropdown : QComboBox
        Selector that maps the saved release-channel index to the human-facing
        update policy labels reused from Foundry.
    release_channel_label : QLabel
        Display label and tooltip for the update-channel selector.
    gui_box : QGroupBox
        Container for default-directory controls.
    default_path_label : QLabel
        Display label for the default-directory strategy dropdown.
    path_dropdown : QComboBox
        Selector for predefined directory strategies such as user home or a
        custom path.
    language_label : QLabel
        Display label and tooltip for the live language selector.
    language_dropdown : QComboBox
        Selector that displays localized language names while storing stable
        locale codes as item data.
    _selected_language : str
        Last persisted locale code used to avoid duplicate language-change
        emissions during label refreshes.
    default_dir_label : QLabel
        Read-only label that mirrors the effective directory path staged by the
        dropdown.
    default_dir_button : QPushButton
        Browse button that resolves the custom default-directory path.
    emulator_command_input : QLineEdit
        Editable field for the emulator executable path.
    emulator_path_button : QPushButton
        Browse button that resolves the emulator executable path.
    command_arguments_input : QLineEdit
        Editable field for the command-line arguments passed to the emulator.
    command_box : QGroupBox
        Section containing emulator command controls and preview labels.
    emulator_command_label : QLabel
        Display label for the emulator executable field.
    command_arguments_label : QLabel
        Display label for emulator argument text.
    command_preview_label : QLabel
        Display label for the composed command preview.
    command_label : QLabel
        Preview label that shows the composed emulator command exactly as
        Instaplay will read it from settings.
    """

    language_changed: SignalInstance = Signal(str)

    def __init__(self, settings: Settings, parent=None):
        """Build grouped controls around the persistent Scribe settings keys.

        The constructor reads the persisted settings values once, uses them to
        seed each Qt control, then wires change signals back into
        :meth:`_update_settings`. That write-through path keeps the preview
        label, stored settings keys, and later main-window workflows aligned
        even before the dialog closes. The final calls to :meth:`on_dropdown`
        and :meth:`update` normalize the initial path preview and emulator
        command preview from the same data flow the interactive callbacks use.

        Parameters
        ----------
        settings : Settings
            Persistent settings store shared with the rest of the editor.
        parent : QWidget, optional
            Parent widget that owns the dialog lifetime and stacking order.
        """
        super(SettingsDialog, self).__init__(parent, tr(TR_CONTEXT, "settings", "Settings"))

        self.settings = settings

        # -----------------------------------------------
        # Online Section

        self.online_box = QGroupBox(tr(TR_CONTEXT, "online", "Online"), self)
        layout = QVBoxLayout()
        self.online_box.setLayout(layout)

        self._release_channel_dropdown = QComboBox()
        self._release_channel_dropdown.addItems([settings_display_text(choice) for choice in release_channel_choices])
        self._release_channel_dropdown.setCurrentIndex(self.settings.value("editor/release_channel"))
        self._release_channel_dropdown.currentTextChanged.connect(self._update_settings)

        self.release_channel_label = QLabel()
        self.release_channel_label.setToolTip(
            tr(
                TR_CONTEXT,
                "help.update_check",
                "Checks the Repository for a new version when the Editor is started. Nightly versions are untested, but have the latest fixes.",
            )
        )
        release_channel_layout = QHBoxLayout()
        release_channel_layout.addWidget(self.release_channel_label)
        release_channel_layout.addStretch(1)
        release_channel_layout.addWidget(self._release_channel_dropdown)
        layout.addLayout(release_channel_layout)

        # -----------------------------------------------
        # GUI section

        self.gui_box = QGroupBox(tr(TR_CONTEXT, "gui", "GUI"), self)
        layout = QVBoxLayout()
        self.gui_box.setLayout(layout)

        path_layout = QHBoxLayout()

        self.path_dropdown = path_dropdown = QComboBox(self)
        for default_dir_key in default_dirs:
            path_dropdown.addItem(default_dir_display_name(default_dir_key), default_dir_key)
        path_dropdown.setCurrentIndex(max(0, path_dropdown.findData(self.settings.value("editor/default_dir"))))
        path_dropdown.currentIndexChanged.connect(self.on_dropdown)

        self.default_path_label = QLabel()
        path_layout.addWidget(self.default_path_label)
        path_layout.addWidget(path_dropdown)

        layout.addLayout(path_layout)

        self.language_dropdown = QComboBox()
        for language_code in available_languages():
            self.language_dropdown.addItem(language_display_name(language_code), language_code)
        selected_language = self.settings.value("editor/language")
        self._selected_language = selected_language
        self.language_dropdown.setCurrentIndex(max(0, self.language_dropdown.findData(selected_language)))
        self.language_dropdown.currentIndexChanged.connect(self._update_settings)

        self.language_label = QLabel()
        self.language_label.setToolTip(
            tr(TR_CONTEXT, "language_changes_apply_immediately", "Language changes apply immediately.")
        )
        language_layout = QHBoxLayout()
        language_layout.addWidget(self.language_label)
        language_layout.addStretch(1)
        language_layout.addWidget(self.language_dropdown)
        layout.addLayout(language_layout)

        default_dir_layout = QHBoxLayout()

        self.default_dir_label = QLabel()

        self.default_dir_button = QPushButton(icon("folder.svg"), "", self)
        self.default_dir_button.clicked.connect(self._get_default_dir)

        default_dir_layout.addWidget(self.default_dir_label, stretch=1)
        default_dir_layout.addWidget(self.default_dir_button)

        layout.addLayout(default_dir_layout)

        # -----------------------------------------------
        # Emulator Command Section

        self.emulator_command_input = QLineEdit(self)
        self.emulator_command_input.setPlaceholderText(tr(TR_CONTEXT, "path_to_emulator", "Path to emulator"))
        self.emulator_command_input.setText(self.settings.value("editor/instaplay_emulator"))

        self.emulator_command_input.textChanged.connect(self._update_settings)

        self.emulator_path_button = QPushButton(icon("folder.svg"), "", self)
        self.emulator_path_button.clicked.connect(self._get_emulator_path)

        self.command_arguments_input = QLineEdit(self)
        self.command_arguments_input.setPlaceholderText("%f")
        self.command_arguments_input.setText(self.settings.value("editor/instaplay_arguments"))

        self.command_arguments_input.textEdited.connect(self._update_settings)

        self.command_label = QLabel()

        self.command_box = QGroupBox(tr(TR_CONTEXT, "emulator", "Emulator"), self)
        command_layout = QVBoxLayout(self.command_box)

        self.emulator_command_label = QLabel()
        command_layout.addWidget(self.emulator_command_label)

        command_input_layout = QHBoxLayout()
        command_input_layout.addWidget(self.emulator_command_input)
        command_input_layout.addWidget(self.emulator_path_button)

        command_layout.addLayout(command_input_layout)
        self.command_arguments_label = QLabel()
        command_layout.addWidget(self.command_arguments_label)
        command_layout.addWidget(self.command_arguments_input)
        self.command_preview_label = QLabel()
        command_layout.addWidget(self.command_preview_label)
        command_layout.addWidget(self.command_label)

        # -----------------------------------------------

        layout = QVBoxLayout(self)
        layout.addWidget(self.online_box)
        layout.addWidget(self.gui_box)
        layout.addWidget(self.command_box)

        self.retranslate_ui()
        self.on_dropdown(self.path_dropdown.currentText())
        self.update()

    def update(self):
        """Refresh the emulator command preview from persisted settings.

        The dialog keeps the preview label derived from settings rather than
        from the line-edit widgets directly. That lets the preview confirm the
        exact values that were last written through :meth:`_update_settings`,
        which matches what later Instaplay launch code will consume.
        """
        self.command_label.setText(
            f" > {self.settings.value('editor/instaplay_emulator')} {self.settings.value('editor/instaplay_arguments')}"
        )

    def _update_settings(self, _=None):
        """Persist widget state back into the shared settings store.

        The dialog uses this method as the single write-through path for every
        editable control. It copies the staged widget values into the settings
        keys that drive update checking, default-directory resolution, and the
        Instaplay command line, then refreshes the preview label so the visible
        command stays synchronized with the stored values.

        Parameters
        ----------
        _ : object, optional
            Signal payload forwarded by Qt change notifications. The dialog
            ignores the value because it always rereads the full widget state.
        """
        self.settings.setValue("editor/instaplay_emulator", self.emulator_command_input.text())
        self.settings.setValue("editor/instaplay_arguments", self.command_arguments_input.text())

        self.settings.setValue("editor/release_channel", self._release_channel_dropdown.currentIndex())
        selected_language = self.language_dropdown.currentData()
        self.settings.setValue("editor/language", selected_language)
        if selected_language != self._selected_language:
            self._selected_language = selected_language
            self.language_changed.emit(selected_language)

        selected_default_dir = self.path_dropdown.currentData()
        self.settings.setValue("editor/default_dir", selected_default_dir)
        if selected_default_dir == "Custom":
            self.settings.setValue("editor/custom_default_dir_path", self.default_dir_label.text())

        self.settings.setValue("editor/default_dir_path", self.default_dir_label.text())

        self.update()

    def retranslate_ui(self) -> None:
        """Refresh visible settings labels that can change in place.

        The method coordinates the live-translation workflow for section
        titles, labels, tooltips, placeholders, release-channel labels,
        default-directory labels, and language names. It preserves stable item
        data and committed settings values while rebuilding display strings.
        Signal blocking creates the commit boundary around dropdown
        repopulation, preventing display-only refreshes from being mistaken for
        user setting changes.
        """
        self.setWindowTitle(tr(TR_CONTEXT, "settings", "Settings"))
        self.online_box.setTitle(tr(TR_CONTEXT, "online", "Online"))
        self.gui_box.setTitle(tr(TR_CONTEXT, "gui", "GUI"))
        self.command_box.setTitle(tr(TR_CONTEXT, "emulator", "Emulator"))
        self.release_channel_label.setText(
            tr(TR_CONTEXT, "check_for_updates_on_startup", "Check for Updates on Startup:")
        )
        self.release_channel_label.setToolTip(
            tr(
                TR_CONTEXT,
                "help.update_check",
                "Checks the Repository for a new version when the Editor is started. Nightly versions are untested, but have the latest fixes.",
            )
        )
        current_release_channel = self._release_channel_dropdown.currentIndex()
        self._release_channel_dropdown.blockSignals(True)
        for index, choice in enumerate(release_channel_choices):
            self._release_channel_dropdown.setItemText(index, settings_display_text(choice))
        self._release_channel_dropdown.setCurrentIndex(current_release_channel)
        self._release_channel_dropdown.blockSignals(False)
        self.default_path_label.setText(tr(TR_CONTEXT, "default_path", "Default path:"))
        self.language_label.setText(tr(TR_CONTEXT, "language", "Language:"))
        self.language_label.setToolTip(
            tr(TR_CONTEXT, "language_changes_apply_immediately", "Language changes apply immediately.")
        )
        self.emulator_command_input.setPlaceholderText(tr(TR_CONTEXT, "path_to_emulator", "Path to emulator"))
        self.emulator_command_label.setText(
            tr(TR_CONTEXT, "emulator_command_or_path_to_exe", 'Emulator command or "path to exe":')
        )
        self.command_arguments_label.setText(
            tr(TR_CONTEXT, "label.emulator_args", "Command arguments (%f will be replaced with rom path):")
        )
        self.command_preview_label.setText(
            tr(TR_CONTEXT, "command_used_to_play_the_rom", "Command used to play the rom:")
        )
        current_language = self.language_dropdown.currentData()
        self.language_dropdown.blockSignals(True)
        for index in range(self.language_dropdown.count()):
            language_code = self.language_dropdown.itemData(index)
            self.language_dropdown.setItemText(index, language_display_name(language_code))
        self.language_dropdown.setCurrentIndex(max(0, self.language_dropdown.findData(current_language)))
        self.language_dropdown.blockSignals(False)
        current_default_dir = self.path_dropdown.currentData()
        self.path_dropdown.blockSignals(True)
        for index in range(self.path_dropdown.count()):
            default_dir_key = self.path_dropdown.itemData(index)
            self.path_dropdown.setItemText(index, default_dir_display_name(default_dir_key))
        self.path_dropdown.setCurrentIndex(max(0, self.path_dropdown.findData(current_default_dir)))
        self.path_dropdown.blockSignals(False)

    def _get_emulator_path(self):
        """Prompt for an emulator executable and stage it in the command field.

        The file picker starts in the platform applications directory so the
        user lands near installed emulator binaries. When the user accepts a
        path, setting the line edit triggers :meth:`_update_settings`, which
        writes the new executable path into persistent settings and refreshes
        the command preview.
        """
        path_to_emulator, _ = QFileDialog.getOpenFileName(
            self,
            caption=tr(TR_CONTEXT, "select_emulator_executable", "Select emulator executable"),
            dir=QStandardPaths.writableLocation(QStandardPaths.StandardLocation.ApplicationsLocation),
        )

        if not path_to_emulator:
            return

        self.emulator_command_input.setText(path_to_emulator)

    def _get_default_dir(self):
        """Prompt for a custom default ROM directory and persist the choice.

        This path picker handles the one dropdown mode whose target directory
        cannot be derived from the shared :data:`default_dirs` table. Accepting
        a directory forces the dropdown into ``"Custom"``, updates the visible
        path label, and reuses :meth:`_update_settings` so both the generic and
        custom default-directory settings keys stay in sync.
        """
        path_to_roms = QFileDialog.getExistingDirectory(
            self,
            caption=tr(TR_CONTEXT, "select_rom_directory", "Select Rom directory"),
            dir=QStandardPaths.writableLocation(QStandardPaths.StandardLocation.HomeLocation),
        )

        if not path_to_roms:
            return

        self.path_dropdown.setCurrentIndex(max(0, self.path_dropdown.findData("Custom")))
        self.default_dir_label.setText(path_to_roms)

        self._update_settings()

    def on_dropdown(self, _=None):
        """Map the selected directory mode to the path preview and settings.

        Parameters
        ----------
        _ : object, optional
            Ignored Qt signal payload.

        Notes
        -----
        The method always finishes by calling :meth:`_update_settings` so the
        persisted directory mode and the preview label change together. That
        keeps later open-dialog workflows aligned with the choice the user can
        currently see.
        """
        selected_default_dir = self.path_dropdown.currentData()
        if selected_default_dir == "Custom":
            self.default_dir_label.setText(self.settings.value("editor/custom_default_dir_path"))
        elif selected_default_dir in default_dirs:
            self.default_dir_label.setText(default_dirs[selected_default_dir])

        self._update_settings()

    def on_exit(self):
        """Flush pending settings writes before delegating dialog shutdown.

        Syncing here preserves the write-through changes made during editing so
        later sessions and launch workflows see the same values even if the
        settings backend has not flushed them yet.
        """
        self.settings.sync()

        super(SettingsDialog, self).on_exit()
