from PySide2.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QComboBox,
)

from PySide2.QtGui import QIcon, QImage, QColor, Qt, QPixmap

# from PySide2.QtGui import QBrush, QColor, QImage, QPainter, QPen, Qt
from PySide2.QtCore import QRect
from foundry.game.gfx.objects.EnemyItem import MASK_COLOR

from foundry import icon, data_dir
from foundry.gui.CustomDialog import CustomDialog
from foundry.gui.settings import RESIZE_LEFT_CLICK, RESIZE_RIGHT_CLICK, SETTINGS, load_settings, save_settings
from foundry.gui.HorizontalLine import HorizontalLine

load_settings()

POWERUPS_NAME = 0
POWERUPS_X = 1
POWERUPS_Y = 2
POWERUPS_VALUE = 3
POWERUPS_PWING = 4
POWERUPS = {
    "none": ["Small Mario", 32, 53, 0, False],
    "mushroom": ["Big Mario", 6, 48, 1, False],
    "leaf": ["Raccoon Mario", 57, 53, 3, False],
    "fire flower": ["Fire Mario", 16, 53, 2, False],
    "tanooki suit": ["Tanooki Mario", 54, 53, 5, False],
    "frog suit": ["Frog Mario", 56, 53, 4, False],
    "hammer suit": ["Hammer Mario", 58, 53, 6, False],
    
    # Even though P-Wing ca *technically* be combined, it only really works with Raccoon and Tanooki suit
    "P-wing Raccoon": ["Raccoon Mario with P-Wing", 55, 53, 3, True],
    "P-wing Tanooki": ["Tanooki Mario with P-Wing", 55, 53, 5, True],
}

png = QImage(str(data_dir / "gfx.png"))
png.convertTo(QImage.Format_RGB888)


class SettingsDialog(CustomDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent, "Settings")

        mouse_box = QGroupBox("Mouse", self)
        mouse_box.setLayout(QVBoxLayout())

        scroll_layout = QHBoxLayout()

        label = QLabel("Scroll objects with mouse wheel:")
        label.setToolTip("Select an object and scroll up and down to change its type.")
        self._scroll_check_box = QCheckBox("Enabled")
        self._scroll_check_box.setChecked(SETTINGS["object_scroll_enabled"])
        self._scroll_check_box.toggled.connect(self._update_settings)

        scroll_layout.addWidget(label)
        scroll_layout.addStretch(1)
        scroll_layout.addWidget(self._scroll_check_box)

        resize_layout = QHBoxLayout()

        self.lmb_radio = QRadioButton("Left Mouse Button")
        rmb_radio = QRadioButton("Right Mouse Button")

        self.lmb_radio.setChecked(SETTINGS["resize_mode"] == RESIZE_LEFT_CLICK)
        rmb_radio.setChecked(SETTINGS["resize_mode"] == RESIZE_RIGHT_CLICK)

        self.lmb_radio.toggled.connect(self._update_settings)

        radio_group = QButtonGroup()
        radio_group.addButton(self.lmb_radio)
        radio_group.addButton(rmb_radio)

        resize_layout.addWidget(QLabel("Object resize mode:"))
        resize_layout.addStretch(1)
        resize_layout.addWidget(self.lmb_radio)
        resize_layout.addWidget(rmb_radio)

        mouse_box.layout().addLayout(scroll_layout)
        mouse_box.layout().addLayout(resize_layout)

        # emulator command

        self.emulator_command_input = QLineEdit(self)
        self.emulator_command_input.setPlaceholderText("Path to emulator")
        self.emulator_command_input.setText(SETTINGS["instaplay_emulator"])

        self.emulator_command_input.textChanged.connect(self._update_settings)

        self.emulator_path_button = QPushButton(icon("folder.svg"), "", self)
        self.emulator_path_button.pressed.connect(self._get_emulator_path)

        self.command_arguments_input = QLineEdit(self)
        self.command_arguments_input.setPlaceholderText("%f")
        self.command_arguments_input.setText(SETTINGS["instaplay_arguments"])

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

        for key, value in POWERUPS.items():
            powerupIcon = self._load_from_png(value[POWERUPS_X], value[POWERUPS_Y])
            label = value[POWERUPS_NAME]

            self.powerup_combo_box.addItem(powerupIcon, value[POWERUPS_NAME], (value[POWERUPS_VALUE], value[POWERUPS_PWING]))

        self.powerup_combo_box.currentIndexChanged.connect(self._update_settings)
        self.powerup_combo_box.setCurrentIndex(0)

        command_layout.addWidget(self.powerup_combo_box)

        # ----------------------

        layout = QVBoxLayout(self)
        layout.addWidget(mouse_box)
        layout.addWidget(command_box)

        self.update()

    def update(self):
        self.command_label.setText(f" > {SETTINGS['instaplay_emulator']} {SETTINGS['instaplay_arguments']}")

    def _update_settings(self, _):
        SETTINGS["instaplay_emulator"] = self.emulator_command_input.text()
        SETTINGS["instaplay_arguments"] = self.command_arguments_input.text()

        if self.lmb_radio.isChecked():
            SETTINGS["resize_mode"] = RESIZE_LEFT_CLICK
        else:
            SETTINGS["resize_mode"] = RESIZE_RIGHT_CLICK

        SETTINGS["object_scroll_enabled"] = self._scroll_check_box.isChecked()

        SETTINGS["default_powerup"] = self.powerup_combo_box.currentData()
        print(SETTINGS["default_powerup"])

        self.update()

    def _get_emulator_path(self):
        path_to_emulator, _ = QFileDialog.getOpenFileName(self, caption="Select emulator executable")

        if not path_to_emulator:
            return

        self.emulator_command_input.setText(path_to_emulator)

    def _load_from_png(self, x: int, y: int) -> QIcon:
        image = png.copy(QRect(x * 16, y * 16, 16, 16))
        mask = image.createMaskFromColor(QColor(*MASK_COLOR).rgb(), Qt.MaskOutColor)
        image.setAlphaChannel(mask)

        pixmap = QPixmap.fromImage(image)
        icon = QIcon(pixmap)

        return icon

    def on_exit(self):
        save_settings()

        super(SettingsDialog, self).on_exit()


def show_settings():
    SettingsDialog().exec_()
