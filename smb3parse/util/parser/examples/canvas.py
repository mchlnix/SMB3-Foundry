"""Render parsed SMB3 level tiles in a lightweight Qt inspection widget.

This example module bridges :class:`smb3parse.util.parser.level.ParsedLevel`
output into a small ``QWidget`` that animates block graphics, paints decoded
screen memory, and performs simple hit-testing back into parsed objects. New
maintainers usually want to read :mod:`smb3parse.util.parser.level` next for
the decoded level model and :mod:`foundry.game.gfx.block_cache` for the block
rendering path.

See Also
--------
smb3parse.util.parser.level.ParsedLevel
    Supplies decoded screen memory and parsed object placements for the
    example viewer.
foundry.game.gfx.block_cache.get_block
    Resolves block indexes into drawable block instances for the active
    graphics and palette state.
"""

from PySide6.QtCore import QPointF, QTimer
from PySide6.QtGui import QMouseEvent, QPainter
from PySide6.QtWidgets import QWidget

from foundry.game.File import ROM
from foundry.game.gfx.block_cache import get_block
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx.Palette import load_palette_group
from smb3parse.levels import LEVEL_SCREEN_WIDTH
from smb3parse.util.parser.level import ParsedLevel

width = LEVEL_SCREEN_WIDTH * 15
height = 27


class Canvas(QWidget):
    """Display a parsed level as animated SMB3 blocks.

    The widget owns just enough rendering state to turn a
    :class:`~smb3parse.util.parser.level.ParsedLevel` into painted blocks. It
    keeps the decoded level model immutable, advances the graphics-set
    animation timer locally, and uses click hit-testing only to identify which
    parsed object contributed a painted tile.

    Parameters
    ----------
    level : ParsedLevel
        Decoded level data whose ``screen_memory`` and ``parsed_objects`` drive
        painting and object hit-testing.

    Attributes
    ----------
    level : ParsedLevel
        Parsed level model being visualized.
    timer : QTimer
        Local animation timer that advances the graphics set frame and triggers
        repaints.
    palette_group
        Palette selection derived from the parsed level's object and palette
        numbers.
    gfx_set : GraphicsSet
        Graphics bank state used when resolving block indexes into drawable
        tiles.
    tsa_data
        Tile-square assembly data for the active object set.
    """

    def __init__(self, level: ParsedLevel):
        """Initialize the widget from parsed level and rendering state.

        The constructor turns parsed SMB3 state into long-lived Qt
        collaborators in one step: it stores the decoded level model, creates
        the animation timer, derives palette and graphics dependencies from the
        parsed header fields, sizes the widget to the decoded block grid, and
        starts the viewer immediately.

        Parameters
        ----------
        level : ParsedLevel
            Parsed level whose object set, palette, graphics set, decoded
            screen memory, and parsed-object tile ranges drive the example
            viewer.

        Notes
        -----
        Construction snapshots only the rendering collaborators needed to draw
        the decoded level. The widget does not re-parse the level during paint
        events; it reuses ``ParsedLevel.screen_memory`` and the cached block
        rendering inputs while the timer advances animation frames.
        """
        super(Canvas, self).__init__()

        self.level = level

        self.timer = QTimer()
        self.timer.setInterval(120)
        self.timer.timeout.connect(self.anim_timer)  # type: ignore

        self.timer.start()

        self.palette_group = load_palette_group(level.object_set_num, level.object_palette_num)
        self.gfx_set = GraphicsSet.from_number(level.graphics_set_num)
        self.tsa_data = ROM.get_tsa_data(level.object_set_num)

        self.setFixedSize(width * Block.SIDE_LENGTH, height * Block.SIDE_LENGTH)

        self.show()

    def anim_timer(self):
        """Advance animated graphics and schedule a repaint.

        Notes
        -----
        SMB3 animated tiles are selected from a four-frame cycle in the active
        graphics set. The timer mutates only that frame index, then requests a
        repaint so the next draw pass resolves blocks against the updated
        animation state.
        """
        self.gfx_set.anim_frame += 1
        self.gfx_set.anim_frame %= 4

        self.repaint()

    def paintEvent(self, event) -> None:
        """Paint the decoded screen memory as block graphics.

        Parameters
        ----------
        event
            Qt paint event describing the invalidated widget region. The
            example redraws the full decoded level surface on each call.

        Notes
        -----
        The draw loop walks ``ParsedLevel.screen_memory`` in decode order,
        derives screen-relative coordinates, resolves each block index through
        the block cache, and paints the resulting block at the fixed tile grid
        position for the widget.
        """
        painter = QPainter(self)

        for i, block_index in enumerate(self.level.screen_memory):
            screen = i // (LEVEL_SCREEN_WIDTH * 27)

            x = (i % LEVEL_SCREEN_WIDTH) + screen * LEVEL_SCREEN_WIDTH
            y = (i // LEVEL_SCREEN_WIDTH) % height

            block = get_block(block_index, self.palette_group, self.gfx_set, self.tsa_data)

            block.draw(painter, x * Block.SIDE_LENGTH, y * Block.SIDE_LENGTH, Block.SIDE_LENGTH)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Map a click back to the parsed object that owns the tile.

        Parameters
        ----------
        event : QMouseEvent
            Mouse press whose position is converted into a decoded tile index
            before the viewer searches the parsed objects in reverse draw order.
        """
        self._find_object_at_pos(event.position().toPoint())

    def _find_object_at_pos(self, pos: QPointF):
        """Find the topmost parsed object occupying a widget position.

        This lookup is the viewer's bridge from painted tiles back to parser
        output. It converts widget coordinates into a single screen-memory
        index, then walks parsed objects from the end so the reported hit
        matches the object that visually sits on top in the rendered scene.

        Parameters
        ----------
        pos : QPointF
            Widget-space position to convert into decoded level tile
            coordinates.

        Notes
        -----
        The lookup mirrors the paint pipeline in reverse: widget coordinates
        become a screen-memory index, then parsed objects are scanned from the
        end so later objects win when multiple objects contribute tiles at the
        same location.
        """
        x = (pos.x() // Block.SIDE_LENGTH) % LEVEL_SCREEN_WIDTH
        y = pos.y() // Block.SIDE_LENGTH
        screen = pos.x() // LEVEL_SCREEN_WIDTH // Block.SIDE_LENGTH

        index = screen * LEVEL_SCREEN_WIDTH * 27
        index += y * LEVEL_SCREEN_WIDTH
        index += x

        for level_object in reversed(self.level.parsed_objects):
            for pos_in_mem, tile_id in level_object.tiles_in_level:
                if pos_in_mem == index:
                    print("Hit", str(level_object))
                    return
