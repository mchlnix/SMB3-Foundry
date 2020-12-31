import qdarkstyle
from collections import namedtuple
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
from PySide2.QtCore import QRect
from foundry.game.gfx.objects.EnemyItem import MASK_COLOR

from foundry import icon, data_dir
from foundry.gui.QDialog import Dialog
from foundry.gui.HorizontalLine import HorizontalLine
from smb3parse.constants import (
    POWERUP_MUSHROOM,
    POWERUP_RACCOON,
    POWERUP_FIREFLOWER,
    POWERUP_TANOOKI,
    POWERUP_FROG,
    POWERUP_HAMMER,
)
from foundry.core.Settings.util import get_setting, set_setting, load_settings, save_settings
from foundry.core.util import RESIZE_LEFT_CLICK, RESIZE_RIGHT_CLICK, DRACULA_STYLE_SET, RETRO_STYLE_SET
from foundry.gui.QIcon.Icon import Icon

PowerUp = namedtuple('PowerUp', ['name', 'icon_name', 'index', 'pwing_enable'])

POWERUPS_PWING = 4
POWERUPS = [
    PowerUp("Small Mario", "small_mario", 0, False),
    PowerUp("Super Mario", "super_mario", POWERUP_MUSHROOM, False),
    PowerUp("Raccoon Mario", "raccoon_mario", POWERUP_RACCOON, False),
    PowerUp("Fire Mario", "fire_mario", POWERUP_FIREFLOWER, False),
    PowerUp("Tanooki Mario", "tanooki_mario", POWERUP_TANOOKI, False),
    PowerUp("Frog Mario", "frog_mario", POWERUP_FROG, False),
    PowerUp("Hammer Mario", "hammer_mario", POWERUP_HAMMER, False),
    PowerUp("Raccoon Mario with P-Wing", "pwing_mario", POWERUP_RACCOON, True),
    PowerUp("Tanooki Mario with P-Wing", "pwing_mario", POWERUP_TANOOKI, True)
]

png = QImage(str(data_dir / "gfx.png"))
png.convertTo(QImage.Format_RGB888)


class SettingsDialog(Dialog):
    def __init__(self, parent=None, sender=None):
        super(SettingsDialog, self).__init__(parent, "Settings")
        self.sender = sender

        mouse_box = QGroupBox("Mouse", self)
        mouse_box.setLayout(QVBoxLayout())

        scroll_layout = QHBoxLayout()

        label = QLabel("Scroll objects with mouse wheel:")
        label.setToolTip("Select an object and scroll up and down to change its type.")
        self._scroll_check_box = QCheckBox("Enabled")
        self._scroll_check_box.setChecked(get_setting("object_scroll_enabled", True))
        self._scroll_check_box.toggled.connect(self._update_settings)

        scroll_layout.addWidget(label)
        scroll_layout.addStretch(1)
        scroll_layout.addWidget(self._scroll_check_box)

        resize_layout = QHBoxLayout()

        self.lmb_radio = QRadioButton("Left Mouse Button")
        rmb_radio = QRadioButton("Right Mouse Button")

        self.lmb_radio.setChecked(get_setting("resize_mode", RESIZE_LEFT_CLICK) == RESIZE_LEFT_CLICK)
        rmb_radio.setChecked(get_setting("resize_mode", RESIZE_LEFT_CLICK) == RESIZE_RIGHT_CLICK)

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

        gui_style_box = QGroupBox("GUI", self)
        gui_style = QHBoxLayout(gui_style_box)

        self.retro_style_radio = QRadioButton("Retro")
        dracula_style_radio = QRadioButton("Dracula")

        self.retro_style_radio.setChecked(get_setting("gui_style", RETRO_STYLE_SET) == RETRO_STYLE_SET)
        dracula_style_radio.setChecked(get_setting("gui_style", RETRO_STYLE_SET) == DRACULA_STYLE_SET)

        self.retro_style_radio.toggled.connect(self._update_settings)

        radio_style_group = QButtonGroup()
        radio_style_group.addButton(self.retro_style_radio)
        radio_style_group.addButton(dracula_style_radio)

        gui_style.addWidget(QLabel("Style:"))
        gui_style.addWidget(self.retro_style_radio)
        gui_style.addWidget(dracula_style_radio)

        # ----------------------------------

        self.emulator_command_input = QLineEdit(self)
        self.emulator_command_input.setPlaceholderText("Path to emulator")
        self.emulator_command_input.setText(get_setting("instaplay_emulator", ""))

        self.emulator_command_input.textChanged.connect(self._update_settings)

        self.emulator_path_button = QPushButton(icon("folder.svg"), "", self)
        self.emulator_path_button.pressed.connect(self._get_emulator_path)

        self.command_arguments_input = QLineEdit(self)
        self.command_arguments_input.setPlaceholderText("%f")
        self.command_arguments_input.setText(get_setting("instaplay_arguments", ""))

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

        for powerup in POWERUPS:
            self.powerup_combo_box.addItem(Icon.as_custom(powerup.icon_name), powerup.name)

        self.powerup_combo_box.currentIndexChanged.connect(self._update_settings)

        self.powerup_combo_box.setCurrentIndex(get_setting("default_powerup", 1))

        command_layout.addWidget(self.powerup_combo_box)

        # ----------------------

        layout = QVBoxLayout(self)
        layout.addWidget(mouse_box)
        layout.addWidget(gui_style_box)
        layout.addWidget(command_box)

        self.update()

    def update(self):
        self.command_label.setText(f" > {get_setting('instaplay_emulator', '')} {get_setting('instaplay_arguments', '')}")

    def _update_settings(self, _):
        set_setting("instaplay_emulator", self.emulator_command_input.text())
        set_setting("instaplay_arguments", self.command_arguments_input.text())

        if self.lmb_radio.isChecked():
            set_setting("resize_mode", RESIZE_LEFT_CLICK)
        else:
            set_setting("resize_mode", RESIZE_RIGHT_CLICK)

        if self.retro_style_radio.isChecked():
            set_setting("gui_style", RETRO_STYLE_SET)
        else:
            set_setting("gui_style", DRACULA_STYLE_SET)

        if get_setting("gui_style", RETRO_STYLE_SET) == DRACULA_STYLE_SET:
            self.sender.setStyleSheet(qdarkstyle.load_stylesheet())
        else:
            self.setStyleSheet("")
            self.sender.setStyleSheet("")

        set_setting("object_scroll_enabled", self._scroll_check_box.isChecked())
        set_setting("default_powerup", self.powerup_combo_box.currentIndex())

        self.update()

    def _get_emulator_path(self):
        path_to_emulator, _ = QFileDialog.getOpenFileName(self, caption="Select emulator executable")

        if not path_to_emulator:
            return

        self.emulator_command_input.setText(path_to_emulator)

    @staticmethod
    def _load_from_png(x: int, y: int) -> QIcon:
        image = png.copy(QRect(x * 16, y * 16, 16, 16))
        mask = image.createMaskFromColor(QColor(*MASK_COLOR).rgb(), Qt.MaskOutColor)
        image.setAlphaChannel(mask)

        pixmap = QPixmap.fromImage(image)
        icon = QIcon(pixmap)

        return icon

    def on_exit(self):
        save_settings()

        super(SettingsDialog, self).on_exit()
