"""Render clickable world maps for level selection workflows.

This module owns the world-map selection surface used inside the level
selector. It wraps a read-only ``WorldView`` and turns clicks on map tiles or
level pointers into staged selection signals that the parent dialog can merge
with its other level sources.

See Also
--------
foundry.gui.dialogs.level_selector.LevelSelector
    Parent dialog that consumes the staged world-map selections.
foundry.gui.visualization.world.WorldView
    Read-only rendered map surface embedded by this selector.
"""

from contextlib import suppress

from PySide6.QtCore import QMargins, QSize, Signal, SignalInstance
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QScrollArea, QScrollBar, QSizePolicy

from foundry.game.File import ROM
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.settings import LevelPreviewType, Settings
from foundry.gui.visualization.world.WorldView import WorldView
from smb3parse.constants import WORLD_MAP_OBJECT_SET
from smb3parse.data_points import LevelPointerData, Position
from smb3parse.levels.world_map import WorldMap as SMB3WorldMap


class WorldMapLevelSelect(QScrollArea):
    """Show a clickable SMB3 world map for level selection.

    The selector loads a world map as a read-only ``WorldView``. Clicks always
    emit the map position, and when ``ignore_levels`` is false clicks on level
    pointers also emit the level name and pointer data.

    Parameters
    ----------
    world_number : int
        One-based SMB3 world number being processed.

    Attributes
    ----------
    ignore_levels : bool
        Whether clicks should emit only positions and ignore level pointers.
    level_clicked : SignalInstance
        Level clicked used for level selection UI state.
    level_selected : SignalInstance
        Level selected used for level selection UI state.
    map_position_clicked : SignalInstance
        Map position clicked used for level selection UI state.
    world : Level
        Loaded world-map level model.
    world_view : WorldView
        Read-only visual map used for coordinate conversion and drawing.
    """

    level_clicked: SignalInstance = Signal(str, LevelPointerData)
    level_selected: SignalInstance = Signal(str, LevelPointerData)
    map_position_clicked: SignalInstance = Signal(Position)

    def __init__(self, world_number: int):
        # TODO Respect block animation setting in Foundry
        """Load and display a world map for selection.

        Construction proceeds in four phases. It first loads the ROM-backed
        world-map model for ``world_number``. It then wraps that model in a
        ``LevelRef`` so the existing ``WorldView`` rendering pipeline can draw
        it. Next it derives a selector-specific settings object from the global
        application settings so pointer visibility, preview behavior, animated
        tiles, and borders match the level-picking workflow rather than the
        world editor. Finally it embeds the configured read-only view into the
        scroll area and leaves the widget ready for click handling.

        That order is the constructor's real contract. Later mouse handlers
        assume ``self.world`` already exposes pointer lookups, ``self.world_view``
        already knows how to translate GUI coordinates back into map positions,
        and the view is already configured in read-only selection mode. The
        constructor therefore bridges ROM-backed world data, selector settings,
        and the later click-to-selection signal flow instead of merely embedding
        a view.

        Parameters
        ----------
        world_number : int
            One-based SMB3 world number being processed.
        """
        super(WorldMapLevelSelect, self).__init__()

        self.ignore_levels = False
        """Set to True, if you only care about Position in the Map, not a level at the position."""

        world = SMB3WorldMap.from_world_number(ROM(), world_number)

        level_ref = LevelRef()
        level_ref.load_level("World", world.layout_address, 0x0, WORLD_MAP_OBJECT_SET)

        self.world = level_ref.level

        app_settings = Settings("mchlnix", "foundry")
        world_settings = Settings()

        world_settings.setValue("world_view/show_level_pointers", app_settings.value("world_view/show_level_pointers"))
        world_settings.setValue(
            "world_view/show_level_previews",
            app_settings.value("editor/level_preview_type") == LevelPreviewType.TOOLTIP,
        )
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
        """Emit a level-selected signal for a double-click.


        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.
        """
        self._try_emit(event, self.level_selected)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Emit a level-clicked signal for a mouse release.


        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.
        """
        self._try_emit(event, self.level_clicked)

    def _try_emit(self, event: QMouseEvent, level_signal: SignalInstance):
        """Emit world-map selection signals for a click event.

        This keeps raw map-position clicks and valid level-pointer clicks flowing through the same
        coordinate conversion path.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.
        level_signal : SignalInstance
            Signal emitted when the click resolves to a valid level pointer.
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
        """Compute a selector size hint that preserves world-view framing.

        The scroll area grows enough to include the child view height and the
        scrollbar width so the parent level selector can lay out the map tab
        without clipping the embedded world view or forcing scrollbars to
        overlap it immediately.

        Returns
        -------
        QSize
            Recommended Qt size for the selector.
        """
        orig_size: QSize = super(WorldMapLevelSelect, self).sizeHint()
        widget_size: QSize = self.widget().sizeHint()

        size = QSize(orig_size.width(), widget_size.height())

        scrollbar_width = QScrollBar().sizeHint().width()

        return size.grownBy(QMargins(scrollbar_width, scrollbar_width, 0, 0))
