"""Show the 16x16 SMB3 block atlas for one selected render context.

``BlockViewer`` stores one object set, graphics set, and palette group.
``BlockBank`` draws the block ids for that exact combination and reports
hovered or clicked block ids from the same atlas. Together they provide one
inspection surface for block decoding outside the level canvas.

See Also
--------
foundry.game.gfx.block_cache
    Supplies cached block decoding for the staged render context.
foundry.gui.windows.LevelViewer
    Uses related decoded block data for level-bank and occupancy inspection.
foundry.gui.dialogs.PaletteViewer
    Provides the companion surface for inspecting palettes that feed block
    rendering.
"""

from math import ceil

from PySide6.QtCore import QPoint, QRect, QSize, QTimer, Signal, SignalInstance
from PySide6.QtGui import QMouseEvent, QPainter, QPaintEvent, QPen, QResizeEvent, Qt
from PySide6.QtWidgets import QComboBox, QLabel, QLayout, QStatusBar, QToolBar, QWidget

from foundry import icon
from foundry.game.gfx import BlockCache
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.GraphicsSet import GRAPHIC_SET_NAMES
from foundry.game.gfx.Palette import PALETTE_GROUPS_PER_OBJECT_SET
from foundry.gui import OBJECT_SET_ITEMS
from foundry.gui.widgets.Spinner import Spinner
from foundry.gui.windows.CustomChildWindow import CustomChildWindow
from smb3parse.constants import TILE_NAMES, UNDERGROUND_OBJECT_SET, WORLD_MAP_OBJECT_SET

ANIMATION_FRAME_DURATION_MS = 125


class BlockViewer(CustomChildWindow):
    """Inspect rendered 16x16 blocks for object and graphics sets.

    The viewer combines object set, graphics set, and palette group controls
    with a block-bank canvas so maintainers can inspect SMB3 TSA/block output
    outside the level editor. It is the quickest way to answer "what does this
    render context draw?" without placing an object into a level first. Toolbar
    controls stage the render context, ``_after_object_set`` pushes that staged
    state into ``BlockBank``, and the canvas handles hover, click, zoom, and
    animation refresh from there.

    Parameters
    ----------
    parent : object
        Parent Qt widget that owns this object.

    Attributes
    ----------
    _graphics_set_number : int
        Graphics set number staged in the dropdown.
    _object_set : int
        Object set number staged in the dropdown.
    block_bank : BlockBank
        Canvas that draws the block grid.
    graphics_set_dropdown : QComboBox
        Graphics set selector.
    next_os_action : QAction
        Action that advances to the next object set.
    object_set_dropdown : QComboBox
        Object set selector.
    object_set_toolbar : QToolBar
        Toolbar containing navigation and render controls.
    palette_group_spinner : Spinner
        Palette group selector.
    prev_os_action : QAction
        Action that moves to the previous object set.
    zoom_in_action : QAction
        Action that increases block-bank zoom.
    zoom_out_action : QAction
        Action that decreases block-bank zoom.

    See Also
    --------
    BlockBank
        Renders the grid and reports hover and click information for each block.

    Notes
    -----
    History around this viewer shows it growing alongside ``BlockCache`` and
    graphics-set controls. The class exists to make render-context changes
    inspectable in one place instead of scattering that debugging work across
    level canvases and object previews.
    """

    def __init__(self, parent):
        """Create the block viewer window.

        The window couples the render-context controls to one ``BlockBank`` so
        maintainers can inspect how object set, graphics set, and palette group
        change the decoded block atlas.
        It is the top-level workflow shell for "pick a render context, then
        inspect individual block ids." Construction proceeds in phases:
        instantiate the shared ``BlockBank`` canvas, build the toolbar actions
        and staged render-context widgets, connect those widgets to the state
        setters below, then route canvas status messages into the window status
        bar so hover and click inspection stay tied to the same staged render
        context.

        Parameters
        ----------
        parent : object
            Parent Qt widget that owns this object.
        """
        super(BlockViewer, self).__init__(parent, "Block Viewer")

        self._object_set = 0
        self._graphics_set_number = 0
        self.block_bank = BlockBank(parent=self)

        self.setCentralWidget(self.block_bank)

        self.object_set_toolbar = QToolBar(self)

        self.prev_os_action = self.object_set_toolbar.addAction(icon("arrow-left.svg"), "Previous object set")
        self.prev_os_action.triggered.connect(self.prev_object_set)

        self.next_os_action = self.object_set_toolbar.addAction(icon("arrow-right.svg"), "Next object set")
        self.next_os_action.triggered.connect(self.next_object_set)

        self.zoom_out_action = self.object_set_toolbar.addAction(icon("zoom-out.svg"), "Zoom Out")
        self.zoom_out_action.triggered.connect(self.block_bank.zoom_out)

        self.zoom_in_action = self.object_set_toolbar.addAction(icon("zoom-in.svg"), "Zoom In")
        self.zoom_in_action.triggered.connect(self.block_bank.zoom_in)

        self.object_set_dropdown = QComboBox(parent=self.object_set_toolbar)
        self.object_set_dropdown.addItems(OBJECT_SET_ITEMS[WORLD_MAP_OBJECT_SET : UNDERGROUND_OBJECT_SET + 1])
        self.object_set_dropdown.setCurrentIndex(0)

        self.object_set_dropdown.currentIndexChanged.connect(self.set_object_set)

        self.graphics_set_dropdown = QComboBox(parent=self.object_set_toolbar)
        self.graphics_set_dropdown.addItems(GRAPHIC_SET_NAMES)
        self.graphics_set_dropdown.setCurrentIndex(0)

        self.graphics_set_dropdown.currentIndexChanged.connect(self.set_graphics_set)

        self.palette_group_spinner = Spinner(self, maximum=PALETTE_GROUPS_PER_OBJECT_SET - 1, base=10)
        self.palette_group_spinner.valueChanged.connect(self.on_palette)

        self.object_set_toolbar.addWidget(self.object_set_dropdown)
        self.object_set_toolbar.addWidget(self.graphics_set_dropdown)

        self.object_set_toolbar.addWidget(QLabel(" Palette: "))
        self.object_set_toolbar.addWidget(self.palette_group_spinner)

        self.addToolBar(self.object_set_toolbar)

        self.layout().setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        self.setStatusBar(QStatusBar(self))
        self.block_bank.status_message_changed.connect(self.statusBar().showMessage)

    @property
    def object_set(self):
        """SMB3 object-set decode context for the visible block atlas.

        The toolbar, status updates, and block-bank canvas all read this one
        value when they need to agree on which SMB3 definition set is being
        inspected and decoded into the visible block atlas. The property is the
        read boundary for the viewer state that later flows through
        ``_after_object_set`` into ``BlockBank`` and the status text it emits.

        Returns
        -------
        int
            Current object set number.
        """
        return self._object_set

    @object_set.setter
    def object_set(self, value):
        """Propagate a new object-set decode context through the viewer.

        Updating the object set also reassigns the default graphics-set selection
        to the matching index, mirroring the common Foundry assumption that a
        level's default graphics set tracks its object set.
        The property update then pushes the new render context through the viewer so
        the atlas, hover names, and click targets all start using the same
        object-set interpretation immediately.

        Parameters
        ----------
        value : int
            Object set number.
        """
        self._object_set = value
        self.object_set_dropdown.setCurrentIndex(self.object_set)
        self.graphics_set_number = value

        self._after_object_set()

    def set_object_set(self, object_set: int):
        """Apply an object-set choice coming from the dropdown signal.

        Parameters
        ----------
        object_set : int
            Object set that controls tiles, graphics, or level object behavior.
        """
        self.object_set = object_set

    @property
    def graphics_set_number(self):
        """Expose the graphics set currently used by the canvas.

        The viewer treats this as part of the active render context rather than
        derived state hidden inside the canvas.

        Returns
        -------
        int
            Current graphics set number.
        """
        return self._graphics_set_number

    @graphics_set_number.setter
    def graphics_set_number(self, value):
        """Apply a graphics set and redraw the block bank.

        This keeps the toolbar control and the preview canvas aligned whenever
        a caller changes the render context programmatically.

        Parameters
        ----------
        value : int
            Graphics set number.
        """
        self._graphics_set_number = value
        self.graphics_set_dropdown.setCurrentIndex(self.graphics_set_number)

        self._after_object_set()

    def set_graphics_set(self, graphics_set: int):
        """Apply a graphics-set choice coming from the dropdown signal.

        Parameters
        ----------
        graphics_set : int
            Graphics set used to draw object previews.
        """
        self.graphics_set_number = graphics_set

    @property
    def palette_group(self):
        """Palette-group selection used when drawing the visible block atlas.

        Keeping palette selection at the window level lets the toolbar and
        canvas stay synchronized while the same decoded block atlas is
        re-rendered with different palette groupings. This property is the
        staged palette boundary consumed by ``_after_object_set`` and direct
        palette-change refreshes.

        Returns
        -------
        int
            Current palette group index.
        """
        return self.palette_group_spinner.value()

    @palette_group.setter
    def palette_group(self, value):
        """Apply the palette group used by the block canvas.

        Parameters
        ----------
        value : int
            Palette group index.
        """
        self.palette_group_spinner.setValue(value)

    def prev_object_set(self):
        """Select the previous block-viewable object set."""
        self.object_set = max(self.object_set - 1, WORLD_MAP_OBJECT_SET)

    def next_object_set(self):
        """Select the next block-viewable object set."""
        self.object_set = min(self.object_set + 1, UNDERGROUND_OBJECT_SET)

    def _after_object_set(self):
        """Push selected render settings into the block-bank canvas."""
        self.block_bank.object_set = self.object_set
        self.block_bank.palette_group_index = self.palette_group
        self.block_bank.graphics_set = self.graphics_set_number

        self.block_bank.update()

    def on_palette(self, value):
        """Update the block bank for a palette-group change.

        Parameters
        ----------
        value : int
            Palette group index.
        """
        self.block_bank.palette_group_index = value
        self.block_bank.update()


class BlockBank(QWidget):
    """Canvas that draws all block ids for a render context.

    The bank renders the 0x00-0xFE block ids in a 16-column grid using
    ``BlockCache``. The 0xFF value is the SMB3 block delimiter and is not drawn
    as an inspectable block. Hover state feeds the status bar, click state feeds
    selection tests, and a timer keeps animated blocks repainting in sync with
    the rest of the editor tooling.

    Parameters
    ----------
    parent : object
        Parent Qt widget that owns this object.
    object_set : int, optional
        Object set that controls tiles, graphics, or level object behavior.
    palette_group_index : int, optional
        Index of the palette group.
    zoom : int, optional
        Zoom factor used for display scaling.

    Attributes
    ----------
    _size : QSize
        Initial fixed canvas size.
    clicked : SignalInstance
        Signal emitted with the clicked block id.
    draw_timer : QTimer
        Timer that repaints animated blocks.
    graphics_set : int
        Graphics set used for block rendering.
    last_clicked_index : int
        Most recent clicked block id.
    object_set : int
        Object set used for block rendering.
    palette_group_index : int
        Palette group used for block rendering.
    sprites : int
        Number of block ids rendered.
    sprites_horiz : int
        Number of block ids per row.
    sprites_vert : int
        Number of rows needed for the block grid.
    status_message_changed : SignalInstance
        Signal emitted with hover status text.
    zoom : int
        Integer display scaling factor.
    zoom_step : int
        Height change per zoom step used by tests and layout.

    Notes
    -----
    The canvas stores render context directly instead of proxying back through
    the toolbar, so tests and helper methods can update object set, palette, and
    graphics selections independently before triggering a repaint.
    """

    status_message_changed: SignalInstance = Signal(str)
    clicked: SignalInstance = Signal(int)

    def __init__(self, parent, object_set=0, palette_group_index=0, zoom=2):
        """Create a block-bank canvas.

        The canvas keeps enough render-context state to rebuild any block on
        hover or repaint without asking the parent window for additional data.

        Parameters
        ----------
        parent : object
            Parent Qt widget that owns this object.
        object_set : int, optional
            Object set that controls tiles, graphics, or level object behavior.
        palette_group_index : int, optional
            Index of the palette group.
        zoom : int, optional
            Zoom factor used for display scaling.
        """
        super(BlockBank, self).__init__(parent)
        self.setMouseTracking(True)

        self.sprites = 255  # 0xFF is the delimiter
        self.zoom_step = 256
        self.sprites_horiz = 16
        self.sprites_vert = ceil(self.sprites / self.sprites_horiz)

        self.object_set = object_set
        self.palette_group_index = palette_group_index
        self.graphics_set = 0
        self.zoom = zoom

        self._size = QSize(
            self.sprites_horiz * Block.WIDTH * self.zoom,
            self.sprites_vert * Block.HEIGHT * self.zoom,
        )

        self.last_clicked_index = 0x00

        self.setFixedSize(self._size)

        self.draw_timer = QTimer(self)
        self.draw_timer.timeout.connect(self.repaint)
        self.draw_timer.setInterval(ANIMATION_FRAME_DURATION_MS)

        self.draw_timer.start()

    def resizeEvent(self, event: QResizeEvent):
        """Schedule a repaint when the canvas is resized.

        Parameters
        ----------
        event : QResizeEvent
            Qt event delivered to the widget.
        """
        self.update()

    def zoom_in(self):
        """Increase the block-grid zoom."""
        self.zoom += 1
        self._after_zoom()

    def zoom_out(self):
        """Decrease the block-grid zoom without going below one."""
        self.zoom = max(self.zoom - 1, 1)
        self._after_zoom()

    def _after_zoom(self):
        """Resize the canvas after a zoom change."""
        new_size = QSize(
            self.sprites_horiz * Block.WIDTH * self.zoom,
            self.sprites_vert * Block.HEIGHT * self.zoom,
        )

        self.setFixedSize(new_size)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Emit block id and grid coordinates for the hovered cell.

        Hover inspection is the main workflow of this widget, so moving the
        cursor continuously recomputes the block id and pushes the decoded name
        into the status bar.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.
        """
        x, y = event.position().toPoint().toTuple()

        block_length = Block.WIDTH * self.zoom

        column = x // block_length
        row = y // block_length

        dec_index = row * self.sprites_horiz + column
        hex_index = hex(dec_index).upper().replace("X", "x")

        if self.object_set == WORLD_MAP_OBJECT_SET:
            tile_name = " – " + TILE_NAMES[dec_index]
        else:
            tile_name = ""

        status_message = f"{dec_index} / {hex_index} @ ({column}, {row}){tile_name}"

        self.status_message_changed.emit(status_message)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Store and emit the clicked block id.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.
        """

        x, y = event.position().toPoint().toTuple()

        block_length = Block.WIDTH * self.zoom

        column = x // block_length
        row = y // block_length

        dec_index = row * self.sprites_horiz + column

        if dec_index < 0xFF:
            self.last_clicked_index = dec_index
            self.clicked.emit(dec_index)

    def paintEvent(self, event: QPaintEvent):
        """Render the block atlas used for inspection and selection.

        Every repaint walks the block id range for the active object set and
        render context so the canvas stays in sync with zoom, palette, and
        animation-frame changes.
        This paint pass is the final stage of the block-viewer pipeline:
        selected render context becomes an inspectable atlas that also drives
        hover names and click selection.

        Parameters
        ----------
        event : QPaintEvent
            Qt event delivered to the widget.
        """
        painter = QPainter(self)

        painter.drawRect(QRect(QPoint(0, 0), self.size()))

        horizontal = self.sprites_horiz

        block_length = Block.WIDTH * self.zoom

        for block_index in range(self.sprites):
            block = BlockCache.block(
                block_index,
                self.object_set,
                self.palette_group_index,
                self.graphics_set,
                animated=True,
            )

            x = (block_index % horizontal) * block_length
            y = (block_index // horizontal) * block_length

            block.draw(painter, x, y, block_length)

        painter.setPen(QPen(Qt.GlobalColor.gray, 1))

        # rows
        for y in range(16):
            y *= block_length

            painter.drawLine(QPoint(0, y), QPoint(16 * block_length, y))

        # columns
        for x in range(16):
            x *= block_length

            painter.drawLine(QPoint(x, 0), QPoint(x, 16 * block_length))
