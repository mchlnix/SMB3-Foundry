

from typing import List, Optional
from PySide2.QtWidgets import QWidget
from PySide2.QtGui import QPaintEvent, QPainter
from PySide2.QtCore import QSize, Qt

from foundry.gui.QCore.object_definitions import DEFAULT_SPRITE_GRAPHIC
from foundry.core.Action.Action import Action
from foundry.core.Action.AbstractActionObject import AbstractActionObject
from foundry.gui.QCore.pattern_table import PATTERN_TBL_DEFAULT
from foundry.gui.QCore.Tracker import PartialTrackingObject
from foundry.gui.QCore.palette import DEFAULT_PALETTE_SET

from foundry.game.gfx.Palette import PaletteSet
from foundry.game.gfx.objects.objects.LevelObjectDefinition import SpriteGraphic
from foundry.game.gfx.PatternTableHandler import PatternTableHandler
from foundry.game.gfx.drawable.Sprite import Sprite
from foundry.game.Size import Size
from foundry.game.Position import Position

from foundry.core.Observables.ObservableDecorator import ObservableDecorator

from foundry.gui.QWidget import Widget


class SpriteDisplayer(Widget, AbstractActionObject):
    """Displays a sprite"""
    def __init__(
            self,
            parent: Optional[QWidget],
            graphic: SpriteGraphic = DEFAULT_SPRITE_GRAPHIC,
            palette_index: int = 0,
            palette: PaletteSet = DEFAULT_PALETTE_SET,
            pattern_table: Optional[PatternTableHandler] = None
    ) -> None:
        Widget.__init__(self, parent)
        AbstractActionObject.__init__(self)
        self.parent = parent
        self._palette = palette
        if pattern_table is None:
            pattern_table = PatternTableHandler(PATTERN_TBL_DEFAULT)
        self._pattern_table = pattern_table
        self._palette_index = palette_index
        self._sprite_graphic = graphic

        self.paint_event_action.observer.attach_observer(lambda *_: self._trigger_refresh())

    @property
    def palette(self) -> PaletteSet:
        """The palette set of the object"""
        return self._palette

    @palette.setter
    def palette(self, palette: PaletteSet) -> None:
        self._palette = palette

    @property
    def pattern_table(self) -> PatternTableHandler:
        """The pattern table the object uses"""
        return self._pattern_table

    @pattern_table.setter
    def pattern_table(self, pattern_table: PatternTableHandler) -> None:
        self._pattern_table = pattern_table

    @property
    def palette_index(self) -> int:
        """The palette index for the sprite"""
        return self._palette_index

    @palette_index.setter
    def palette_index(self, index: int) -> None:
        self._palette_index = index

    @property
    def sprite_graphic(self) -> SpriteGraphic:
        """Provides the current sprite graphic we are indexing to"""
        return self._sprite_graphic

    @sprite_graphic.setter
    def sprite_graphic(self, graphic: SpriteGraphic) -> None:
        self._sprite_graphic = graphic

    @property
    def graphic(self) -> int:
        """Returns the current index onto the graphics page used"""
        return self.sprite_graphic.graphic

    @graphic.setter
    def graphic(self, new_graphic) -> None:
        self.sprite_graphic.graphic = new_graphic
        self.paint_event_action.observer(True)

    @property
    def sprite(self) -> Sprite:
        return Sprite.from_sprite_graphic(
            graphic=self.sprite_graphic,
            palette_group=self.palette,
            palette_index=self.palette_index,
            graphics_page=self.pattern_table
        )

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action("paint_event", ObservableDecorator(lambda *_: True)),
        ]

    def resizeEvent(self, event):
        """Resizes the widget to the correct size"""
        new_size = QSize(8, 16)
        new_size.scale(event.size(), Qt.KeepAspectRatio)
        self.resize(new_size)

    def sizeHint(self) -> QSize:
        """The minimum amount of space required for the widget"""
        return QSize(8, 16)

    def _trigger_refresh(self):
        self.update()

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        self.sprite.draw(painter, Position(0, 0), Size(painter.device().width(), painter.device().height()))


class SpriteDisplayerTracker(PartialTrackingObject, SpriteDisplayer):
    """SpriteDisplayer with Tracking abilities"""

    def __init__(
            self,
            parent: Optional[QWidget],
            graphic: SpriteGraphic = DEFAULT_SPRITE_GRAPHIC,
            palette_index: int = 0,
            palette: PaletteSet = DEFAULT_PALETTE_SET,
            pattern_table: Optional[PatternTableHandler] = None
    ) -> None:
        SpriteDisplayer.__init__(self, parent, graphic, palette_index, palette, pattern_table)
        PartialTrackingObject.__init__(self)

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action("paint_event", ObservableDecorator(lambda *_: True)),
            Action("pressed", ObservableDecorator(lambda button: button)),
            Action("released", ObservableDecorator(lambda button: button)),
            Action("single_clicked", ObservableDecorator(lambda button: button)),
            Action("double_clicked", ObservableDecorator(lambda button: button)),
            Action("mouse_moved", ObservableDecorator(lambda pos: pos))
        ]
