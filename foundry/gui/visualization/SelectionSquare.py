"""Track marquee-selection rectangles for editable Foundry views.

This module holds :class:`SelectionSquare`, the small Qt-facing helper that
stores drag start and end points, exposes the widget-space rectangle used for
painting, and converts that rectangle back into editor-grid coordinates for
selection tests. ``MainView`` keeps one instance alive across mouse press,
drag, paint, and release events so marquee-selection state is preserved in one
place instead of being rebuilt in each handler.

See Also
--------
foundry.gui.visualization.MainView
    Owns the selection helper during level and world-map drag workflows.
"""

from PySide6.QtCore import QPoint, QRect
from PySide6.QtGui import QColor, QPainter, QPen, Qt

from smb3parse.util.rect import Rect

STROKE_COLOR = QColor(0x00, 0x00, 0x00, 0x80)


class SelectionSquare:
    """Track and draw a rectangular drag-selection area.

    The square stores raw widget coordinates while dragging and can convert the
    rectangle back into editor grid coordinates using caller-provided scale
    factors and offsets. Views keep one of these objects around across mouse
    events so drag state, paint state, and grid-space conversion stay in one
    place instead of being recomputed in each handler.

    Attributes
    ----------
    active : bool
        Whether a drag selection is in progress.
    brush : Qt.BrushStyle
        Brush used to draw the selection rectangle.
    dx : int
        Horizontal grid offset applied when converting to editor coordinates.
    dy : int
        Vertical grid offset applied when converting to editor coordinates.
    end_point : QPoint
        Current drag end point in widget coordinates.
    pen : QPen
        Pen used to draw the selection rectangle.
    rect : QRect
        Current widget-coordinate selection rectangle.
    should_draw : bool
        Whether the rectangle should be painted.
    start_point : QPoint
        Drag start point in widget coordinates.
    """

    def __init__(self):
        """Create an inactive marquee-selection helper.

        The helper keeps drag start/end points, Qt widget-space rectangle data,
        and grid-space offsets together so mouse handlers and paint code can
        share one piece of transient selection state.
        """
        self.start_point = QPoint(0, 0)
        self.end_point = QPoint(0, 0)

        self.active = False
        self.should_draw = False

        self.dx, self.dy = 0, 0
        self.rect = QRect(self.start_point, self.end_point)

        self.pen = QPen(STROKE_COLOR, 1)
        self.brush = Qt.NoBrush

    def is_active(self):
        """Report whether ``MainView`` should keep treating the drag as live.

        Mouse-move handlers use this flag to decide whether incoming Qt
        coordinates should extend the marquee rectangle or be interpreted as a
        normal hover or click in the editor surface.

        Returns
        -------
        bool
            ``True`` while the selection drag is active.
        """
        return self.active

    def set_offset(self, dx: int, dy: int):
        """Apply a grid-coordinate offset to adjusted rectangles.

        Views use this when widget coordinates and logical map coordinates do
        not share the same origin, such as world views with hidden border rows.

        Parameters
        ----------
        dx : int
            Horizontal offset.
        dy : int
            Vertical offset.
        """
        self.dx, self.dy = dx, dy

    def start(self, point: QPoint):
        """Start a selection drag.

        Parameters
        ----------
        point : QPoint
            Drag start point in widget coordinates.
        """
        self.active = True

        self.start_point = point

    def set_current_end(self, point: QPoint):
        """Update the drag end point and visible rectangle.

        Parameters
        ----------
        point : QPoint
            Drag end point in widget coordinates.
        """
        if not self.active:
            return

        self.should_draw = True

        self.end_point = point

        self.rect = QRect(self.start_point, self.end_point)

    def stop(self):
        """Stop drawing and mark the drag inactive."""
        self.active = False
        self.should_draw = False

    def get_rect(self):
        """Expose the Qt rectangle used by the active paint and hit-test pass.

        ``MainView`` reads this widget-space rectangle before converting it
        into grid coordinates or painting the marquee outline over the visible
        level or world-map surface.

        Returns
        -------
        QRect
            Current selection rectangle.
        """
        return self.rect

    def get_adjusted_rect(self, horizontal_factor: int, vertical_factor: int) -> Rect:
        """Convert the marquee rectangle into grid coordinates.

        The widget-space rectangle is converted back into editor-grid units so
        selection code can compare it with object rectangles stored in level or
        world-map coordinates.

        Parameters
        ----------
        horizontal_factor : int
            Widget pixels per grid unit horizontally.
        vertical_factor : int
            Widget pixels per grid unit vertically.

        Returns
        -------
        Rect
            Grid-coordinate rectangle including configured offsets.
        """
        x, y = self.get_rect().topLeft().toTuple()
        width, height = self.get_rect().size().toTuple()

        x //= horizontal_factor
        width //= horizontal_factor

        y //= vertical_factor
        height //= vertical_factor

        return Rect(x + self.dx, y + self.dy, width + 1, height + 1)

    def draw(self, painter: QPainter):
        """Draw the rectangle when a drag has visible extent.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        """
        if self.should_draw:
            painter.setPen(self.pen)
            painter.setBrush(self.brush)

            painter.drawRect(self.rect)
