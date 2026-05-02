"""Render SMB3 autoscroll camera paths for level previews.

This module provides :class:`AutoScrollDrawer`, the level-visualization helper
that decodes SMB3 autoscroll movement tables from the active ROM and projects
them onto the editor's level preview. It participates in the level-view
rendering workflow between low-level autoscroll command bytes and the Qt
painter surface: the drawer resolves the configured autoscroll routine, traces
camera-center movement, and accumulates the covered screen area so maintainers
can inspect how the level view will scroll.

See Also
--------
foundry.gui.visualization.MainView
    Main editing surface that hosts level-visualization helpers.
foundry.game.level.Level
    Level model whose header and Mario start position anchor the autoscroll
    preview.
"""

from PySide6.QtCore import QPoint, QPointF, QRectF, QSizeF
from PySide6.QtGui import QBrush, QPainter, QPen, QPolygonF, Qt

from foundry.game import GROUND
from foundry.game.File import ROM
from foundry.game.gfx.drawable.Block import Block
from foundry.game.level.Level import Level
from smb3parse.constants import Constants
from smb3parse.levels import LEVEL_SCREEN_WIDTH

HORIZONTAL_SCROLL_0 = 0
HORIZONTAL_SCROLL_1 = 1
UP_RIGHT_DIAG_SCROLL = 2
SPIKE_CEILING_SCROLL = 3
UP_TIL_DOOR_SCROLL = 4
WATER_LEVEL_SCROLL = 5


_ASCROLL_SCREEN_HEIGHT = 12


class AutoScrollDrawer:
    """Visualize supported SMB3 autoscroll movement paths.

    The drawer reads the autoscroll movement tables from the active ROM and
    traces the camera center through supported horizontal autoscroll routines.
    Blue segments show constant-speed movement; red segments show acceleration.
    The workflow is: decode the row value, resolve the ROM routine slice, step
    through movement commands, and accumulate both path lines and covered screen
    rectangles for visualization.

    Parameters
    ----------
    auto_scroll_row : int
        Encoded autoscroll enemy/item row value.
    level : Level
        Level whose header determines the initial camera position.

    Attributes
    ----------
    acceleration_brush : QBrush
        Brush used for acceleration markers.
    acceleration_pen : QPen
        Pen used for acceleration path segments.
    auto_scroll_row : int
        Encoded autoscroll row value.
    current_pos : QPointF
        Current traced camera-center position.
    horizontal_speed : int
        Current horizontal subpixel speed from the autoscroll routine.
    level : Level
        Level being visualized.
    pixel_length : int
        Pixel scale relative to a native NES pixel.
    rom : ROM
        Active ROM used to read autoscroll tables.
    screen_polygon : QPolygonF
        Union of screen rectangles covered by the traced path.
    scroll_brush : QBrush
        Brush used for constant-speed markers.
    scroll_pen : QPen
        Pen used for constant-speed path segments.
    vertical_speed : int
        Current vertical subpixel speed from the autoscroll routine.

    Notes
    -----
    Only supported horizontal autoscroll patterns are visualized here. Several
    vanilla SMB3 autoscroll types are intentionally ignored because their
    routines are not represented by this drawer yet.
    """

    def __init__(self, auto_scroll_row: int, level: Level):
        """Create an autoscroll path drawer.

        The drawer snapshots the encoded autoscroll selector and the level
        header it should anchor to, then initializes ROM-backed tracing state
        that :meth:`draw` reuses while walking the selected movement routine.

        Parameters
        ----------
        auto_scroll_row : int
            Encoded autoscroll enemy/item row value.
        level : Level
            Level whose header determines the initial camera position.
        """
        self.auto_scroll_row = auto_scroll_row
        self.level = level

        self.current_pos = QPointF()
        self.horizontal_speed = 0
        self.vertical_speed = 0

        self.rom = ROM()

        self.pixel_length = 1

        self.acceleration_pen = QPen(Qt.PenStyle.NoPen)
        self.acceleration_brush = QBrush(Qt.BrushStyle.NoBrush)
        self.scroll_pen = QPen(Qt.PenStyle.NoPen)
        self.scroll_brush = QBrush(Qt.BrushStyle.NoBrush)

        self.screen_polygon = QPolygonF()

    def draw(self, painter: QPainter, block_length: int):
        """Draw the supported autoscroll path for the configured row.

        This method converts the view's block scale into painter-space pixels,
        resolves the selected SMB3 autoscroll routine from ROM tables, and then
        steps through each movement command to update ``current_pos`` and the
        covered screen polygon. The workflow has three stages: configure pens
        and brushes for the view zoom level, trace each ROM movement command
        into line segments and viewport coverage, and finally paint the stop
        marker plus the accumulated covered-screen overlay for the selected
        autoscroll enemy row.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        block_length : int
            Rendered block size in pixels.
        """
        self.pixel_length = block_length // Block.WIDTH

        self.scroll_brush = QBrush(Qt.GlobalColor.blue)
        self.scroll_pen = QPen(self.scroll_brush, 2 * self.pixel_length)

        self.acceleration_brush = QBrush(Qt.GlobalColor.red)
        self.acceleration_pen = QPen(self.acceleration_brush, 2 * self.pixel_length)

        painter.setPen(self.scroll_pen)
        painter.setBrush(self.scroll_brush)

        auto_scroll_type_index = self.auto_scroll_row >> 4
        auto_scroll_routine_index = self.auto_scroll_row & 0b0001_1111

        if auto_scroll_type_index in [
            SPIKE_CEILING_SCROLL,
            UP_TIL_DOOR_SCROLL,
            WATER_LEVEL_SCROLL,
            UP_RIGHT_DIAG_SCROLL,
        ]:
            # not visualized
            return
        elif auto_scroll_type_index not in [HORIZONTAL_SCROLL_0, HORIZONTAL_SCROLL_1]:
            # illegal value, those appear in the vanilla ROM, though; so error out
            return

        first_movement_command_index = (
            self.rom.int(Constants.AScroll_HorizontalInitMove + auto_scroll_routine_index) + 1
        ) % 256
        last_movement_command_index = (
            self.rom.int(Constants.AScroll_HorizontalInitMove + auto_scroll_routine_index + 1)
        ) % 256

        self.horizontal_speed = 0
        self.vertical_speed = 0

        self.current_pos = self._determine_auto_scroll_start(block_length)

        for movement_command_index in range(first_movement_command_index, last_movement_command_index + 1):
            movement_command = self.rom.int(Constants.AScroll_Movement + movement_command_index)
            movement_repeat = self.rom.int(Constants.AScroll_MovementRepeat + movement_command_index)

            self._execute_movement_command(painter, movement_command, movement_repeat)

        stop_marker = QRectF(QPoint(0, 0), QSizeF(10, 10) * self.pixel_length)
        stop_marker.moveCenter(self.current_pos)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(stop_marker)

        painter.setPen(self.scroll_pen)
        painter.setBrush(self.scroll_brush)

        painter.setOpacity(0.2)
        painter.drawPolygon(self.screen_polygon)

    def _execute_movement_command(self, painter: QPainter, command: int, repeat: int):
        """Trace and draw one ROM autoscroll movement command.

        The command byte decides whether this step applies acceleration in
        place, performs a constant-speed movement span, or dispatches into one
        of SMB3's movement loops. Each branch updates the traced camera state
        before painting the corresponding line segment and merging its covered
        screen area into ``screen_polygon``.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        command : int
            Raw movement command byte.
        repeat : int
            Repeat count or tick count for the command.
        """
        h_updates_per_tick = 4  # got those by reading the auto scroll routine
        v_updates_per_tick = 2

        is_acceleration_command = (command >> 4) == 0

        if is_acceleration_command:
            # set speed
            h_acceleration_index = (command & 0b00001100) >> 2
            v_acceleration_index = command & 0b00000011

            assert h_acceleration_index != 3
            assert v_acceleration_index != 3

            h_acceleration = self.rom.int(Constants.AScroll_VelAccel + h_acceleration_index)
            v_acceleration = self.rom.int(Constants.AScroll_VelAccel + v_acceleration_index)

            if h_acceleration == 0xFF:
                h_acceleration = -0x01

            if v_acceleration == 0xFF:
                v_acceleration = -0x01

            h_acceleration <<= 4
            v_acceleration <<= 4

            movement_ticks = repeat
            repeat = 1
        else:
            auto_scroll_loop_selector = command >> 4

            loop_start_offset = Constants.AScroll_MovementLoopStart - 2 + auto_scroll_loop_selector

            if auto_scroll_loop_selector in [0, 1]:
                # normal movement command
                movement_ticks = self.rom.int(loop_start_offset)

                h_acceleration = 0
                v_acceleration = 0
            else:
                # loop command
                movement_loop_start_index = self.rom.int(loop_start_offset)
                movement_loop_end_index = self.rom.int(loop_start_offset + 1)

                number_of_commands = movement_loop_end_index - movement_loop_start_index

                movement_loop_commands = self.rom.read(
                    Constants.AScroll_MovementLoop + movement_loop_start_index, number_of_commands
                )
                movement_loop_repeats = self.rom.read(
                    Constants.AScroll_MovementLoopTicks + movement_loop_start_index,
                    number_of_commands,
                )

                for _ in range(repeat):
                    for sub_command, sub_repeat in zip(movement_loop_commands, movement_loop_repeats):
                        self._execute_movement_command(painter, sub_command, sub_repeat)

                return

        if is_acceleration_command and (h_acceleration or v_acceleration):
            painter.setPen(self.acceleration_pen)
            painter.setBrush(self.acceleration_brush)
        else:
            painter.setPen(self.scroll_pen)
            painter.setBrush(self.scroll_brush)

        # circle at start of new command
        painter.drawEllipse(self.current_pos, 4 * self.pixel_length, 4 * self.pixel_length)

        self._add_points_for_position(self.current_pos)

        if is_acceleration_command and (h_acceleration or v_acceleration):
            for _ in range(movement_ticks):
                self.horizontal_speed += h_acceleration
                self.vertical_speed += v_acceleration

                old_pos = self.current_pos

                self.current_pos += (
                    QPointF(
                        h_updates_per_tick * self.horizontal_speed / 256,
                        v_updates_per_tick * self.vertical_speed / 256,
                    )
                    * self.pixel_length
                )

                painter.drawLine(old_pos, self.current_pos)
                self._add_points_for_position(self.current_pos)
        else:
            old_pos = QPointF(self.current_pos)

            h_movement = h_updates_per_tick * self.horizontal_speed / 256 * movement_ticks * repeat
            v_movement = v_updates_per_tick * self.vertical_speed / 256 * movement_ticks * repeat

            self.current_pos += QPointF(h_movement, v_movement) * self.pixel_length

            painter.drawLine(old_pos, self.current_pos)

            self._add_points_for_line(old_pos, self.current_pos)

    def _add_points_for_position(self, pos: QPointF):
        """Add the visible screen rectangle centered on a position.

        Parameters
        ----------
        pos : QPointF
            Camera-center position in painter coordinates.
        """
        self.screen_polygon = self.screen_polygon.united(QPolygonF.fromList(self._rect_for_point(pos)))

    def _add_points_for_line(self, start: QPointF, stop: QPointF):
        """Add the screen area swept between two camera positions.

        :meth:`draw` reaches this helper after one constant-speed ROM command
        advances ``current_pos`` from ``start`` to ``stop``. The helper turns
        both camera centers into painter-space viewport corners, branches on
        the span's vertical direction, and builds ``point_list`` in the corner
        order needed for one non-self-intersecting sweep polygon. The method
        then unions that polygon into ``screen_polygon`` so the overlay state
        carried through :meth:`draw` records the full viewport corridor covered
        by the command instead of only the rectangles at ``start`` and
        ``stop``.

        Parameters
        ----------
        start : QPointF
            Start camera-center position.
        stop : QPointF
            End camera-center position.
        """
        start_points = self._rect_for_point(start)
        stop_points = self._rect_for_point(stop)

        point_list = []

        if start.y() == stop.y():
            point_list.extend([start_points[0], stop_points[1], stop_points[2], start_points[3]])
        elif start.y() < stop.y():
            point_list.extend(start_points[0:2])
            point_list.extend(stop_points[1:4])
            point_list.append(start_points[3])
        else:
            point_list.append(start_points[0])
            point_list.extend(stop_points[0:3])
            point_list.extend(start_points[2:4])

        self.screen_polygon = self.screen_polygon.united(QPolygonF.fromList(point_list))

    def _rect_for_point(self, pos: QPointF):
        """Describe the painter-space viewport centered on a camera position.

        Autoscroll tracing stores only camera-center positions, so the overlay
        builders need a repeatable way to recover the full SMB3 viewport for
        each traced point. This helper expands one center point into the four
        corners of the screen rectangle at the active block scale.
        :meth:`_add_points_for_position` uses the returned corners when one
        movement step should contribute a single visible screen.
        :meth:`_add_points_for_line` calls it for both ends of a movement span
        so it can build the polygon swept between consecutive centers before
        merging that polygon into ``screen_polygon``.

        Parameters
        ----------
        pos : QPointF
            Camera-center position.

        Returns
        -------
        tuple[QPointF, QPointF, QPointF, QPointF]
            Top-left, top-right, bottom-right, and bottom-left screen corners.
        """
        top_right = (
            pos + QPointF(LEVEL_SCREEN_WIDTH // 2, -_ASCROLL_SCREEN_HEIGHT // 2) * self.pixel_length * Block.WIDTH
        )
        bottom_right = (
            pos + QPoint(LEVEL_SCREEN_WIDTH // 2, _ASCROLL_SCREEN_HEIGHT // 2) * self.pixel_length * Block.WIDTH
        )

        top_left = top_right - QPointF(LEVEL_SCREEN_WIDTH, 0) * self.pixel_length * Block.WIDTH
        bottom_left = bottom_right - QPointF(LEVEL_SCREEN_WIDTH, 0) * self.pixel_length * Block.WIDTH

        return top_left, top_right, bottom_right, bottom_left

    def _determine_auto_scroll_start(self, block_length: int) -> QPointF:
        # only support horizontal levels for now
        """Compute the initial camera-center used for autoscroll tracing.

        The starting point comes from the level header's Mario spawn row and
        the fixed horizontal autoscroll camera rules used by SMB3 horizontal
        stages. That anchor gives :meth:`draw` the initial camera center before
        ROM movement commands advance the preview path.

        Parameters
        ----------
        block_length : int
            Rendered block size in pixels.

        Returns
        -------
        QPointF
            Starting camera-center position in painter coordinates.
        """
        _, mario_y = self.level.header.mario_position()

        scroll_x, scroll_y = LEVEL_SCREEN_WIDTH // 2, min(mario_y + 2, GROUND - _ASCROLL_SCREEN_HEIGHT // 2)

        return QPointF(scroll_x, scroll_y) * block_length
