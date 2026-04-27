"""World-map block picking widgets for Scribe's tool window.

This module owns the small picker stack that lets Scribe users browse world-map
tiles, promote one tile into the active selection, and keep that selection in
sync with the palette carried by the live level reference. ``BlockBank`` provides the
full tile bank, ``BlockList`` preserves the active tile and the recent-history
row, and ``BlockIcon`` renders individual clickable previews.

New maintainers usually want to read this file together with the world-editing
tool window that hosts it and the Foundry block viewer that supplies the tile
grid.

See Also
--------
foundry.gui.windows.BlockViewer.BlockBank : Shared tile-bank widget reused by
    the picker.
foundry.game.level.LevelRef.LevelRef : Emits palette and level changes that
    keep the picker synchronized with the active world state.
"""

from PySide6.QtCore import QSize, Signal, SignalInstance
from PySide6.QtGui import QMouseEvent, QPainter, QPaintEvent, Qt
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QVBoxLayout, QWidget

from foundry.game.gfx.block_cache import get_worldmap_tile
from foundry.game.gfx.drawable.Block import Block
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.windows.BlockViewer import BlockBank
from smb3parse.levels import WORLD_MAP_BLANK_TILE_ID


class BlockIcon(QWidget):
    """Render one selectable world-map tile preview.

    ``BlockList`` and ``BlockPicker`` use this widget as the smallest visual
    handoff point between decoded tile data and interactive world-editing
    controls. The icon owns the cached tile image for one tile id and emits
    that id again when the user picks the preview.

    Parameters
    ----------
    block_id : int
        Tile identifier to decode through the world-map tile cache.
    palette_group_no : int, optional
        Palette group used when decoding the tile preview.
    zoom_level : int, optional
        Display scale multiplier applied to the cached block dimensions.

    Attributes
    ----------
    clicked : SignalInstance
        Emits the tile identifier stored in ``block_id`` after a left-click
        release.
    palette_group_no : int
        Palette group used to decode the cached world-map tile preview.
    block_id : int
        Tile identifier emitted when the preview is clicked.
    block : Block
        Cached drawable tile for the selected block id and palette selection.
    zoom_level : int
        Multiplier applied when reporting size and painting the tile.
    """

    clicked: SignalInstance = Signal(int)

    def __init__(self, block_id, palette_group_no=0, zoom_level=2):
        """Create a fixed-size preview for one world-map tile.

        The constructor immediately decodes the first tile image so layouts and
        paint events can treat the widget as ready-to-render state instead of
        waiting for a later refresh cycle.

        Parameters
        ----------
        block_id : int
            Tile identifier to decode into the initial preview.
        palette_group_no : int, optional
            Palette group used for the initial decode. Later palette updates
            replace the cached block by calling :meth:`set_block_id`.
        zoom_level : int, optional
            Display scale multiplier used by :meth:`sizeHint` and
            :meth:`paintEvent`.
        """
        super(BlockIcon, self).__init__()

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.palette_group_no = palette_group_no

        self.block_id = block_id

        self.block = get_worldmap_tile(block_id, palette_group_no)

        self.zoom_level = zoom_level

    def set_block_id(self, block_id) -> int:
        """Swap the preview to a new tile and return the previous tile id.

        This method is the decode boundary for palette-preserving preview
        changes. ``BlockList`` uses it both when the active tile changes and
        when the recent-history strip shifts older picks forward.

        Parameters
        ----------
        block_id : int
            Tile identifier to decode with the icon's current palette group.

        Returns
        -------
        int
            Tile identifier that was displayed before the update.

        Notes
        -----
        ``BlockList`` uses the returned id to rotate the "recent blocks" row
        without losing the previous selection history.
        """
        old_block_id = self.block_id
        self.block_id = block_id

        self.block = get_worldmap_tile(block_id, self.palette_group_no)

        self.update()

        return old_block_id

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Emit the tile id when the user releases the left mouse button.

        Parameters
        ----------
        event : QMouseEvent
            Mouse release event routed by Qt.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.block_id)

    def sizeHint(self) -> QSize:
        """Report the scaled preview size expected by layouts.

        The picker uses fixed-size icons, so layouts rely on this method to
        keep the recent-history strip aligned with the same pixel footprint as
        the block cache draw call.

        Returns
        -------
        QSize
            Block dimensions multiplied by the configured zoom level.
        """
        return QSize(Block.WIDTH, Block.HEIGHT) * self.zoom_level

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint the cached tile preview at the widget origin.

        The draw call reuses the cached ``Block`` so repaint requests stay tied
        to the most recent decode performed by :meth:`__init__` or
        :meth:`set_block_id`.

        Parameters
        ----------
        event : QPaintEvent
            Qt paint event for the widget update cycle.

        Returns
        -------
        None
            Result of the base widget paint handler.
        """
        painter = QPainter(self)

        self.block.draw(painter, 0, 0, Block.WIDTH * self.zoom_level)

        return super(BlockIcon, self).paintEvent(event)


class BlockList(QWidget):
    """Track the active tile selection and a short recent-history row.

    This widget is the stateful bridge between the full tile bank and the
    single tile id emitted back to the tool window. It keeps one large preview
    for the active tile and a short rotation history so repeat edits do not
    force the user to reopen the full bank for common picks.

    Parameters
    ----------
    palette_group : int
        Palette group used to decode the active preview and the recent tile
        previews.

    Attributes
    ----------
    block_was_picked : SignalInstance
        Emits the tile id that should become the tool window's active block.
    palette_group : int
        Palette group applied to every icon in the list.
    current_block : BlockIcon
        Large preview representing the tile that will be emitted to the tool
        window when the picker confirms a selection.
    recent_blocks : list[BlockIcon]
        Rolling history of previously selected tiles, with the most recent tile
        shifted toward the front of the row.

    See Also
    --------
    BlockIcon : Preview widget reused for both the active tile and the history
        strip.
    BlockPicker : Parent widget that relays the chosen tile into the tool
        window.
    """

    block_was_picked: SignalInstance = Signal(int)

    def __init__(self, palette_group):
        """Build the active-selection preview and recent tile history.

        Construction follows one data-flow path: create the large active icon,
        seed the history row with blank placeholders, then connect every icon
        back into :meth:`set_current_block` so both bank-driven picks and
        history re-picks pass through the same rotation and emission logic.
        The finished widget therefore owns all local selection state before the
        parent picker subscribes to its ``block_was_picked`` signal.

        Parameters
        ----------
        palette_group : int
            Palette group used for the initial tile decoding pass.
        """
        super(BlockList, self).__init__()

        self._layout = QHBoxLayout(self)

        self.palette_group = palette_group

        self.current_block = BlockIcon(0, palette_group, zoom_level=4)
        self.current_block.clicked.connect(self.set_current_block)

        self.recent_blocks = [BlockIcon(WORLD_MAP_BLANK_TILE_ID) for _ in range(9)]

        self._layout.addWidget(self.current_block)
        self._layout.addSpacing(10)

        for block_icon in self.recent_blocks:
            block_icon.clicked.connect(self.set_current_block)
            self.layout().addWidget(block_icon)

    def set_current_block(self, new_block_id):
        """Promote a tile into the active slot and rotate recent history.

        Parameters
        ----------
        new_block_id : int
            Tile identifier chosen from the tile bank or one of the recent
            previews.

        Notes
        -----
        The rotation loop preserves the previously active tile by cascading it
        through the recent-history row until an identical tile stops the shift
        or the row is exhausted. Emitting ``block_was_picked`` after the shift
        makes the tool window observe the same tile id that the previews now
        display.
        """
        if self.current_block.block_id != new_block_id:
            last_block_id = self.current_block.block_id

            self.current_block.set_block_id(new_block_id)

            for block_icon in self.recent_blocks:
                if block_icon.block_id == last_block_id:
                    break

                last_block_id = block_icon.set_block_id(last_block_id)

                if last_block_id == new_block_id:
                    break

        self.block_was_picked.emit(new_block_id)

    def update_palette_group(self, palette_group: int):
        """Re-decode every preview with a newly selected world palette.

        Parameters
        ----------
        palette_group : int
            Palette group selected by the active world or level reference.
        """
        for block_icon in [self.current_block] + self.recent_blocks:
            block_icon.palette_group_no = palette_group

            block_icon.set_block_id(block_icon.block_id)


class BlockPicker(QWidget):
    """Compose the tile bank and recent tile list for world editing.

    ``BlockPicker`` coordinates the read-only bank supplied by Foundry with the
    small stateful selection strip used by Scribe. Its job is to keep both
    widgets synchronized with the palette stored in ``LevelRef`` and to forward
    the chosen tile id back to the parent tool window. It is the handoff point
    between Scribe's world-editing UI and Foundry's block rendering helpers, so
    future changes need to preserve both the palette-sync path and the
    tile-selection signal path.

    Parameters
    ----------
    parent : QWidget
        Parent widget that hosts the picker inside the Scribe tool window.
    level_ref : LevelRef
        Active world reference that supplies the palette index and emits
        synchronization signals when the edited world changes.

    Attributes
    ----------
    tile_selected : SignalInstance
        Emits the tile id that the hosting tool window should apply to later
        world-map paint operations.
    level_ref : LevelRef
        Active world reference whose palette and level changes drive picker
        updates.
    block_bank : BlockBank
        Shared tile-bank view that exposes the full set of world-map tiles.
    block_list : BlockList
        Recent-selection strip that mirrors the selected tile id and palette.

    See Also
    --------
    BlockList : Owns the local tile-selection history and emits the chosen tile
        id.
    foundry.gui.windows.BlockViewer.BlockBank : Shared tile-bank widget used
        for bulk tile browsing.
    """

    tile_selected: SignalInstance = Signal(int)

    def __init__(self, parent, level_ref: LevelRef):
        """Wire the bank, recent-history row, and palette synchronization.

        Construction happens in three stages: create the bank and history row
        from the live palette index stored in ``level_ref.level.data``, route
        bank clicks into the history strip,
        then subscribe to ``LevelRef`` so later palette or level swaps repaint
        both views from the same source of truth.

        Parameters
        ----------
        parent : QWidget
            Parent widget that owns the picker.
        level_ref : LevelRef
            Active world reference that provides the palette index stored in the
            loaded world data and emits palette and level change notifications.

        Notes
        -----
        The picker delegates bulk tile browsing to ``BlockBank`` and keeps the
        recent-history row aligned with the same palette by listening to both
        palette and level changes from ``level_ref``. That signal wiring means
        a tile chosen before a palette swap stays selected while both preview
        surfaces are re-decoded against the updated palette.
        """
        super(BlockPicker, self).__init__(parent)

        self.setLayout(QVBoxLayout())

        self.level_ref = level_ref

        self.block_bank = BlockBank(self, palette_group_index=level_ref.level.data.palette_index)
        self.block_bank.status_message_changed.connect(self.window().statusBar().showMessage)
        self.level_ref.palette_changed.connect(self._update_palette_group)
        self.level_ref.level_changed.connect(self._update_palette_group)

        self.block_list = BlockList(level_ref.level.data.palette_index)

        self.block_bank.clicked.connect(self.block_list.set_current_block)
        self.block_list.block_was_picked.connect(self.tile_selected.emit)

        self.layout().addWidget(self.block_bank)
        self.layout().addWidget(self.block_list)

    def set_zoom(self, zoom_level):
        """Forward a new zoom level to the shared tile bank.

        Parameters
        ----------
        zoom_level : int
            Scale multiplier applied by the bank when rendering tile previews.
        """
        self.block_bank.zoom = zoom_level

    def _update_palette_group(self):
        """Refresh bank and recent previews after a palette-bearing change.

        Notes
        -----
        ``LevelRef`` emits both palette and level change signals for world
        edits. This slot rereads the live palette index from the reference,
        repaints the bank, and then re-decodes every preview in the recent tile
        list so the active selection stays visually consistent with the edited
        world.
        """
        self.block_bank.palette_group_index = self.level_ref.level.data.palette_index
        self.block_bank.update()

        self.block_list.update_palette_group(self.level_ref.level.data.palette_index)
