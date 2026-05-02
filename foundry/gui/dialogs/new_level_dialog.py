"""Choose the object set for a brand-new level before creation begins.

This module owns the modal chooser that runs at the start of new-level
creation. It narrows the user to valid level object sets, explains why the
choice matters, and shows representative preview art so the later creation
workflow can proceed with one committed object-set decision.

See Also
--------
foundry.gui.dialogs.ObjectSetSelector
    Smaller object-set picker used by workflows that only need the numeric
    choice and not the themed preview surface.
foundry.gui.dialogs.LevelHeaderEditor
    Dialog that edits the next-area object set after a level already exists.
"""

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
)

from foundry import data_dir
from foundry.gui import OBJECT_SET_ITEMS
from foundry.gui.dialogs.CustomDialog import CustomDialog
from foundry.gui.localization import tr, tr_data_name
from smb3parse.constants import OBJECT_SET_NAMES

_PREVIEW_SIDE_LENGTH = 512

_EXAMPLE_IMAGE_PATH = data_dir / "level_previews"


def _object_set_item_text(object_set_index: int) -> str:
    """Format a translated object-set dropdown row.

    Parameters
    ----------
    object_set_index : int
        Stable SMB3 object-set index stored as combo user data.

    Returns
    -------
    str
        Display text combining the hexadecimal object-set id and localized name.
    """
    return f"{object_set_index:X} {tr_data_name('ObjectSet', OBJECT_SET_NAMES[object_set_index])}"


class NewLevelDialog(CustomDialog):
    """Pick the object set for a newly created level.

    The dialog explains that object-set choice determines the level's theme and
    object definitions, then previews a representative image for the selected
    set so the user can make that choice with visual context.

    Parameters
    ----------
    parent : QWidget | None
        Parent Qt widget that owns this object.

    Attributes
    ----------
    _EXAMPLE_IMAGES : list[QPixmap | None]
        Example preview images keyed by object set index.
    button_box : QDialogButtonBox
        Dialog buttons used to accept or reject the choice.
    explanation_label : QLabel
        Wrapped explanatory label describing why the choice is permanent.
    icon_label : QLabel
        Label that shows the selected object-set preview image.
    object_set_dropdown : QComboBox
        Dropdown containing selectable object sets.
    object_set_index : int
        Index of the selected object set in ``OBJECT_SET_ITEMS``.
    prompt_label : QLabel
        Short prompt label above the object-set explanation and dropdown.

    Notes
    -----
    Several object sets are removed from the dropdown because they are not
    valid choices for the new-level workflow.
    """

    def __init__(self, parent):
        """Build the new-level object-set chooser and preview.

        Construction preloads the representative object-set preview images,
        builds the explanatory text and filtered dropdown, wires the dialog
        buttons, and then leaves the chooser ready for ``_on_object_set_change``
        to keep the preview image synchronized with the selected object set.
        That makes the dialog a short staging step at the front of level
        creation: pick one valid object set with visual context, then let the
        caller continue with actual level construction.

        Parameters
        ----------
        parent : QWidget | None
            Parent Qt widget that owns this object.
        """
        super().__init__(parent, tr("Common", "new_level", "New Level"))

        self.object_set_index = 0

        self._EXAMPLE_IMAGES: list[QPixmap | None] = [
            None,
            QPixmap(_EXAMPLE_IMAGE_PATH / "Plains.png"),
            QPixmap(_EXAMPLE_IMAGE_PATH / "Dungeon.png"),
            QPixmap(_EXAMPLE_IMAGE_PATH / "Hilly.png"),
            QPixmap(_EXAMPLE_IMAGE_PATH / "Sky.png"),
            QPixmap(_EXAMPLE_IMAGE_PATH / "Piranha.png"),
            QPixmap(_EXAMPLE_IMAGE_PATH / "Water.png"),
            None,
            QPixmap(_EXAMPLE_IMAGE_PATH / "Pipes.png"),
            QPixmap(_EXAMPLE_IMAGE_PATH / "Desert.png"),
            QPixmap(_EXAMPLE_IMAGE_PATH / "Ship.png"),
            QPixmap(_EXAMPLE_IMAGE_PATH / "Giant.png"),
            QPixmap(_EXAMPLE_IMAGE_PATH / "Ice.png"),
            QPixmap(_EXAMPLE_IMAGE_PATH / "Cloudy.png"),
            QPixmap(_EXAMPLE_IMAGE_PATH / "Underground.png"),
            None,
        ]

        main_layout = QHBoxLayout(self)

        self.icon_label = QLabel()
        text_layout = QVBoxLayout()

        self.prompt_label = QLabel()

        self.explanation_label = QLabel()
        self.explanation_label.setWordWrap(True)

        self.object_set_dropdown = QComboBox()
        for object_set_index, _object_set_name in enumerate(OBJECT_SET_ITEMS):
            self.object_set_dropdown.addItem(_object_set_item_text(object_set_index), object_set_index)
        self.object_set_dropdown.currentIndexChanged.connect(self._on_object_set_change)

        self.object_set_dropdown.removeItem(0xF)  # No Spade Object Set
        self.object_set_dropdown.removeItem(0x7)  # No Mushroom House Object Set
        self.object_set_dropdown.removeItem(0x0)  # No Overworld Object Set

        self.button_box = QDialogButtonBox()
        self.button_box.addButton(QDialogButtonBox.StandardButton.Ok).clicked.connect(self.accept)
        self.button_box.addButton(QDialogButtonBox.StandardButton.Cancel).clicked.connect(self.reject)

        text_layout.addStretch()
        text_layout.addWidget(self.prompt_label)
        text_layout.addWidget(self.explanation_label)
        text_layout.addSpacing(20)
        text_layout.addWidget(self.object_set_dropdown)

        text_layout.addWidget(self.icon_label)
        text_layout.addSpacing(20)
        text_layout.addWidget(self.button_box)

        main_layout.addLayout(text_layout)
        self.retranslate_ui()

    def retranslate_ui(self) -> None:
        """Refresh new-level labels without changing the chosen object set.

        The dialog title, prompt, explanatory copy, and object-set row text are
        rebuilt from the active catalog. Combo-box ``itemData`` values and the
        current selection remain stable so creating the level still uses the
        same encoded object-set id after a language switch.
        """
        self.setWindowTitle(tr("Common", "new_level", "New Level"))
        self.prompt_label.setText(
            tr("Common", "help.select_object_set_first", "To create a new level, first select the Object Set.")
        )
        self.explanation_label.setText(
            tr(
                "Common",
                "help.new_level_object_set",
                "This will determine the level's theme, by selecting a specific set of objects, that follow a similar style. This cannot be changed.",
            )
        )
        for index in range(self.object_set_dropdown.count()):
            self.object_set_dropdown.setItemText(index, _object_set_item_text(self.object_set_dropdown.itemData(index)))

    def _on_object_set_change(self, _):
        """Update the preview image for the selected object set.

        Parameters
        ----------
        _ : int
            Dropdown index emitted by Qt.
        """
        self.object_set_index = self.object_set_dropdown.currentData()

        example_image = self._EXAMPLE_IMAGES[self.object_set_index]
        assert example_image is not None, "No example image for this object set"

        self.icon_label.setPixmap(example_image.scaled(_PREVIEW_SIDE_LENGTH, _PREVIEW_SIDE_LENGTH))
