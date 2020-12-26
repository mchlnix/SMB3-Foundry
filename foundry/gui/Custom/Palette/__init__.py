

from typing import Optional, List
from PySide2.QtWidgets import QGridLayout, QWidget, QHBoxLayout
from PySide2.QtGui import Qt

from foundry.gui.QCore import MARGIN_TIGHT
from foundry.gui.QCore.palette import DEFAULT_PALETTE_SET, DEFAULT_PALETTE
from foundry.gui.QToolButton import ColoredToolButton
from foundry.game.gfx.Palette import PaletteController, PaletteSet, Palette, Color
from foundry.core.Observables.ObservableDecorator import ObservableDecorator
from foundry.gui.QWidget import Widget
from foundry.core.Action.Action import Action
from foundry.core.Action.AbstractActionObject import AbstractActionObject


_palette_controller = PaletteController()


class PaletteSetEditor(Widget, AbstractActionObject):
    """A widget to help with editing a palette set"""
    palette_set_changed_action: Action  # Updated whenever the palette_set is changed

    def __init__(self, parent: Optional[QWidget], palette: Optional[PaletteSet] = DEFAULT_PALETTE_SET) -> None:
        from foundry.gui.Custom.Palette.NESPaletteSelector import ColorPickerButton
        Widget.__init__(self, parent)
        AbstractActionObject.__init__(self)
        self.parent = parent
        self.palette = palette

        self._set_up_layout()
        self._initialize_internal_observers()

    def _initialize_internal_observers(self) -> None:
        """Initializes internal observers for special events"""
        name = self.__class__.__name__

        def set_palette_closure(idx: int):
            """Returns a function that returns that sets a palette by palette index"""
            def set_palette(pal: Palette):
                """Sets a palette set by index"""
                return self._set_palette_set_color(idx, pal)
            return set_palette

        self.background_button.color_change_action.observer.attach_observer(
            lambda color: self._set_background_color(color), name=f"{name} Set Background Color"
        )
        for index, palette in enumerate(self.palette_editors):
            palette.palette_changed_action.observer.attach_observer(
                set_palette_closure(index), name=f"{name} Set Palette"
            )

    def _set_up_layout(self) -> None:
        """Returns the widgets layout"""
        from foundry.gui.Custom.Palette.NESPaletteSelector import ColorPickerButton
        self.palette_editors = []

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)

        self.background_button = ColorPickerButton.as_tiny(self, self.palette.background_color)
        hbox.addWidget(self.background_button)
        for idx in range(4):
            editor = PaletteEditor(self, self.palette[idx])
            self.palette_editors.append(editor)
            hbox.addWidget(editor)

        self.setLayout(hbox)

    def _push_palette_set(self) -> None:
        """Forces an update to the entire palette set"""
        for idx, palette in enumerate(self.palette_editors):
            palette._palette = self.palette[idx]
            palette._push_palette_to_buttons()

    def _set_palette_set_color(self, pal_idx: int, palette: Palette) -> None:
        self.palette[pal_idx] = palette
        self.palette_set_changed_action.observer(self.palette)

    def _set_background_color(self, color: Color):
        self.palette.background_color = color
        self.palette_set_changed_action.observer(self.palette)

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action("palette_set_changed", ObservableDecorator(lambda palette_set: palette_set, "Palette Set Updated")),
        ]


class PaletteEditor(Widget, AbstractActionObject):
    """A widget to help edit a single palette"""
    def __init__(self, parent: Optional[QWidget], palette: Optional[Palette] = DEFAULT_PALETTE) -> None:
        Widget.__init__(self, parent)
        AbstractActionObject.__init__(self)
        self.parent = parent
        self._palette = palette

        self._set_up_layout()
        self._initialize_internal_observers()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.parent}, {self.palette})"

    def _set_up_layout(self) -> None:
        """Returns the widgets layout"""
        from foundry.gui.Custom.Palette.NESPaletteSelector import ColorPickerButton
        self.buttons = []
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)
        for idx in range(3):
            button = ColorPickerButton.as_tiny(self, self.palette[idx])
            self.buttons.append(button)
            hbox.addWidget(button)
        self.setLayout(hbox)

    def _initialize_internal_observers(self) -> None:
        """Initializes internal observers for special events"""
        def set_palette_color_closure(index):
            """Returns a function that sets a palette color by index"""
            def set_palette_color(color: Color):
                """Sets a palette color by index"""
                self._set_palette_color(index, color)
            return set_palette_color

        for idx, button in enumerate(self.buttons):
            button.color_change_action.observer.attach_observer(
                set_palette_color_closure(idx), name="Set Palette Color"
            )

    def _set_palette_color(self, idx: int, color: Color) -> None:
        self.palette[idx] = color
        self.palette_changed_action.observer(self.palette)

    def _push_palette_to_buttons(self) -> None:
        """Pushes the palette onto the palette buttons"""
        for idx, button in enumerate(self.buttons):
            button._set_color(self.palette[idx])  # pushes the color to the button without updating the palette

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action("palette_changed", ObservableDecorator(lambda palette: palette, "Palette Updated")),
        ]

    @property
    def palette(self) -> Palette:
        """The palette we are controlling"""
        return self._palette

    @palette.setter
    def palette(self, palette: Palette) -> None:
        self._set_palette(palette)
        self.palette_changed_action(palette)

    def _set_palette(self, palette: Palette) -> None:
        """Sets the palette without making an update"""
        self._palette = palette
        self._push_palette_to_buttons()


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
