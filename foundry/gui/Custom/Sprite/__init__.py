

from typing import List, Optional
from PySide2.QtWidgets import QWidget
from PySide2.QtGui import QPaintEvent, QPainter
from PySide2.QtCore import QSize

from foundry.game.gfx.Palette import PaletteController, PaletteSet, Palette, Color
from foundry.decorators.Observer import Observed
from foundry.game.gfx.PatternTableHandler import PatternTableHandler
from foundry.gui.QWidget import Widget
from foundry.gui.QCore.Action import Action, AbstractActionObject
from foundry.game.gfx.objects.objects.LevelObjectDefinition import SpriteGraphic, Animation
from foundry.game.gfx.drawable.Sprite import Sprite
from foundry.game.Size import Size
from foundry.game.Position import Position


class SpriteDisplayer(Widget, AbstractActionObject):
    """Displays a sprite"""
    def __init__(
            self,
            parent: Optional[QWidget],
            animation: Animation,
            palette: PaletteSet,
            pattern_table: PatternTableHandler,
            index: int = 0
    ) -> None:
        Widget.__init__(self, parent)
        AbstractActionObject.__init__(self)
        self.parent = parent
        self._palette = palette
        self._pattern_table = pattern_table
        self._animation = animation
        self._index = index

        self.paint_event_action.observer.attach(lambda *_: self._trigger_refresh())

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
        self.pattern_table_from_animation()

    def pattern_table_from_animation(self) -> None:
        """Updates the pattern table for animation"""
        ptn = self.pattern_table.pattern_table
        page = self.animation.page
        ptn.sprite_2 = page
        ptn.sprite_3 = page
        self._pattern_table = ptn

    @property
    def animation(self) -> Animation:
        """The animation for the sprite"""
        return self._animation

    @animation.setter
    def animation(self, animation: Animation) -> None:
        self._animation = animation

    @property
    def index(self) -> int:
        """The index into the animation"""
        return self._index

    @index.setter
    def index(self, index: int) -> None:
        self._index = index

    @property
    def sprite_graphic(self) -> SpriteGraphic:
        """Provides the current sprite graphic we are indexing to"""
        return self.animation.graphics[self.index]

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
            palette_index=self.animation.palette,
            graphics_page=self.pattern_table
        )

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action("paint_event", Observed(lambda *_: True)),
        ]

    def sizeHint(self) -> QSize:
        """The minimum amount of space required for the widget"""
        return QSize(32, 64)

    def _trigger_refresh(self):
        print("updating")
        self.update()

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        self.sprite.draw(painter, Position(0, 0), Size(painter.device().width(), painter.device().height()))





