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

from PySide6.QtCore import QStandardPaths
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
from foundry.gui import label_and_widget
from foundry.gui.dialogs.CustomDialog import CustomDialog
from foundry.gui.dialogs.SettingsDialog import default_dirs, release_channel_choices
from foundry.gui.settings import Settings


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
    _release_channel_dropdown : QComboBox
        Selector that maps the saved release-channel index to the human-facing
        update policy labels reused from Foundry.
    gui_box : QGroupBox
        Container for default-directory controls.
    path_dropdown : QComboBox
        Selector for predefined directory strategies such as user home or a
        custom path.
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
    command_label : QLabel
        Preview label that shows the composed emulator command exactly as
        Instaplay will read it from settings.
    """

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
        super(SettingsDialog, self).__init__(parent, "Settings")

        self.settings = settings

        # -----------------------------------------------
        # Online Section

        online_box = QGroupBox("Online", self)
        layout = QVBoxLayout()
        online_box.setLayout(layout)

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

        # -----------------------------------------------
        # GUI section

        self.gui_box = QGroupBox("GUI", self)
        layout = QVBoxLayout()
        self.gui_box.setLayout(layout)

        path_layout = QHBoxLayout()

        self.path_dropdown = path_dropdown = QComboBox(self)
        path_dropdown.addItems(default_dirs.keys())
        path_dropdown.setCurrentText(self.settings.value("editor/default_dir"))
        path_dropdown.currentTextChanged.connect(self.on_dropdown)

        path_layout.addWidget(QLabel("Default path:"))
        path_layout.addWidget(path_dropdown)

        layout.addLayout(path_layout)

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

        # -----------------------------------------------

        layout = QVBoxLayout(self)
        layout.addWidget(online_box)
        layout.addWidget(self.gui_box)
        layout.addWidget(command_box)

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

        self.settings.setValue(
            "editor/release_channel", release_channel_choices.index(self._release_channel_dropdown.currentText())
        )

        self.settings.setValue("editor/default_dir", self.path_dropdown.currentText())
        if self.path_dropdown.currentText() == "Custom":
            self.settings.setValue("editor/custom_default_dir_path", self.default_dir_label.text())

        self.settings.setValue("editor/default_dir_path", self.default_dir_label.text())

        self.update()

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
            caption="Select emulator executable",
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
            caption="Select Rom directory",
            dir=QStandardPaths.writableLocation(QStandardPaths.StandardLocation.HomeLocation),
        )

        if not path_to_roms:
            return

        self.path_dropdown.setCurrentText("Custom")
        self.default_dir_label.setText(path_to_roms)

        self._update_settings()

    def on_dropdown(self, new_text):
        """Map the selected directory mode to the path preview and settings.

        Parameters
        ----------
        new_text : str
            Label chosen in the directory-mode dropdown. Built-in labels map to
            :data:`default_dirs`, while ``"Custom"`` reuses the previously
            stored custom path.

        Notes
        -----
        The method always finishes by calling :meth:`_update_settings` so the
        persisted directory mode and the preview label change together. That
        keeps later open-dialog workflows aligned with the choice the user can
        currently see.
        """
        if new_text == "Custom":
            self.default_dir_label.setText(self.settings.value("editor/custom_default_dir_path"))
        elif new_text in default_dirs:
            self.default_dir_label.setText(default_dirs[new_text])

        self._update_settings()

    def on_exit(self):
        """Flush pending settings writes before delegating dialog shutdown.

        Syncing here preserves the write-through changes made during editing so
        later sessions and launch workflows see the same values even if the
        settings backend has not flushed them yet.
        """
        self.settings.sync()

        super(SettingsDialog, self).on_exit()
