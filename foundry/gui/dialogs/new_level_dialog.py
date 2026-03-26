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

_PREVIEW_SIDE_LENGTH = 512

_EXAMPLE_IMAGE_PATH = data_dir / "level_previews"


class NewLevelDialog(CustomDialog):
    def __init__(self, parent):
        super().__init__(parent, "New Level")

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

        prompt_label = QLabel("To create a new level, first select the Object Set.")

        explanation_label = QLabel(
            "This will determine the level's theme, by selecting a specific set of objects, that follow a similar "
            "style. This cannot be changed."
        )
        explanation_label.setWordWrap(True)

        self.object_set_dropdown = QComboBox()
        self.object_set_dropdown.addItems(OBJECT_SET_ITEMS)
        self.object_set_dropdown.currentIndexChanged.connect(self._on_object_set_change)

        self.object_set_dropdown.removeItem(0xF)  # No Spade Object Set
        self.object_set_dropdown.removeItem(0x7)  # No Mushroom House Object Set
        self.object_set_dropdown.removeItem(0x0)  # No Overworld Object Set

        self.button_box = QDialogButtonBox()
        self.button_box.addButton(QDialogButtonBox.StandardButton.Ok).clicked.connect(self.accept)
        self.button_box.addButton(QDialogButtonBox.StandardButton.Cancel).clicked.connect(self.reject)

        text_layout.addStretch()
        text_layout.addWidget(prompt_label)
        text_layout.addWidget(explanation_label)
        text_layout.addSpacing(20)
        text_layout.addWidget(self.object_set_dropdown)

        text_layout.addWidget(self.icon_label)
        text_layout.addSpacing(20)
        text_layout.addWidget(self.button_box)

        main_layout.addLayout(text_layout)

    def _on_object_set_change(self, _):
        new_text = self.object_set_dropdown.currentText()

        self.object_set_index = OBJECT_SET_ITEMS.index(new_text)

        example_image = self._EXAMPLE_IMAGES[self.object_set_index]
        assert example_image is not None, "No example image for this object set"

        self.icon_label.setPixmap(example_image.scaled(_PREVIEW_SIDE_LENGTH, _PREVIEW_SIDE_LENGTH))
