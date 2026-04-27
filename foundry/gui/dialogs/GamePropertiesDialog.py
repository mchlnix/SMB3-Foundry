"""Edit advanced ROM-backed properties described by configuration metadata.

This module turns the descriptor file in ``game_properties.ini`` into a tree of
editable ROM settings, one detail widget per property, and a save path that
writes changed bytes back to the loaded ROM. It is the dialog-layer bridge
between declarative property metadata and the concrete widgets that let
maintainers inspect and patch advanced game settings.

See Also
--------
foundry.gui.dialogs.CustomDialog
    Base dialog behavior reused by this advanced settings editor.
foundry.gui.widgets.Spinner
    Raw-value editor used by each property widget.
"""

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
    """Describe one editable ROM-backed game property.

    Entries are parsed from ``game_properties.ini`` and define how a byte in the
    ROM should be displayed, bounded, transformed, and written back. Each
    instance moves through the dialog in three stages: parsed from the
    descriptor file, attached to a tree item, then consumed by ``_InfoWidget``
    to build the actual editor. The dataclass itself is intentionally passive;
    it carries enough metadata for the dialog tree, display-value formatter,
    and save path to agree on how one ROM byte should be presented.

    Attributes
    ----------
    base_value : int
        Base value used for subtractive display transforms.
    description : str
        Help text shown beside the property editor.
    is_inverted : bool
        Whether displayed values are inverted from the stored byte.
    is_subtracted : bool
        Whether displayed values are ``base_value - stored_byte``.
    max_value : int
        Maximum allowed byte value.
    min_value : int
        Minimum allowed byte value.
    name : str
        Property name shown in the tree.
    rom_address : int
        ROM address written by this property.
    unit : str
        Unit suffix shown with the decimal value.

    See Also
    --------
    _InfoWidget
        Builds the editable widget for one parsed property.
    GamePropertiesDialog
        Parses and organizes property metadata into the dialog tree.
    """

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
        """Format the user-facing value string for a stored byte.

        The dialog keeps the spinner on the raw ROM byte while labels use the
        descriptor's inverted or subtractive display transform, so this helper
        centralizes the translation shown beside the editor and the text that is
        recomputed on every spinner change. It is the formatting boundary
        between raw ROM byte state and the human-facing value displayed beside
        the editor.

        Parameters
        ----------
        value : int
            Raw byte value from the spinner or ROM.

        Returns
        -------
        str
            Transformed value plus unit suffix.
        """
        if self.is_inverted:
            value = 0x100 - value

        elif self.is_subtracted:
            value = self.base_value - value

        return f"{value} {self.unit}"


class _InfoWidget(QWidget):
    """Edit one ROM-backed game property.

    The widget shows the property description, a bounded spinner, the resolved
    display value, and the ROM/PRG address being edited. It is the bridge
    between descriptor-driven property metadata and an actual editor surface:
    ``_PropInfo`` describes how a byte should be interpreted, and this widget
    turns that description into a concrete read-edit-write workflow against the
    ROM object. That separation keeps the dialog extensible, because new
    properties can often be added in configuration rather than in widget code.

    Parameters
    ----------
    rom : Rom
        ROM data source used for game data lookups.
    prop_info : _PropInfo
            Parsed property metadata.

    Attributes
    ----------
    _prop_info : _PropInfo
        Parsed property metadata.
    _rom : Rom
        ROM object whose byte is edited.
    _spinner : Spinner
        Bounded editor for the raw stored value.

    See Also
    --------
    _PropInfo
        Descriptor object that supplies bounds, formatting, and ROM address
        information for this widget.
    GamePropertiesDialog
        Builds one info widget per editable property and saves them together.
    """

    def __init__(self, rom: Rom, prop_info: _PropInfo):
        """Create an editor for one parsed property.

        Construction runs in four phases. It first stores the ROM object and
        parsed descriptor so every later read, display transform, and write is
        tied to one source of truth. It then builds the static explanatory
        labels plus the bounded spinner row that will hold the staged raw byte.
        Next it wires the spinner's change signal to the decimal label so each
        staged edit immediately flows through ``_PropInfo.value_str`` before the
        user saves. Finally it performs the initial ROM read, which seeds the
        spinner, triggers that same display-update path, and leaves the widget
        fully synchronized before the dialog ever shows it. The constructor is
        therefore the whole open-time setup path for one property: read the ROM
        byte, stage edits in the spinner, reflect them through the descriptor's
        display transform, and leave ``save_value`` to commit the final staged
        byte later.

        Parameters
        ----------
        rom : Rom
            ROM data source used for game data lookups.
        prop_info : _PropInfo
            Parsed property metadata.
        """
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
        """Load the stored ROM byte into the spinner.

        ``Spinner`` emits its display update after the value is set.
        """
        self._spinner.setValue(self._rom.int(self._prop_info.rom_address))

    def save_value(self):
        """Write the spinner value back to ROM.

        Each property currently writes one byte at its configured ROM address.
        """
        self._rom.write(self._prop_info.rom_address, self._spinner.value())


class GamePropertiesDialog(CustomDialog):
    """Edit advanced ROM properties described by ``game_properties.ini``.

    The dialog parses a small INI-like descriptor file into a tree of editable
    ROM bytes. Selecting a property shows its detail editor; accepting the
    dialog writes every edited spinner value back to the ROM object.

    Parameters
    ----------
    parent : object
        Parent Qt widget that owns this object.
    rom : Rom
        ROM data source used for game data lookups.

    Attributes
    ----------
    _details_switcher : QStackedWidget
        Detail editor stack keyed by the selected tree item.
    _prop_info_widgets : dict[QTreeWidgetItem, _InfoWidget]
        Collection of prop info widgets maintained for dialog UI state.
    _prop_item_to_data : dict[QTreeWidgetItem, _PropInfo]
        Mapping from tree item to parsed property metadata.
    _prop_tree : QTreeWidget
        Tree containing sections and properties from the descriptor file.
    _rom : Rom
        ROM object edited by the dialog.
    """

    def __init__(self, parent, rom: Rom):
        """Build the game-properties tree and detail editors.

        Construction parses the descriptor file, creates the left-hand tree,
        creates one editor widget per property, and selects the first parsed
        property so the dialog opens with a valid detail view. The resulting
        dialog keeps tree navigation, per-property widgets, and final ROM writes
        separated until ``accept`` commits every edited value. In practice this
        constructor is the setup boundary that turns declarative property
        metadata into the full tree-navigation and stacked-editor state used by
        the dialog workflow.

        Parameters
        ----------
        parent : object
            Parent Qt widget that owns this object.
        rom : Rom
            ROM data source used for game data lookups.
        """
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
        """Save all property widgets before accepting the dialog.

        The tree selection does not imply a single edited property; every detail
        widget is asked to write its current value to the ROM.

        Returns
        -------
        object
            Result from ``QDialog.accept``.
        """
        for prop_widget in self._prop_info_widgets.values():
            prop_widget.save_value()

        return super().accept()

    def _on_item_changed(self, new_item: QTreeWidgetItem):
        """Show the detail widget for a selected property item.


        Parameters
        ----------
        new_item : QTreeWidgetItem
            Newly selected tree item.
        """
        if new_item not in self._prop_info_widgets:
            return

        self._details_switcher.setCurrentWidget(self._prop_info_widgets[new_item])

    def _build_items(self, prop_file):
        """Parse the property descriptor file into tree items.

        The descriptor format is section-oriented: section headers create tree
        groups, ``caption`` starts a property, and following ``info``, ``type``,
        and ``unit`` lines fill its metadata.

        Parameters
        ----------
        prop_file : TextIO
            Open descriptor file for game property metadata.
        """
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
        """Create one detail editor widget for each parsed property.

        Widgets are registered in the stacked layout using their matching tree
        item as the lookup key.
        """
        for prop_item, prop_info in self._prop_item_to_data.items():
            info_widget = _InfoWidget(self._rom, prop_info)

            self._prop_info_widgets[prop_item] = info_widget
            self._details_switcher.addWidget(info_widget)

    def _parse_section_header(self, line):
        """Parse a section header line into a tree section.

        Section items are organizational only; later ``caption`` entries attach
        editable properties beneath the most recently parsed section, which lets
        the descriptor file define dialog grouping without hard-coding widget
        layout in Python. This keeps grouping state in the parse workflow so
        later property lines can attach themselves to the correct tree branch.

        Parameters
        ----------
        line : str
            Descriptor line such as ``[Physics]``.

        Returns
        -------
        QTreeWidgetItem
            Created tree item for the section.
        """
        section_title = line.removeprefix("[").removesuffix("]")
        current_section_item = QTreeWidgetItem(self._prop_tree)
        current_section_item.setText(0, section_title)

        return current_section_item

    def _parse_property(self, current_section_item, line):
        """Parse a property caption line into a tree item.

        The new property item is attached to the containing section and initialized
        with a blank ``_PropInfo`` record that later descriptor lines fill in.

        Parameters
        ----------
        current_section_item : QTreeWidgetItem | None
            Section item that should contain the property.
        line : str
            Descriptor line beginning with ``caption``.

        Returns
        -------
        QTreeWidgetItem
            Created tree item for the property.

        Raises
        ------
        ValueError
            If the input data or current state is invalid.
        """
        if current_section_item is None:
            raise ValueError("No section was found, before a caption was set.")

        property_title = line.removeprefix("caption ")

        current_prop_item = QTreeWidgetItem(current_section_item)
        current_prop_item.setText(0, property_title)

        self._prop_item_to_data[current_prop_item] = _PropInfo(name=property_title)

        return current_prop_item

    def _parse_property_values(self, current_prop_item, line):
        """Parse value encoding and bounds for a property.

        Supported encodings include direct integer bytes, inverted byte display,
        and subtractive display based on a descriptor-provided base value.

        Parameters
        ----------
        current_prop_item : QTreeWidgetItem | None
            Property item whose metadata should be updated.
        line : str
            Descriptor line beginning with ``type``.

        Raises
        ------
        ValueError
            If the input data or current state is invalid.
        """
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
        """Parse the display unit for a property.

        Units affect only the derived human-facing value label; the stored ROM
        byte and spinner bounds remain unchanged.


        Parameters
        ----------
        current_prop_item : QTreeWidgetItem | None
            Property item whose unit should be updated.
        line : str
            Descriptor line beginning with ``unit``.

        Raises
        ------
        ValueError
            If the input data or current state is invalid.
        """
        if current_prop_item not in self._prop_item_to_data:
            raise ValueError("No caption was found, before type values were set.")

        line = line.removeprefix("unit ")

        self._prop_item_to_data[current_prop_item].unit = line.strip()

    @property
    def undo_stack(self) -> QUndoStack:
        """Expose the owning window's shared undo stack.

        The dialog currently writes values directly on accept, but exposing the
        undo stack keeps it aligned with other editor dialogs and gives callers
        the same integration point other advanced settings surfaces use. It is
        the dialog's bridge back into the main editor workflow when property
        editing eventually needs to coordinate with shared undo state.

        Returns
        -------
        QUndoStack
            Undo stack named ``undo_stack`` in the owning window.
        """
        return self.parent().window().findChild(QUndoStack, "undo_stack")
