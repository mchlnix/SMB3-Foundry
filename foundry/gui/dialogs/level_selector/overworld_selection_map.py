from contextlib import suppress

from PySide6.QtCore import QMargins, QSize, Signal, SignalInstance
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QScrollArea, QScrollBar, QSizePolicy

from foundry.game.File import ROM
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.settings import Settings
from foundry.gui.visualization.world.WorldView import WorldView
from smb3parse.constants import WORLD_MAP_OBJECT_SET
from smb3parse.data_points import LevelPointerData, Position
from smb3parse.levels.world_map import WorldMap as SMB3WorldMap


class WorldMapLevelSelect(QScrollArea):
    level_clicked: SignalInstance = Signal(str, LevelPointerData)
    level_selected: SignalInstance = Signal(str, LevelPointerData)
    map_position_clicked: SignalInstance = Signal(Position)

    def __init__(self, world_number: int):
        # TODO Respect block animation setting in Foundry
        super(WorldMapLevelSelect, self).__init__()

        self.ignore_levels = False
        """Set to True, if you only care about Position in the Map, not a level at the position."""

        world = SMB3WorldMap.from_world_number(ROM(), world_number)

        level_ref = LevelRef()
        level_ref.load_level("World", world.layout_address, 0x0, WORLD_MAP_OBJECT_SET)

        self.world = level_ref.level

        world_settings = Settings()
        world_settings.setValue(
            "world_view/show_level_pointers", Settings("mchlnix", "foundry").value("world_view/show_level_pointers")
        )
        world_settings.setValue("world_view/show_level_previews", True)
        world_settings.setValue("world_view/animated_tiles", True)
        world_settings.setValue("world_view/show_border", True)

        self.world_view = WorldView(self, level_ref, world_settings, None)

        self.world_view.setMouseTracking(True)
        self.world_view.read_only = True

        self.world_view.set_zoom(2.0)

        self.setWidget(self.world_view)

        self.setMouseTracking(True)

        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        self._try_emit(event, self.level_selected)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._try_emit(event, self.level_clicked)

    def _try_emit(self, event: QMouseEvent, level_signal: SignalInstance):
        """
        Analyzes the clicked position described in event and, if a valid level was clicked, emits the signal specified
        by level_signal.

        A map_position_clicked event will be emitted, regardless of whether a level was clicked or not.

        :param event: The mouse event describing the interaction.
        :param level_signal: The signal to emit, if a valid level was clicked.
        """
        pos = self.world_view.mapFromParent(event.position().toPoint())

        level_pos = self.world_view.to_level_point(pos)
        self.map_position_clicked.emit(level_pos)

        if self.ignore_levels:
            return

        x, y = level_pos.xy

        with suppress(ValueError):
            if (level_pointer := self.world.level_pointer_at(x, y)) is None:
                return

            level_signal.emit(self.world.level_name_at_position(x, y), level_pointer.data)

    def sizeHint(self) -> QSize:
        orig_size: QSize = super(WorldMapLevelSelect, self).sizeHint()
        widget_size: QSize = self.widget().sizeHint()

        size = QSize(orig_size.width(), widget_size.height())

        scrollbar_width = QScrollBar().sizeHint().width()

        return size.grownBy(QMargins(scrollbar_width, scrollbar_width, 0, 0))
