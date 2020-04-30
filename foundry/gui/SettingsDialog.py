from PySide2.QtWidgets import QGroupBox, QLabel, QLineEdit, QVBoxLayout

from foundry.gui.CustomDialog import CustomDialog
from foundry.gui.settings import SETTINGS, load_settings, save_settings

load_settings()


class SettingsDialog(CustomDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)

        self.emulator_command_input = QLineEdit(self)
        self.emulator_command_input.textEdited.connect(self._update_settings)
        self.emulator_command_input.setPlaceholderText("Path to emulator")
        self.emulator_command_input.setText(SETTINGS["instaplay_emulator"])

        self.command_arguments_input = QLineEdit(self)
        self.command_arguments_input.textEdited.connect(self._update_settings)
        self.command_arguments_input.setPlaceholderText("%f")
        self.command_arguments_input.setText(SETTINGS["instaplay_arguments"])

        self.command_label = QLabel()

        command_box = QGroupBox("Emulator", self)
        command_layout = QVBoxLayout(command_box)

        command_layout.addWidget(QLabel("Emulator command or path to exe:"))
        command_layout.addWidget(self.emulator_command_input)
        command_layout.addWidget(QLabel("Command arguments (%f will be replaced with rom path):"))
        command_layout.addWidget(self.command_arguments_input)

        layout = QVBoxLayout(self)
        layout.addWidget(command_box)
        layout.addWidget(QLabel("Command used to play the rom:"))
        layout.addWidget(self.command_label)

        self.update()

    def update(self):
        self.command_label.setText(f" > {SETTINGS['instaplay_emulator']} {SETTINGS['instaplay_arguments']}")

    def _update_settings(self, _):
        SETTINGS["instaplay_emulator"] = self.emulator_command_input.text()
        SETTINGS["instaplay_arguments"] = self.command_arguments_input.text()

        self.update()

    def on_exit(self):
        save_settings()

        super(SettingsDialog, self).on_exit()


def show_settings():
    SettingsDialog().exec_()
