from PySide6.QtCore import QRect, QStandardPaths
from PySide6.QtGui import QColor, QIcon, QImage, QPixmap, Qt
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
from foundry.game.gfx.drawable import MASK_COLOR
from foundry.game.gfx.drawable.Block import Block
from foundry.gui import label_and_widget
from foundry.gui.CustomDialog import CustomDialog
from foundry.gui.HorizontalLine import HorizontalLine
from foundry.gui.settings import (
    GUI_STYLE,
    RESIZE_LEFT_CLICK,
    RESIZE_RIGHT_CLICK,
    Settings,
)
from smb3parse.constants import (
    POWERUP_FIREFLOWER,
    POWERUP_FROG,
    POWERUP_HAMMER,
    POWERUP_MUSHROOM,
    POWERUP_RACCOON,
    POWERUP_TANOOKI,
)

POWERUPS_NAME = 0
POWERUPS_X = 1
POWERUPS_Y = 2
POWERUPS_VALUE = 3
POWERUPS_PWING = 4
POWERUPS = [
    ("Small Mario", 32, 53, 0, False),
    ("Big Mario", 6, 48, POWERUP_MUSHROOM, False),
    ("Raccoon Mario", 57, 53, POWERUP_RACCOON, False),
    ("Fire Mario", 16, 53, POWERUP_FIREFLOWER, False),
    ("Tanooki Mario", 54, 53, POWERUP_TANOOKI, False),
    ("Frog Mario", 56, 53, POWERUP_FROG, False),
    ("Hammer Mario", 58, 53, POWERUP_HAMMER, False),
    # Even though P-Wing can *technically* be combined, it only really works with Raccoon and Tanooki suit
    ("Raccoon Mario with P-Wing", 55, 53, POWERUP_RACCOON, True),
    ("Tanooki Mario with P-Wing", 55, 53, POWERUP_TANOOKI, True),
]

png = QImage(str(data_dir / "gfx.png"))
png.convertTo(QImage.Format_RGB888)


default_dirs = {
    "User": QStandardPaths.writableLocation(QStandardPaths.HomeLocation),
    "Desktop": QStandardPaths.writableLocation(QStandardPaths.DesktopLocation),
    "Documents": QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation),
    "Downloads": QStandardPaths.writableLocation(QStandardPaths.DownloadLocation),
    "Custom": "",
}


class SettingsDialog(CustomDialog):
    def __init__(self, settings: Settings, parent=None):
        super(SettingsDialog, self).__init__(parent, "Settings")

        self.settings = settings

        # -----------------------------------------------
        # Online Section

        online_box = QGroupBox("Online", self)
        online_box.setLayout(QVBoxLayout())

        self._update_check_box = QCheckBox("Enabled")
        self._update_check_box.setChecked(self.settings.value("editor/update_on_startup"))
        self._update_check_box.toggled.connect(self._update_settings)

        online_box.layout().addLayout(
            label_and_widget(
                "Check for Updates on Startup:",
                self._update_check_box,
                tooltip="Checks the Repository for a new Version when the Editor is started.",
            )
        )

        # -----------------------------------------------
        # Mouse Section

        mouse_box = QGroupBox("Mouse", self)
        mouse_box.setLayout(QVBoxLayout())

        self._scroll_check_box = QCheckBox("Enabled")
        self._scroll_check_box.setChecked(self.settings.value("editor/object_scroll_enabled"))
        self._scroll_check_box.toggled.connect(self._update_settings)

        mouse_box.layout().addLayout(
            label_and_widget(
                "Scroll objects with mouse wheel:",
                self._scroll_check_box,
                tooltip="Select an object and scroll up and down to change its type.",
            )
        )

        self._tooltip_check_box = QCheckBox("Enabled")
        self._tooltip_check_box.setChecked(self.settings.value("level view/object_tooltip_enabled"))
        self._tooltip_check_box.toggled.connect(self._update_settings)

        mouse_box.layout().addLayout(
            label_and_widget(
                "Show object names on hover:",
                self._tooltip_check_box,
                tooltip="When hovering your cursor over an object in a level, "
                "its name and position is shown in a tooltip.",
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

        resize_layout = QHBoxLayout()
        resize_layout.addWidget(QLabel("Object resize mode:"))
        resize_layout.addStretch(1)
        resize_layout.addWidget(self.lmb_radio)
        resize_layout.addWidget(rmb_radio)

        mouse_box.layout().addLayout(resize_layout)

        # -----------------------------------------------
        # GUI Section

        self.gui_box = QGroupBox("GUI", self)
        QVBoxLayout(self.gui_box)

        style_layout = QHBoxLayout()

        style_layout.addWidget(QLabel("Style:"))
        style_layout.addStretch(1)

        for gui_style in GUI_STYLE.keys():
            gui_style = gui_style.capitalize()

            style_radio_button = QRadioButton(gui_style)
            style_radio_button.setChecked(self.settings.value("editor/gui_style") == GUI_STYLE[gui_style.upper()]())
            style_radio_button.toggled.connect(self._update_settings)

            style_layout.addWidget(style_radio_button)

        self.gui_box.layout().addLayout(style_layout)

        path_layout = QHBoxLayout()

        self.path_dropdown = path_dropdown = QComboBox(self)
        path_dropdown.addItems(default_dirs.keys())
        path_dropdown.setCurrentText(self.settings.value("editor/default dir"))
        path_dropdown.currentTextChanged.connect(self.on_dropdown)

        path_layout.addWidget(QLabel("Default path:"))
        path_layout.addWidget(path_dropdown)

        self.gui_box.layout().addLayout(path_layout)

        default_dir_layout = QHBoxLayout()

        self.default_dir_label = QLabel()

        self.default_dir_button = QPushButton(icon("folder.svg"), "", self)
        self.default_dir_button.pressed.connect(self._get_default_dir)

        default_dir_layout.addWidget(self.default_dir_label, stretch=1)
        default_dir_layout.addWidget(self.default_dir_button)

        self.gui_box.layout().addLayout(default_dir_layout)

        # -----------------------------------------------
        # Emulator Command Section

        self.emulator_command_input = QLineEdit(self)
        self.emulator_command_input.setPlaceholderText("Path to emulator")
        self.emulator_command_input.setText(self.settings.value("editor/instaplay_emulator"))

        self.emulator_command_input.textChanged.connect(self._update_settings)

        self.emulator_path_button = QPushButton(icon("folder.svg"), "", self)
        self.emulator_path_button.pressed.connect(self._get_emulator_path)

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
            powerup_icon = self._load_from_png(x, y)

            self.powerup_combo_box.addItem(powerup_icon, name)

        self.powerup_combo_box.setCurrentIndex(self.settings.value("editor/default_powerup"))
        self.powerup_combo_box.currentIndexChanged.connect(self._update_settings)

        command_layout.addWidget(self.powerup_combo_box)

        # ----------------------

        layout = QVBoxLayout(self)
        layout.addWidget(online_box)
        layout.addWidget(mouse_box)
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

        if self.lmb_radio.isChecked():
            self.settings.setValue("editor/resize_mode", RESIZE_LEFT_CLICK)
        else:
            self.settings.setValue("editor/resize_mode", RESIZE_RIGHT_CLICK)

        # setup style sheets
        for child_widget in self.gui_box.children():
            if isinstance(child_widget, QRadioButton):
                if child_widget.isChecked():
                    selected_gui_style = child_widget.text().upper()

                    loaded_style_sheet = GUI_STYLE[selected_gui_style]()
                    self.settings.setValue("editor/gui_style", loaded_style_sheet)

                    self.parent().setStyleSheet(self.settings.value("editor/gui_style"))
                    break

        self.settings.setValue("editor/default dir", self.path_dropdown.currentText())
        if self.path_dropdown.currentText() == "Custom":
            self.settings.setValue("editor/custom default dir path", self.default_dir_label.text())

        self.settings.setValue("editor/default dir path", self.default_dir_label.text())

        self.settings.setValue("editor/update_on_startup", self._update_check_box.isChecked())
        self.settings.setValue("editor/object_scroll_enabled", self._scroll_check_box.isChecked())
        self.settings.setValue("level view/object_tooltip_enabled", self._tooltip_check_box.isChecked())

        self.settings.setValue("editor/default_powerup", self.powerup_combo_box.currentIndex())

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

    @staticmethod
    def _load_from_png(x: int, y: int) -> QIcon:
        image = png.copy(QRect(x * Block.SIDE_LENGTH, y * Block.SIDE_LENGTH, Block.SIDE_LENGTH, Block.SIDE_LENGTH))
        mask = image.createMaskFromColor(QColor(*MASK_COLOR).rgb(), Qt.MaskOutColor)
        image.setAlphaChannel(mask)

        pixmap = QPixmap.fromImage(image)
        icon_from_png = QIcon(pixmap)

        return icon_from_png

    def on_exit(self):
        self.settings.sync()

        super(SettingsDialog, self).on_exit()
