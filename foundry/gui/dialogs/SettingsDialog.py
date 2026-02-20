from dataclasses import dataclass

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
    POWERUP_RACCOON,
    POWERUP_TANOOKI,
)

POWERUPS_NAME = 0
POWERUPS_X = 1
POWERUPS_Y = 2
POWERUPS_VALUE = 3
POWERUPS_PWING = 4


@dataclass
class PowerupEntry:
    description: str
    png_x: int
    png_y: int
    power_up_code: int
    has_p_wing: bool

    def to_tuple(self):
        return self.description, self.png_x, self.png_y, self.power_up_code, self.has_p_wing

    def __iter__(self):
        return iter(self.to_tuple())


POWERUPS = [
    PowerupEntry(_("Small Mario"), 32, 53, 0, False),
    PowerupEntry(_("Big Mario"), 6, 48, POWERUP_MUSHROOM, False),
    PowerupEntry(_("Raccoon Mario"), 57, 53, POWERUP_RACCOON, False),
    PowerupEntry(_("Fire Mario"), 16, 53, POWERUP_FIREFLOWER, False),
    PowerupEntry(_("Tanooki Mario"), 54, 53, POWERUP_TANOOKI, False),
    PowerupEntry(_("Frog Mario"), 56, 53, POWERUP_FROG, False),
    PowerupEntry(_("Hammer Mario"), 58, 53, POWERUP_HAMMER, False),
    # Even though P-Wing can *technically* be combined, it only really works with Raccoon and Tanooki suit
    PowerupEntry(_("Raccoon Mario with P-Wing"), 55, 53, POWERUP_RACCOON, True),
    PowerupEntry(_("Tanooki Mario with P-Wing"), 55, 53, POWERUP_TANOOKI, True),
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
        super(SettingsDialog, self).__init__(parent, _("Settings"))

        self.settings = settings

        # Online Section
        # -----------------------------------------------

        online_box = QGroupBox(_("Online"), self)
        layout = QVBoxLayout()
        online_box.setLayout(layout)

        self._update_check_box = QCheckBox(_("Enabled"))
        self._update_check_box.setChecked(self.settings.value("editor/update_on_startup"))
        self._update_check_box.toggled.connect(self._update_settings)

        layout.addLayout(
            label_and_widget(
                _("Check for Updates on Startup:"),
                self._update_check_box,
                tooltip=_("Checks the Repository for a new Version when the Editor is started."),
            )
        )

        # Mouse Section
        # -----------------------------------------------

        mouse_box = QGroupBox(_("Mouse"), self)
        layout = QVBoxLayout()
        mouse_box.setLayout(layout)

        self._scroll_check_box = QCheckBox(_("Enabled"))
        self._scroll_check_box.setChecked(self.settings.value("editor/object_scroll_enabled"))
        self._scroll_check_box.toggled.connect(self._update_settings)

        layout.addLayout(
            label_and_widget(
                _("Scroll objects with mouse wheel:"),
                self._scroll_check_box,
                tooltip=_("Select an object and scroll up and down to change its type."),
            )
        )

        self._tooltip_check_box = QCheckBox(_("Enabled"))
        self._tooltip_check_box.setChecked(self.settings.value("level view/object_tooltip_enabled"))
        self._tooltip_check_box.toggled.connect(self._update_settings)

        layout.addLayout(
            label_and_widget(
                _("Show object names on hover:"),
                self._tooltip_check_box,
                tooltip=_(
                    "When hovering your cursor over an object in a level, "
                    "its name and position is shown in a tooltip."
                ),
            )
        )

        self.lmb_radio = QRadioButton(_("Left Mouse Button"))
        rmb_radio = QRadioButton(_("Right Mouse Button"))

        self.lmb_radio.setChecked(self.settings.value("editor/resize_mode") == RESIZE_LEFT_CLICK)
        rmb_radio.setChecked(self.settings.value("editor/resize_mode") == RESIZE_RIGHT_CLICK)

        self.lmb_radio.toggled.connect(self._update_settings)

        radio_group = QButtonGroup()
        radio_group.addButton(self.lmb_radio)
        radio_group.addButton(rmb_radio)

        resize_layout = label_and_widget(_("Object resize mode:"), self.lmb_radio, rmb_radio)
        layout.addLayout(resize_layout)

        # GUI Section
        # -----------------------------------------------

        self.gui_box = QGroupBox(_("GUI"), self)
        layout = QVBoxLayout()
        self.gui_box.setLayout(layout)

        self.ask_for_level_management_check_box = QCheckBox(_("Enabled"))
        self.ask_for_level_management_check_box.setChecked(self.settings.value("editor/ask_for_level_management"))
        self.ask_for_level_management_check_box.stateChanged.connect(self._update_settings)

        self.gui_box.layout().addLayout(
            label_and_widget(
                _("Ask for Automatic Level Management when opening a new ROM:"),
                self.ask_for_level_management_check_box,
                tooltip=_(
                    "Should the editor ask to enable Automatic Level Management when opening a new ROM "
                    "that isn't managed yet?"
                ),
            )
        )

        self.level_highlight_check_box = QCheckBox(_("Enabled"))
        self.level_highlight_check_box.setChecked(self.settings.value("world view/show level pointers"))
        self.level_highlight_check_box.stateChanged.connect(self._update_settings)

        level_highlight_layout = label_and_widget(
            _("Highlight Levels in LevelSelector World Maps:"), self.level_highlight_check_box
        )
        self.gui_box.layout().addLayout(level_highlight_layout)

        style_choices = []

        for gui_style in GUI_STYLE.keys():
            gui_style = gui_style.capitalize()

            style_radio_button = QRadioButton(gui_style)
            style_radio_button.setChecked(self.settings.value("editor/gui_style") == GUI_STYLE[gui_style.upper()]())
            style_radio_button.toggled.connect(self._update_settings)

            style_choices.append(style_radio_button)

        style_layout = label_and_widget(_("Style:"), *style_choices)
        layout.addLayout(style_layout)

        path_layout = QHBoxLayout()

        self.path_dropdown = path_dropdown = QComboBox(self)
        path_dropdown.addItems(default_dirs.keys())
        path_dropdown.setCurrentText(self.settings.value("editor/default dir"))
        path_dropdown.currentTextChanged.connect(self.on_dropdown)

        path_layout.addWidget(QLabel(_("Default path:")))
        path_layout.addWidget(path_dropdown)

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
        self.emulator_command_input.setPlaceholderText(_("Path to emulator"))
        self.emulator_command_input.setText(self.settings.value("editor/instaplay_emulator"))

        self.emulator_command_input.textChanged.connect(self._update_settings)

        self.emulator_path_button = QPushButton(icon("folder.svg"), "", self)
        self.emulator_path_button.clicked.connect(self._get_emulator_path)

        self.command_arguments_input = QLineEdit(self)
        self.command_arguments_input.setPlaceholderText("%f")
        self.command_arguments_input.setText(self.settings.value("editor/instaplay_arguments"))

        self.command_arguments_input.textEdited.connect(self._update_settings)

        self.command_label = QLabel()

        command_box = QGroupBox(_("Emulator"), self)
        command_layout = QVBoxLayout(command_box)

        command_layout.addWidget(QLabel(_('Emulator command or "path to exe":')))

        command_input_layout = QHBoxLayout()
        command_input_layout.addWidget(self.emulator_command_input)
        command_input_layout.addWidget(self.emulator_path_button)

        command_layout.addLayout(command_input_layout)
        command_layout.addWidget(QLabel(_("Command arguments (%f will be replaced with rom path):")))
        command_layout.addWidget(self.command_arguments_input)
        command_layout.addWidget(QLabel(_("Command used to play the rom:")))
        command_layout.addWidget(self.command_label)

        command_layout.addWidget(HorizontalLine())

        command_layout.addWidget(QLabel(_("Power up of Mario when playing level:")))
        self.powerup_combo_box = QComboBox()

        for name, x, y, value, p_wing in POWERUPS:
            powerup_icon = self._load_from_png(x, y)

            self.powerup_combo_box.addItem(powerup_icon, name)

        self.powerup_combo_box.setCurrentIndex(self.settings.value("editor/default_powerup"))
        self.powerup_combo_box.currentIndexChanged.connect(self._update_settings)

        self.starman_checkbox = QCheckBox()
        self.starman_checkbox.setIcon(self._load_from_png(18, 53))
        self.starman_checkbox.setChecked(self.settings.value("editor/powerup_starman"))
        self.starman_checkbox.stateChanged.connect(self._update_settings)

        powerup_layout = QHBoxLayout()

        powerup_layout.addWidget(self.powerup_combo_box, stretch=1)
        powerup_layout.addWidget(self.starman_checkbox)

        command_layout.addLayout(powerup_layout)

        self.skip_title_screen_cb = QCheckBox(_("Enabled"))
        self.skip_title_screen_cb.setChecked(self.settings.value("editor/instaplay_skip_title_screen"))
        self.skip_title_screen_cb.stateChanged.connect(self._update_settings)

        command_layout.addLayout(label_and_widget(_("Instaplay skips Title Screen"), self.skip_title_screen_cb))

        # -----------------------------------------------

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
        self.settings.setValue("editor/instaplay_skip_title_screen", self.skip_title_screen_cb.isChecked())

        if self.lmb_radio.isChecked():
            self.settings.setValue("editor/resize_mode", RESIZE_LEFT_CLICK)
        else:
            self.settings.setValue("editor/resize_mode", RESIZE_RIGHT_CLICK)

        self.settings.setValue("editor/ask_for_level_management", self.ask_for_level_management_check_box.isChecked())
        self.settings.setValue("world view/show level pointers", self.level_highlight_check_box.isChecked())

        # set up style sheets
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
        self.settings.setValue("editor/powerup_starman", self.starman_checkbox.isChecked())

        self.update()

    def _get_emulator_path(self):
        path_to_emulator, __ = QFileDialog.getOpenFileName(
            self,
            caption=_("Select emulator executable"),
            dir=QStandardPaths.writableLocation(QStandardPaths.ApplicationsLocation),
        )

        if not path_to_emulator:
            return

        self.emulator_command_input.setText(path_to_emulator)

    def _get_default_dir(self):
        path_to_roms = QFileDialog.getExistingDirectory(
            self,
            caption=_("Select Rom directory"),
            dir=QStandardPaths.writableLocation(QStandardPaths.HomeLocation),
        )

        if not path_to_roms:
            return

        self.path_dropdown.setCurrentText(_("Custom"))
        self.default_dir_label.setText(path_to_roms)

        self._update_settings()

    def on_dropdown(self, new_text):
        if new_text == _("Custom"):
            self.default_dir_label.setText(self.settings.value("editor/custom default dir path"))
        elif new_text in default_dirs:
            self.default_dir_label.setText(default_dirs[new_text])

        self._update_settings()

    @staticmethod
    def _load_from_png(x: int, y: int) -> QIcon:
        image = png.copy(
            QRect(
                x * Block.SIDE_LENGTH,
                y * Block.SIDE_LENGTH,
                Block.SIDE_LENGTH,
                Block.SIDE_LENGTH,
            )
        )
        mask = image.createMaskFromColor(QColor(*MASK_COLOR).rgb(), Qt.MaskMode.MaskOutColor)
        image.setAlphaChannel(mask)

        pixmap = QPixmap.fromImage(image)
        icon_from_png = QIcon(pixmap)

        return icon_from_png

    def on_exit(self):
        self.settings.sync()

        super(SettingsDialog, self).on_exit()
