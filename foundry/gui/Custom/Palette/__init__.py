from typing import Optional, List
from PySide2.QtWidgets import QGridLayout, QWidget
from PySide2.QtGui import Qt

from foundry.gui.QCore import MARGIN_TIGHT
from foundry.gui.QToolButton import ColoredToolButton
from foundry.game.gfx.Palette import PaletteController
from foundry.core.Observables.ObservableDecorator import ObservableDecorator
from foundry.gui.QWidget import Widget
from foundry.core.Action.Action import Action
from foundry.core.Action.AbstractActionObject import AbstractActionObject


_palette_controller = PaletteController()


class ColorPicker(Widget, AbstractActionObject):
    """A widget to help with picking a NES color"""
    def __init__(self, parent: Optional[QWidget]) -> None:
        Widget.__init__(self, parent)
        AbstractActionObject.__init__(self)

        self._set_up_layout()
        self._initialize_internal_observers()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.parent})"

    def _initialize_internal_observers(self) -> None:
        """Initializes internal observers for special events"""
        def update_color_closure(btn: ColoredToolButton):
            """A closure for a updating a color of a given button"""
            def get_button_color(*_):
                """Update the color of a given button"""
                self.color_selected_action.observer(btn.color)
            return get_button_color

        def update_button_clicked_closure(idx: int):
            """Returns a function to get the index of a button"""
            def update_button_clicked(*_):
                """Returns the index of a button"""
                self.color_index_selected_action(idx)
            return update_button_clicked

        for index, button in enumerate(self.buttons):
            button.clicked_action.observer.attach_observer(
                update_color_closure(button), name="Get Button Color"
            )
            button.clicked_action.observer.attach_observer(
                update_button_clicked_closure(index), name="Get Button Index"
            )

    def _set_up_layout(self) -> None:
        """Returns the widgets layout"""
        self.buttons = []
        grid_layout = QGridLayout()
        grid_layout.setSpacing(MARGIN_TIGHT)
        grid_layout.setDefaultPositioning(0x10, Qt.Horizontal)
        for idx in range(0x40):
            button = ColoredToolButton.as_tiny(self, _palette_controller.colors[idx])
            self.buttons.append(button)
            grid_layout.addWidget(button, row=idx % 0x10, column=idx // 0x10)

        self.setLayout(grid_layout)

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        name = self.__class__.__name__
        return [
            Action("color_selected", ObservableDecorator(lambda color: color, f"{name} Color Selected")),
            Action("color_index_selected", ObservableDecorator(
                lambda color_idx: color_idx, f"{name} Color Index Selected"
            ))
        ]
