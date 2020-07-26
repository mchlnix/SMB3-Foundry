

from typing import Optional, List
from PySide2.QtWidgets import QGridLayout, QWidget, QLayout, QHBoxLayout
from PySide2.QtGui import Qt

from foundry.gui.QCore import MARGIN_TIGHT
from foundry.gui.QToolButton import ColoredToolButton
from foundry.game.gfx.Palette import PaletteController, PaletteSet, Palette, Color
from foundry.decorators.Observer import Observed
from foundry.gui.QWidget import Widget
from foundry.gui.QCore.Action import Action, AbstractActionObject


_palette_controller = PaletteController()
_default_color_index = 0
_default_color = Color(0, 0, 0)
_default_palette = Palette(_default_color, _default_color, _default_color, _default_color)
_default_palette_set = PaletteSet(_default_palette, _default_palette, _default_palette, _default_palette)


class PaletteSetEditor(Widget, AbstractActionObject):
    """A widget to help with editing a palette set"""

    def __init__(self, parent: Optional[QWidget], palette: Optional[PaletteSet] = _default_palette_set) -> None:
        from foundry.gui.Custom.Palette.NESPaletteSelector import ColorPickerButton
        Widget.__init__(self, parent)
        AbstractActionObject.__init__(self)
        self.parent = parent
        self.palette = palette
        self.palette_set_changed_action.observer.attach(lambda *_: print(self.palette))

        self.palette_editors = []
        hbox = QHBoxLayout()
        hbox.setSizeConstraint(QLayout.SetFixedSize)
        hbox.setSpacing(MARGIN_TIGHT)

        self.background_button = ColorPickerButton.as_tiny(self, self.palette[0][0])
        self.background_button.color_change_action.observer.attach(
            lambda *_: self._set_palette_set_color(0, 0, self.background_button.color)
        )
        hbox.addWidget(self.background_button)

        for idx in range(4):
            editor = PaletteEditor(self, self.palette[idx])
            editor.palette_changed_action.observer.attach(lambda pal, i=idx: self._set_palette_set_palette(i, pal))
            self.palette_editors.append(editor)
            hbox.addWidget(editor)
        self.setLayout(hbox)

    def _set_palette_set_color(self, pal_idx, idx, color) -> None:
        p_set = list(self.palette)
        p = list(p_set[pal_idx])
        p[idx] = color
        p_set[pal_idx] = Palette(p[0], p[1], p[2], p[3])
        self.palette = PaletteSet(p_set[0], p_set[1], p_set[2], p_set[3])
        self.palette_set_changed_action.observer(self.palette)

    def _set_palette_set_palette(self, pal_idx: int, palette: Palette):
        p_set = list(self.palette)
        p_set[pal_idx] = palette
        self.palette = PaletteSet(p_set[0], p_set[1], p_set[2], p_set[3])

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action("palette_set_changed", Observed(lambda palette_set: palette_set)),
        ]


class PaletteEditor(Widget, AbstractActionObject):
    """A widget to help edit a single palette"""
    def __init__(self, parent: Optional[QWidget], palette: Optional[Palette] = _default_palette) -> None:
        Widget.__init__(self, parent)
        AbstractActionObject.__init__(self)
        self.parent = parent
        self.palette = palette

        self._set_up_layout()
        self._initialize_internal_observers()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.parent}, {self.palette})"

    def _set_up_layout(self) -> None:
        """Returns the widgets layout"""
        from foundry.gui.Custom.Palette.NESPaletteSelector import ColorPickerButton
        self.buttons = []
        hbox = QHBoxLayout()
        hbox.setSizeConstraint(QLayout.SetFixedSize)
        hbox.setSpacing(0)
        for idx in range(3):
            button = ColorPickerButton.as_tiny(self, idx)
            self.buttons.append(button)
            hbox.addWidget(button)
        self.setLayout(hbox)

    def _initialize_internal_observers(self) -> None:
        """Initializes internal observers for special events"""
        for idx, button in enumerate(self.buttons):
            button.color_change_action.observer.attach(
                lambda color, i=idx: self._set_palette_color(i, color)
            )

    def _set_palette_color(self, idx, color) -> None:
        p = list(self.palette)
        p[idx] = color
        self.palette = Palette(p[0], p[1], p[2], p[3])
        self.palette_changed_action.observer(self.palette)

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action("palette_changed", Observed(lambda palette: palette)),
        ]


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
        for idx, button in enumerate(self.buttons):
            button.clicked_action.observer.attach(
                lambda *_, btn=button: self.color_selected_action.observer(getattr(btn, "color")))
            button.clicked_action.observer.attach(
                lambda *_, i=idx: self.color_index_selected_action.observer(i)
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
        return [
            Action("color_selected", Observed(lambda color: color)),
            Action("color_index_selected", Observed(lambda color_idx: color_idx))
        ]
