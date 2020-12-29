

from typing import Optional, List
from PySide2.QtWidgets import QWidget, QGridLayout, QVBoxLayout
from PySide2.QtGui import Qt

from foundry.gui.QLabel import Label
from foundry.core.Observables.ObservableDecorator import ObservableDecorator
from foundry.gui.QWidget import Widget
from foundry.core.Action.Action import Action
from foundry.core.Action.AbstractActionObject import AbstractActionObject
from foundry.gui.QSpinner.HexSpinner import HexSpinner
from foundry.gui.QCheckBox.SpriteFlipCheckbox import SpriteFlipCheckbox
from foundry.game.gfx.objects.objects.LevelObjectDefinition import SpriteGraphic, Animation


class AnimationWidget(Widget, AbstractActionObject):
    def __init__(self, parent: Optional[QWidget], name: str, animation: Animation) -> None:
        Widget.__init__(self, parent)
        AbstractActionObject.__init__(self)
        self.name = name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.parent}, {self.name}, {self._sprite_graphic})"

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action("graphic_changed", ObservableDecorator(lambda graphic: graphic)),
        ]

    def _initialize_internal_observers(self) -> None:
        """Initializes internal observers for special events"""
        self.graphic_spinner.value_changed_action.observer.attach_observer(lambda *_: self._update_graphic())
        self.mirror_checkbox.values_changed_action.observer.attach_observer(lambda *_: self._update_graphic())

    def _update_graphic(self) -> None:
        self._sprite_graphic = SpriteGraphic(
            self.graphic_spinner.value(),
            self.mirror_checkbox.horizontal_flip,
            self.mirror_checkbox.vertical_flip
        )

        self.graphic_changed_action.observer(self.sprite_graphic)

    def _set_up_layout(self) -> None:
        """Returns the widgets layout"""
        graphic = self.sprite_graphic

        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)

        self.label = Label(self, self.name)
        self.label.setAlignment(Qt.AlignCenter)

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.graphic_spinner = HexSpinner(self, graphic.graphic)
        self.mirror_checkbox = SpriteFlipCheckbox(self, graphic.horizontal_flip, graphic.vertical_flip)
        layout.setDefaultPositioning(2, Qt.Horizontal)
        layout.addWidget(Label(self, "Graphic"))
        layout.addWidget(self.graphic_spinner)
        layout.addWidget(Label(self, "Mirroring"))
        layout.addWidget(self.mirror_checkbox)

        vbox.addWidget(self.label)
        vbox.addLayout(layout)
        self.setLayout(vbox)

    @property
    def sprite_graphic(self) -> SpriteGraphic:
        """The graphic we are keeping track of"""
        return self._sprite_graphic

    @sprite_graphic.setter
    def sprite_graphic(self, graphic: SpriteGraphic) -> None:
        self._sprite_graphic = graphic
        self._update_graphic()















