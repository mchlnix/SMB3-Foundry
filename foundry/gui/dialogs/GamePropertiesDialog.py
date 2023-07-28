from dataclasses import dataclass

from PySide6.QtCore import QSize
from PySide6.QtGui import QUndoStack
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QStackedWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from foundry import data_dir
from foundry.gui.dialogs.CustomDialog import CustomDialog
from foundry.gui.util import center_widget
from foundry.gui.widgets.Spinner import Spinner
from smb3parse.constants import BASE_OFFSET
from smb3parse.util import hex_int
from smb3parse.util.rom import PRG_BANK_SIZE, Rom

_PROP_PATH = data_dir / "game_properties.ini"


@dataclass
class _PropInfo:
    name: str = ""
    description: str = ""
    rom_address: int = 0
    min_value: int = 0
    max_value: int = 0
    base_value: int = 0
    is_subtracted: bool = False
    is_inverted: bool = False
    unit: str = ""

    def value_str(self, value):
        if self.is_inverted:
            value = 0x100 - value

        elif self.is_subtracted:
            value = self.base_value - value

        return f"{value} {self.unit}"


class _InfoWidget(QWidget):
    def __init__(self, rom: Rom, prop_info: _PropInfo):
        super().__init__()

        self._rom = rom
        self._prop_info = prop_info

        layout = QVBoxLayout(self)

        info_label = QLabel(prop_info.description)
        info_label.setWordWrap(True)

        edit_layout = QHBoxLayout()

        self._spinner = Spinner(maximum=prop_info.max_value)
        self._spinner.setMinimum(prop_info.min_value)

        decimal_label = QLabel()

        self._spinner.valueChanged.connect(lambda x: decimal_label.setText(prop_info.value_str(x)))

        edit_layout.addWidget(QLabel("Value:"))
        edit_layout.addStretch(1)
        edit_layout.addWidget(decimal_label)
        edit_layout.addWidget(self._spinner)

        layout.addWidget(info_label)
        layout.addLayout(edit_layout)
        layout.addStretch(1)
        layout.addWidget(
            QLabel(
                f"ROM Address: {prop_info.rom_address:#X} / "
                f"PRG_{(prop_info.rom_address - BASE_OFFSET) // PRG_BANK_SIZE:0>3}"
            )
        )

        self._read_current_value()

    def _read_current_value(self):
        self._spinner.setValue(self._rom.int(self._prop_info.rom_address))

    def save_value(self):
        self._rom.write(self._prop_info.rom_address, self._spinner.value())


class GamePropertiesDialog(CustomDialog):
    def __init__(self, parent, rom: Rom):
        super(GamePropertiesDialog, self).__init__(parent, "Game Properties")
        self._rom = rom

        self.setMinimumSize(QSize(600, 600))

        self.setLayout(QHBoxLayout())

        self._prop_tree = QTreeWidget(self)
        self._prop_tree.currentItemChanged.connect(self._on_item_changed)

        self._details_switcher = QStackedWidget(self)

        button_group = QDialogButtonBox()
        button_group.addButton(QDialogButtonBox.StandardButton.Cancel).clicked.connect(self.reject)
        button_group.addButton(QDialogButtonBox.StandardButton.Save).clicked.connect(self.accept)

        details_and_buttons_layout = QVBoxLayout()
        details_and_buttons_layout.addWidget(self._details_switcher, stretch=1)
        details_and_buttons_layout.addWidget(button_group)

        self.layout().addWidget(self._prop_tree, stretch=1)
        self.layout().addLayout(details_and_buttons_layout, stretch=1)

        self._prop_item_to_data: dict[QTreeWidgetItem, _PropInfo] = {}
        self._prop_info_widgets: dict[QTreeWidgetItem, _InfoWidget] = {}

        with _PROP_PATH.open("r") as prop_file:
            self._build_items(prop_file)

        if self._prop_item_to_data:
            self._prop_tree.setCurrentItem(list(self._prop_item_to_data.keys())[0])

        center_widget(self)

    def accept(self):
        for prop_widget in self._prop_info_widgets.values():
            prop_widget.save_value()

        return super().accept()

    def _on_item_changed(self, new_item: QTreeWidgetItem):
        if new_item not in self._prop_info_widgets:
            return

        self._details_switcher.setCurrentWidget(self._prop_info_widgets[new_item])

    def _build_items(self, prop_file):
        current_section_item = None
        current_prop_item = None

        for line in prop_file.readlines():
            line = line.strip()

            if line == "" or line.startswith((";", "!")):
                continue

            elif line.startswith("["):
                current_section_item = self._parse_section_header(line)
                current_section_item.setExpanded(True)

            elif line.startswith("caption "):
                current_prop_item = self._parse_property(current_section_item, line)

            elif line.startswith("info "):
                self._prop_item_to_data[current_prop_item].description = line.removeprefix("info ")

            elif line.startswith("type "):
                self._parse_property_values(current_prop_item, line)

            elif line.startswith("unit "):
                self._parse_unit(current_prop_item, line)

        self._make_setting_widgets()

    def _make_setting_widgets(self):
        for prop_item, prop_info in self._prop_item_to_data.items():
            info_widget = _InfoWidget(self._rom, prop_info)

            self._prop_info_widgets[prop_item] = info_widget
            self._details_switcher.addWidget(info_widget)

    def _parse_section_header(self, line):
        section_title = line.removeprefix("[").removesuffix("]")
        current_section_item = QTreeWidgetItem(self._prop_tree)
        current_section_item.setText(0, section_title)

        return current_section_item

    def _parse_property(self, current_section_item, line):
        if current_section_item is None:
            raise ValueError("No section was found, before a caption was set.")

        property_title = line.removeprefix("caption ")

        current_prop_item = QTreeWidgetItem(current_section_item)
        current_prop_item.setText(0, property_title)

        self._prop_item_to_data[current_prop_item] = _PropInfo(name=property_title)

        return current_prop_item

    def _parse_property_values(self, current_prop_item, line):
        if current_prop_item not in self._prop_item_to_data:
            raise ValueError("No caption was found, before type values were set.")

        data = self._prop_item_to_data[current_prop_item]

        line = line.removeprefix("type ")

        if line.startswith("SUB_"):
            data.is_subtracted = True

            line = line.removeprefix("SUB_")
            data.base_value, line = hex_int(line[:2]), line[2:]

        elif line.startswith("INV"):
            data.is_inverted = True
            line = line.removeprefix("INV")

        else:
            assert line.startswith("INT")
            line = line.removeprefix("INT")

        data.rom_address, data.min_value, data.max_value = map(hex_int, line.strip().split(" "))

    def _parse_unit(self, current_prop_item, line):
        if current_prop_item not in self._prop_item_to_data:
            raise ValueError("No caption was found, before type values were set.")

        line = line.removeprefix("unit ")

        self._prop_item_to_data[current_prop_item].unit = line.strip()

    @property
    def undo_stack(self) -> QUndoStack:
        return self.parent().window().findChild(QUndoStack, "undo_stack")
