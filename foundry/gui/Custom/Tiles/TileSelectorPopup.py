

from typing import Optional, Callable
from PySide2.QtWidgets import QVBoxLayout

from foundry.gui.QDialog import Dialog

from .TileSelector import TileSelector


class ColorPickerPopup(Dialog):
    """Allows you to pick a custom color and returns the value"""

    def __init__(self, parent, title="Select a Tile", action: Optional[Callable] = None) -> None:
        Dialog.__init__(self, parent, title)

        self._set_up_layout()
        self._initialize_internal_observers(action)

    def _set_up_layout(self) -> None:
        """Returns the widgets layout"""
        layout = QVBoxLayout(self)
        self.tile_picker = TileSelector(self)
        layout.addWidget(self.tile_picker)
        self.setLayout(layout)

    def _initialize_internal_observers(self, action) -> None:
        """Initializes internal observers for special events"""
        name = self.__class__.__name__
        self.tile_picker.single_clicked_action.observer.attach_observer(
            lambda *_: self.accept(), name=f"{name} Closed"
        )

        if action is not None:
            self.tile_picker.single_clicked_action.observer.attach_observer(
                lambda value: action(value), name=f"{name} Returned Tile to Action"
            )