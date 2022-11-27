from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import (
    QCheckBox,
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
from foundry.gui.CustomDialog import CustomDialog
from foundry.gui.SettingsDialog import default_dirs
from foundry.gui.settings import (
    Settings,
)


class SettingsDialog(CustomDialog):
    def __init__(self, settings: Settings, parent=None):
        super(SettingsDialog, self).__init__(parent, "Settings")

        self.settings = settings

        # -----------------------------------------------
        # Online Section

        online_box = QGroupBox("Online", self)
        layout = QVBoxLayout()
        online_box.setLayout(layout)

        self._update_check_box = QCheckBox("Enabled")
        self._update_check_box.setChecked(self.settings.value("editor/update_on_startup"))
        self._update_check_box.toggled.connect(self._update_settings)

        layout.addLayout(
            label_and_widget(
                "Check for Updates on Startup:",
                self._update_check_box,
                tooltip="Checks the Repository for a new Version when the Editor is started.",
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
        path_dropdown.setCurrentText(self.settings.value("editor/default dir"))
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
        self.command_label.setText(
            f" > {self.settings.value('editor/instaplay_emulator')} {self.settings.value('editor/instaplay_arguments')}"
        )

    def _update_settings(self, _=None):
        self.settings.setValue("editor/instaplay_emulator", self.emulator_command_input.text())
        self.settings.setValue("editor/instaplay_arguments", self.command_arguments_input.text())

        self.settings.setValue("editor/update_on_startup", self._update_check_box.isChecked())

        self.settings.setValue("editor/default dir", self.path_dropdown.currentText())
        if self.path_dropdown.currentText() == "Custom":
            self.settings.setValue("editor/custom default dir path", self.default_dir_label.text())

        self.settings.setValue("editor/default dir path", self.default_dir_label.text())

        self.update()

    def _get_emulator_path(self):
        path_to_emulator, _ = QFileDialog.getOpenFileName(
            self,
            caption="Select emulator executable",
            dir=QStandardPaths.writableLocation(QStandardPaths.ApplicationsLocation),
        )

        if not path_to_emulator:
            return

        self.emulator_command_input.setText(path_to_emulator)

    def _get_default_dir(self):
        path_to_roms = QFileDialog.getExistingDirectory(
            self, caption="Select Rom directory", dir=QStandardPaths.writableLocation(QStandardPaths.HomeLocation)
        )

        if not path_to_roms:
            return

        self.path_dropdown.setCurrentText("Custom")
        self.default_dir_label.setText(path_to_roms)

        self._update_settings()

    def on_dropdown(self, new_text):
        if new_text == "Custom":
            self.default_dir_label.setText(self.settings.value("editor/custom default dir path"))
        elif new_text in default_dirs:
            self.default_dir_label.setText(default_dirs[new_text])

        self._update_settings()

    def on_exit(self):
        self.settings.sync()

        super(SettingsDialog, self).on_exit()
