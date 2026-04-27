"""Interactive level-editing view for Foundry's in-level workflow.

This module contains the canvas that translates Qt input into selection,
dragging, resizing, Mario-position edits, and object placement commands for
decoded SMB3 levels. It is the interaction counterpart to ``LevelDrawer`` and
the main bridge between editor gestures and undoable level mutations.

See Also
--------
foundry.gui.visualization.MainView
    Shared view shell that provides common interaction and coordinate logic.
foundry.gui.visualization.level.LevelDrawer
    Rendering pipeline paired with this interactive canvas.
foundry.game.level.Level
    Level model mutated and queried by this view.
"""

from bisect import bisect_right
from typing import cast

from PySide6.QtCore import QPoint, QSize, QTimer
from PySide6.QtGui import QDropEvent, QMouseEvent, Qt, QUndoStack, QWheelEvent
from PySide6.QtWidgets import QScrollArea, QToolTip, QWidget

from foundry import ctrl_is_pressed, make_macro
from foundry.game import EXPANDS_BOTH, EXPANDS_HORIZ, EXPANDS_VERT
from foundry.game.File import ROM
from foundry.game.gfx import BlockCache
from foundry.game.gfx.objects.in_level.enemy_item import EnemyItem
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from foundry.game.gfx.objects.in_level.level_object import LevelObject
from foundry.game.level.Level import Level
from foundry.game.level.LevelRef import LevelRef
from foundry.game.level.WorldMap import WorldMap
from foundry.gui.commands import (
    AddEnemyAt,
    AddLevelObjectAt,
    MoveObjects,
    RemoveObject,
    ResizeObjects,
    SetLevelAttribute,
)
from foundry.gui.ContextMenu import LevelContextMenu
from foundry.gui.settings import RESIZE_LEFT_CLICK, RESIZE_RIGHT_CLICK, Settings
from foundry.gui.visualization.level.LevelDrawer import LevelDrawer
from foundry.gui.visualization.MainView import (
    MODE_DRAG,
    MODE_FREE,
    MODE_MOVE_MARIO,
    MODE_RESIZE_DIAG,
    MODE_RESIZE_HORIZ,
    MODE_RESIZE_VERT,
    RESIZE_MODES,
    MainView,
)
from foundry.gui.windows.BlockViewer import ANIMATION_FRAME_DURATION_MS
from smb3parse.data_points import Position
from smb3parse.levels import HEADER_LENGTH


class LevelView(MainView):
    """Interactive editor canvas for SMB3 level layouts.

    The view owns level-specific input behavior on top of ``MainView``:
    object/enemy selection, dragging, resizing, wheel-based type cycling,
    toolbar drops, Mario start-position dragging, and save-safety checks.
    It is the point where temporary visual gestures become undoable Foundry
    commands: drags become ``MoveObjects``, resizes become ``ResizeObjects``,
    drops become add commands, and Mario-position edits become merged level
    attribute updates.

    Parameters
    ----------
    parent : QWidget | None
        Parent Qt widget that owns this object.
    level : LevelRef
        Reference to the edited level.
    settings : Settings
        Application settings used to configure the widget behavior.
    context_menu : LevelContextMenu | None
        Context menu populated or displayed by the widget.

    Attributes
    ----------
    _last_mario_indexes : tuple[int, int]
        Header start indexes captured before a Mario-start drag begins.
    _object_was_selected_on_last_click : bool
        Whether the active click already changed selection before release logic runs.
    currently_dragged_object : InLevelObject | None
        Toolbar object previewed over the level during drag/drop placement.
    drag_start_point : Position
        Grid position where the active move gesture began.
    dragging_happened : bool
        Whether the active drag gesture produced a position change.
    drawer : LevelDrawer
        Renderer for level layers, overlays, and animation state.
    last_mouse_position : Position
        Last level-grid position used by drag, resize, or Mario gestures.
    mouse_mode : int
        Active interaction mode such as free, drag, resize, or move-Mario.
    objects_before_moving : list[InLevelObject]
        Copies of selected objects captured before a move command is committed.
    objects_before_resizing : list[InLevelObject]
        Copies of selected objects captured before a resize command is committed.
    redraw_timer : QTimer | None
        Timer that advances animated blocks and enemies when enabled.
    resize_obj_start_point : Position
        Grid position used as the anchor while resizing the selected objects.
    resizing_happened : bool
        Whether the active resize gesture changed encoded object data.
    """

    def __init__(
        self,
        parent: QWidget | None,
        level: LevelRef,
        settings: Settings,
        context_menu: LevelContextMenu | None,
    ):
        """Create the level editor view.

        The view installs a ``LevelDrawer``, hooks animation refresh to palette
        and level changes, and initializes the transient gesture state later
        consumed by move, resize, Mario-position, and drop commands.

        Parameters
        ----------
        parent : QWidget | None
            Parent Qt widget that owns this object.
        level : LevelRef
            Reference to the edited level.
        settings : Settings
            Application settings used to configure the widget behavior.
        context_menu : LevelContextMenu | None
            Context menu populated or displayed by the widget.
        """
        self.drawer = LevelDrawer()
        self.redraw_timer: QTimer | None = None

        super(LevelView, self).__init__(parent, level, settings, context_menu)

        level.palette_changed.connect(self.update_anim_timer)
        level.level_changed.connect(self.update_anim_timer)
        self.update_anim_timer()

        self.mouse_mode = MODE_FREE

        self.last_mouse_position: Position = Position.from_xy(0, 0)

        self.dragging_happened = True
        self.resizing_happened = False

        self.resize_obj_start_point = Position.from_xy(0, 0)
        self.drag_start_point = Position.from_xy(0, 0)

        self._last_mario_indexes = 0, 0

        self.objects_before_resizing: list[InLevelObject] = []
        self.objects_before_moving: list[InLevelObject] = []

        self.setWhatsThis(
            "<b>Level View</b><br/>"
            "This renders the level as it would appear in game plus additional information, that can be "
            "toggled in the View menu.<br/>"
            "It supports selecting multiple objects, moving, copy/pasting and resizing them using the "
            "mouse or the usual keyboard shortcuts.<br/>"
            "There are still occasional rendering errors, or small inconsistencies. If you find them, "
            "please report the kind of object (name or values in the SpinnerPanel) and the level or "
            "object set they appear in, in the discord and @Michael or on the github page under Help."
            "<br/><br/>"
            ""
            "If all else fails, click the play button up top to see your level in game in seconds."
        )

    @property
    def level(self) -> Level:
        """Edited SMB3 level model behind the active canvas workflow.

        Dragging, resizing, tooltips, and save checks all route through this
        typed accessor instead of repeatedly unpacking ``level_ref``.

        Returns
        -------
        Level
            Level model referenced by ``level_ref``.
        """
        return self.level_ref.level

    @property
    def level_header(self):
        """Mutable SMB3 header staged on the edited level.

        Mario-start editing and header-derived rendering behavior both read
        this shared header state during interactive editing.

        Returns
        -------
        object
            Level header belonging to ``self.level``.
        """
        return self.level.header

    @property
    def undo_stack(self) -> QUndoStack:
        """Undo stack used for committed level-edit commands.

        Move, resize, add, and Mario-position edits all end up on this shared
        stack instead of mutating level state invisibly.

        Returns
        -------
        QUndoStack
            Main-window undo stack used for committed level-view edits.
        """
        return cast(QUndoStack, self.window().findChild(QUndoStack, "undo_stack"))

    def next_anim_step(self):
        """Advance animated blocks/enemies and repaint."""
        BlockCache.next_frame()
        self.drawer.anim_frame += 1
        self.drawer.anim_frame %= 4

        self.repaint()

    def update_anim_timer(self):
        """Start or stop the level animation repaint timer."""
        if not self.level_ref:
            return

        if self.redraw_timer is not None:
            self.redraw_timer.stop()
            self.drawer.anim_frame = 0

        if self.settings.value("level_view/block_animation"):
            redraw_timer = QTimer(self)
            redraw_timer.setInterval(ANIMATION_FRAME_DURATION_MS)
            redraw_timer.timeout.connect(self.next_anim_step)
            redraw_timer.start()

            self.redraw_timer = redraw_timer

    def set_zoom(self, zoom):
        """Persist and apply a level-view zoom factor.

        Parameters
        ----------
        zoom : float
            Zoom factor used for display scaling.
        """
        self.settings.setValue("level_view/last_zoom_factor", zoom)
        super().set_zoom(zoom)

    def sizeHint(self) -> QSize:
        """Qt size implied by level bounds and the active zoom factor.

        Qt queries this hint while the surrounding ``QScrollArea`` decides the
        editor viewport, scrollbar ranges, and repaintable canvas size.
        Returning decoded level bounds in block units scaled by
        ``block_length`` keeps layout, scrolling, drag previews, hit testing,
        and ``LevelDrawer`` output on the same coordinate system that the rest
        of the interaction pipeline uses. When no decoded level is attached
        yet, the method falls back to the base ``MainView`` sizing path until
        ``level_ref`` can supply authoritative bounds for the editing session.

        Returns
        -------
        QSize
            Canvas size derived from the level width and height after applying
            the active block scaling.
        """
        if self.level is None:
            return super(LevelView, self).sizeHint()

        w, h = self.level.size

        w *= self.block_length
        h *= self.block_length

        return QSize(w, h)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Update drag, resize, Mario movement, selection, and tooltips.

        The method keeps live gestures temporary until the corresponding mouse
        release commits an undo command.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.

        Returns
        -------
        object
            Result returned by the base view handler, if any.
        """
        mouse_point = event.position().toPoint()

        if self.mouse_mode == MODE_DRAG:
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            self._dragging(mouse_point)

        elif self.mouse_mode in RESIZE_MODES:
            previously_selected_objects = self.level_ref.selected_objects

            self._resizing(mouse_point)

            self.level_ref.selected_objects = previously_selected_objects

        elif self.mouse_mode == MODE_MOVE_MARIO:
            self._update_mario_move(mouse_point)

        elif self.selection_square.active:
            self._set_selection_end(event)

        elif self.settings.value("editor/resize_mode") == RESIZE_LEFT_CLICK:
            self._set_cursor_for_position(mouse_point)

        object_under_cursor = self.object_at(mouse_point)

        if self.settings.value("level_view/object_tooltip_enabled") and object_under_cursor is not None:
            self.setToolTip(str(object_under_cursor))
        else:
            self.setToolTip("")
            QToolTip.hideText()

        return super(LevelView, self).mouseMoveEvent(event)

    def _set_cursor_for_position(self, mouse_point: QPoint):
        """Switch cursors when hover reaches a resizable object edge.

        Parameters
        ----------
        mouse_point : QPoint
            Widget-coordinate cursor position.
        """
        level_object = self.object_at(mouse_point)

        if isinstance(level_object, (EnemyItem, LevelObject)):
            is_resizable = not level_object.is_fixed

            edges = self._cursor_on_edge_of_object(level_object, mouse_point)

            if is_resizable and edges:
                if edges == Qt.Edge.RightEdge and level_object.expands() & EXPANDS_HORIZ:
                    cursor = Qt.CursorShape.SizeHorCursor
                elif edges == Qt.Edge.BottomEdge and level_object.expands() & EXPANDS_VERT:
                    cursor = Qt.CursorShape.SizeVerCursor
                elif (level_object.expands() & EXPANDS_BOTH) == EXPANDS_BOTH:
                    cursor = Qt.CursorShape.SizeFDiagCursor
                else:
                    return

                if self.mouse_mode not in RESIZE_MODES:
                    self.setCursor(cursor)

                return

        if self.mouse_mode not in RESIZE_MODES:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def _cursor_on_edge_of_object(self, level_object: InLevelObject, pos: QPoint, edge_width: int = 4) -> Qt.Edge:
        """Detect which resize edge of an object lies under the cursor.

        Resize-mode staging depends on this edge test so later drag handling
        can choose horizontal, vertical, or diagonal resize state correctly.

        Parameters
        ----------
        level_object : InLevelObject
            Level object being displayed or modified.
        pos : QPoint
            Widget-coordinate cursor position.
        edge_width : int, optional
            Pixel tolerance for edge detection.

        Returns
        -------
        Qt.Edge
            Resize edge under the cursor, if one is active.
        """
        right = (level_object.get_rect().left() + level_object.get_rect().width) * self.block_length
        bottom = (level_object.get_rect().top() + level_object.get_rect().height) * self.block_length

        on_right_edge = pos.x() in range(right - edge_width, right)
        on_bottom_edge = pos.y() in range(bottom - edge_width, bottom)

        edges = Qt.Edge(0)

        if on_right_edge:
            edges |= Qt.Edge.RightEdge

        if on_bottom_edge:
            edges |= Qt.Edge.BottomEdge

        return edges

    def wheelEvent(self, event: QWheelEvent):
        """Optionally cycle the selected object's type with the mouse wheel.

        Type-cycling is deliberately conservative: it only runs when the
        feature is enabled, the cursor is over a selected in-level object, and
        the active model is a normal level rather than a world map. Otherwise
        the event falls back to the normal scroll behavior.

        Parameters
        ----------
        event : QWheelEvent
            Qt event delivered to the widget.

        Returns
        -------
        bool
            ``True`` when the wheel changed an object type.
        """
        if self.settings.value("editor/object_scroll_enabled"):
            pos = event.position().toPoint()
            obj_under_cursor = self.object_at(pos)

            if obj_under_cursor is None:
                return False

            if isinstance(self.level, WorldMap):
                return False

            # scrolling through the level could unintentionally change objects, if the cursor would wander onto them.
            # this is annoying (to me) so only change already selected objects
            if obj_under_cursor not in self.level_ref.selected_objects:
                return False

            self._change_object_on_mouse_wheel(pos, event.angleDelta().y())

            return True
        else:
            super(LevelView, self).wheelEvent(event)
            return False

    def _change_object_on_mouse_wheel(self, cursor_position: QPoint, y_delta: int):
        """Replace the object under the cursor with its next or previous type.

        The change is staged as a macro of remove-plus-add so it stays undoable,
        preserves list position, and works uniformly for both terrain objects
        and enemy/item entries.

        Parameters
        ----------
        cursor_position : QPoint
            Widget-coordinate cursor position.
        y_delta : int
            Wheel delta used to choose increment or decrement.
        """
        obj_under_cursor = self.object_at(cursor_position)

        if not isinstance(obj_under_cursor, InLevelObject):
            return

        if y_delta > 0:
            macro_name = f"Increment Type of '{obj_under_cursor.name}'"
        else:
            macro_name = f"Decrement Type of '{obj_under_cursor.name}'"

        self.undo_stack.beginMacro(macro_name)

        if isinstance(obj_under_cursor, LevelObject):
            index = self.level.objects.index(obj_under_cursor)
        else:
            index = self.level.enemies.index(cast(EnemyItem, obj_under_cursor))

        copied_object = obj_under_cursor.copy()

        self.undo_stack.push(RemoveObject(self.level_ref, obj_under_cursor))

        if y_delta > 0:
            copied_object.increment_type()
        else:
            copied_object.decrement_type()

        if isinstance(copied_object, LevelObject):
            self.undo_stack.push(
                AddLevelObjectAt(
                    self,
                    self.from_level_point(*copied_object.get_position()),
                    copied_object.domain,
                    copied_object.obj_index,
                    copied_object.length,
                    index=index,
                    selected=True,
                )
            )
        else:
            self.undo_stack.push(
                AddEnemyAt(
                    self,
                    self.from_level_point(*copied_object.get_position()),
                    copied_object.obj_index,
                    index,
                    selected=True,
                ),
            )

        self.undo_stack.endMacro()

    def _on_right_mouse_button_down(self, event: QMouseEvent):
        """Start right-click selection or right-click resize mode.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.
        """
        if self.mouse_mode == MODE_DRAG:
            return

        level_pos = self.to_level_point(event.position().toPoint())

        self.last_mouse_position = level_pos

        if self._select_objects_on_click(event) and self.settings.value("editor/resize_mode") == RESIZE_RIGHT_CLICK:
            self._try_start_resize(MODE_RESIZE_DIAG, event)

    def _try_start_resize(self, resize_mode: int, event: QMouseEvent):
        """Start a resize gesture when selected objects support it.

        The method filters out non-resizable cases, captures the anchor object
        position, and snapshots the pre-resize objects so mouse release can turn
        the temporary preview into one undoable ``ResizeObjects`` command.

        Parameters
        ----------
        resize_mode : int
            Resize mode bitmask.
        event : QMouseEvent
            Qt event delivered to the widget.

        Returns
        -------
        bool
            ``True`` when resizing started.
        """
        if resize_mode not in RESIZE_MODES:
            return False

        if all(isinstance(obj, EnemyItem) for obj in self.get_selected_objects()):
            return False

        # check if there is at least one selected object that can be resized with the given mode, otherwise, return
        at_least_one = False

        for obj in self.get_selected_objects():
            if obj.expands() & EXPANDS_VERT and resize_mode & MODE_RESIZE_VERT:
                at_least_one = True
                break
            elif obj.expands() & EXPANDS_HORIZ and resize_mode & MODE_RESIZE_HORIZ:
                at_least_one = True
                break

        if not at_least_one:
            return False

        self.mouse_mode = resize_mode

        if (found_obj := self.object_at(event.position().toPoint())) is None:
            return False

        self.resize_obj_start_point = Position.from_xy(*found_obj.get_position())

        self.objects_before_resizing = [obj.copy() for obj in self.get_selected_objects()]

        return True

    def _resizing(self, mouse_point: QPoint):
        """Resize selected objects during an active resize gesture.

        During the drag this mutates only the live preview objects. The
        committed undo command is created later by ``_stop_resize`` once the
        pointer is released.

        Parameters
        ----------
        mouse_point : QPoint
            Widget-coordinate cursor position.
        """
        self.resizing_happened = True

        if isinstance(self.level, WorldMap):
            return

        level_pos = self.to_level_point(mouse_point)

        dx, dy = (level_pos - self.resize_obj_start_point).xy

        if not self.mouse_mode & MODE_RESIZE_HORIZ:
            dx = 0

        if not self.mouse_mode & MODE_RESIZE_VERT:
            dy = 0

        self.last_mouse_position = level_pos

        selected_objects = self.get_selected_objects()

        for obj in selected_objects:
            obj.resize_by(dx, dy)

        self.update()

    def get_selected_objects(self) -> list[InLevelObject]:
        """Expose selected in-level objects with the level-specific type.

        ``MainView`` exposes a generic selection surface; ``LevelView`` narrows
        it back to in-level objects for drag, resize, clipboard, and save-safety
        workflows.

        Returns
        -------
        list[InLevelObject]
            Currently selected in-level objects.
        """
        return cast(list[InLevelObject], super(LevelView, self).get_selected_objects())

    def _on_right_mouse_button_up(self, event):
        """Commit right-click resize or open the level context menu.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.
        """
        if self.resizing_happened:
            self._stop_resize()

        elif self.context_menu is not None:
            menu_pos = self.mapToGlobal(event.position().toPoint())
            object_under_cursor = self.object_at(event.position())

            if self.get_selected_objects():
                menu = self.context_menu.as_object_menu(object_under_cursor)
            else:
                menu = self.context_menu.as_background_menu(object_under_cursor)

            menu.popup(menu_pos)

        self.resizing_happened = False
        self.mouse_mode = MODE_FREE
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def _stop_resize(self):
        """Commit a completed resize gesture to the undo stack.

        Resize previews mutate the live objects immediately for responsiveness.
        This method snapshots the before/after state into a single
        ``ResizeObjects`` command so undo restores the exact encoded object
        sizes.
        """
        if not self.resizing_happened:
            return

        if self.mouse_mode not in RESIZE_MODES or not self.get_selected_objects():
            return

        self.undo_stack.push(
            ResizeObjects(
                self.level_ref,
                self.objects_before_resizing,
                self.get_selected_objects(),
            )
        )

        self.objects_before_resizing = []

        self.resizing_happened = False
        self.mouse_mode = MODE_FREE
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def _on_left_mouse_button_down(self, event: QMouseEvent):
        # 1 If clicking on Mario: show potential Mario positions, when dragging
        # 2 if clicking on background: deselect everything, start selection square
        # 3 if clicking on background and ctrl: start selection_square
        # 4 if clicking on selected object: deselect everything and select only this object
        # 5 if clicking on selected object and ctrl: do nothing, deselect this object on release
        # 6 if clicking on unselected object: deselect everything and select only this object
        # 7 if clicking on unselected object and ctrl: select this object

        """Start Mario movement, selection, dragging, resizing, or marquee selection.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.
        """
        if self._is_over_mario_sprite(event.position().toPoint()):
            self._start_move_mario()

        elif self._select_objects_on_click(event):
            obj = self.object_at(event.position().toPoint())

            if not isinstance(obj, InLevelObject):
                return

            # enable all drag functionality
            if obj is not None:
                edge = self._cursor_on_edge_of_object(obj, event.position().toPoint())

                if (
                    self.settings.value("editor/resize_mode") == RESIZE_LEFT_CLICK
                    and edge
                    and self._try_start_resize(self._resize_mode_from_edge(edge), event)
                ):
                    return

                self.drag_start_point = Position.from_xy(*obj.get_position())
                self.objects_before_moving = [obj.copy() for obj in self.get_selected_objects()]
        else:
            self._start_selection_square(event.position().toPoint())

    def _is_over_mario_sprite(self, mouse_point: QPoint) -> bool:
        # Mario Sprite is offset by half a block, so offset the cursor as well
        """Detect the cursor over the drawn Mario start sprite.

        Mario is rendered with a half-block horizontal offset and only when the
        corresponding view option is enabled, so hit testing mirrors that same
        display logic before entering Mario-move mode.

        Parameters
        ----------
        mouse_point : QPoint
            Widget-coordinate cursor position.

        Returns
        -------
        bool
            ``True`` when Mario is visible and under the cursor.
        """
        mouse_point.setX(mouse_point.x() - self.block_length // 2)

        if not self.settings.value("level_view/draw_mario"):
            return False

        return self.level_header.mario_position() == self.to_level_point(mouse_point).xy

    def _start_move_mario(self):
        """Begin a Mario start-position drag."""
        self.mouse_mode = MODE_MOVE_MARIO

        self._last_mario_indexes = self.level_header.mario_start_indexes

        self.setCursor(Qt.CursorShape.ClosedHandCursor)

        self.drawer.should_draw_potential_marios = True

        self.update()

    def _update_mario_move(self, mouse_point: QPoint):
        # Mario Sprite is offset by half a block, so offset the cursor as well
        """Preview a valid Mario start-position move.

        The drag only updates the live header preview when the hovered position
        maps to one of SMB3's valid start-action positions. The actual undoable
        header edit is committed later by ``_stop_mario_move``.

        Parameters
        ----------
        mouse_point : QPoint
            Widget-coordinate cursor position.
        """
        mouse_point.setX(mouse_point.x() - self.block_length // 2)

        # get current mouse position
        # convert it to level position
        current_level_position = self.to_level_point(mouse_point)

        # check if among valid mario positions
        if current_level_position.xy not in self.level_header.gen_mario_start_positions():
            return

        # if so, get the corresponding starting indexes
        x_index, y_index = self.level_header.start_indexes_from_position(*current_level_position.xy)

        # write them to the level header temporarily
        self.level_header.start_x_index = x_index
        self.level_header.start_y_index = y_index

        self.update()

    def _stop_mario_move(self):
        """Commit or revert a Mario start-position drag."""
        cur_mario_indexes = self.level_header.mario_start_indexes

        if self._last_mario_indexes != cur_mario_indexes:
            last_x, last_y = self._last_mario_indexes
            cur_x, cur_y = cur_mario_indexes

            self.level_header.start_x_index = last_x
            self.level_header.start_y_index = last_y

            x_command = SetLevelAttribute(self.level_ref, "start_x_index", cur_x)
            y_command = SetLevelAttribute(self.level_ref, "start_y_index", cur_y)

            make_macro(
                self.undo_stack,
                f"Set Mario Start Position to {self.level_header.mario_position()}",
                x_command,
                y_command,
            )
        else:
            start_x_index, start_y_index = self._last_mario_indexes

            self.level_header.start_x_index = start_x_index
            self.level_header.start_y_index = start_y_index

        self.drawer.should_draw_potential_marios = False

    @staticmethod
    def _resize_mode_from_edge(edge: Qt.Edge):
        """Convert Qt edge flags to Foundry resize-mode flags.

        The edge detector works in Qt terms, while the gesture state machine
        uses Foundry's horizontal/vertical resize flags for later drag
        processing.

        Parameters
        ----------
        edge : Qt.Edge
            Edges detected under the cursor.

        Returns
        -------
        int
            Resize mode bitmask.
        """
        mode = 0

        if edge & Qt.Edge.RightEdge:
            mode |= MODE_RESIZE_HORIZ

        if edge & Qt.Edge.BottomEdge:
            mode |= MODE_RESIZE_VERT

        return mode

    def _dragging(self, mouse_point: QPoint):
        """Move selected objects during a drag gesture preview.

        Like resizing, dragging mutates the live objects for immediate visual
        feedback and defers undo-command creation until mouse release.

        Parameters
        ----------
        mouse_point : QPoint
            Widget-coordinate cursor position.
        """
        self.dragging_happened = True

        level_pos = self.to_level_point(mouse_point)

        dx, dy = (level_pos - self.last_mouse_position).xy

        self.last_mouse_position = level_pos

        selected_objects = self.get_selected_objects()

        for obj in selected_objects:
            obj.move_by(dx, dy)

        self.update()

    def object_at(self, q_point: QPoint) -> InLevelObject | None:
        """Look up the in-level object under a widget point.

        This view-level wrapper keeps callers in widget coordinates while the
        shared object-hit-testing still routes through ``MainView`` and the
        model-backed selection surface.

        Parameters
        ----------
        q_point : QPoint
            Point in widget coordinates.

        Returns
        -------
        InLevelObject | None
            Frontmost in-level object under that widget position, if one exists.
        """
        return cast(InLevelObject | None, super(LevelView, self).object_at(q_point))

    def _on_left_mouse_button_up(self, event: QMouseEvent):
        """Commit drag, resize, selection, or Mario movement after release.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.
        """
        obj = self.object_at(event.position().toPoint())

        if self.mouse_mode == MODE_DRAG and self.dragging_happened:
            drag_end_point = self.to_level_point(event.position().toPoint())

            if self.drag_start_point != drag_end_point:
                self._stop_drag(drag_end_point)
            else:
                self.dragging_happened = False

        elif self.resizing_happened:
            self._stop_resize()

        elif self.selection_square.active:
            self._stop_selection_square()

        elif obj and obj.selected and not self._object_was_selected_on_last_click:
            # handle selected object on release to allow dragging

            if ctrl_is_pressed():
                # take selected object under cursor out of current selection
                selected_objects = self.get_selected_objects().copy()
                selected_objects.remove(obj)
                self.select_objects(selected_objects, replace_selection=True)
            else:
                # replace selection with only selected object
                self.select_objects([obj], replace_selection=True)

        elif self.mouse_mode == MODE_MOVE_MARIO:
            self._stop_mario_move()

        self.mouse_mode = MODE_FREE
        self._object_was_selected_on_last_click = False
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def _stop_drag(self, drag_end_point: Position):
        """Commit an object drag to the undo stack when positions changed.

        Parameters
        ----------
        drag_end_point : Position
            Model position where the drag ended.
        """
        if not self.dragging_happened:
            return

        move_happened = False

        for old_obj, new_obj in zip(self.objects_before_moving, self.get_selected_objects()):
            if old_obj.get_position() != new_obj.get_position():
                move_happened = True
                break

        if move_happened:
            self.undo_stack.push(
                MoveObjects(
                    self.level_ref,
                    self.objects_before_moving,
                    self.get_selected_objects(),
                )
            )

        self.objects_before_moving.clear()
        self.dragging_happened = False

    def scroll_to_objects(self, objects: list[InLevelObject]):
        """Scroll the containing area to selected objects.

        Parameters
        ----------
        objects : list[InLevelObject]
            Objects whose positions should be made visible.
        """
        if not objects:
            return

        min_x = min([obj.x_position for obj in objects]) * self.block_length
        min_y = min([obj.y_position for obj in objects]) * self.block_length

        # TODO not great, not terrible
        cast(QScrollArea, cast(QWidget, self.parent().parent())).ensureVisible(min_x, min_y)

    def level_safe_to_save(self) -> tuple[bool, str, str]:
        """Assess whether the edited level can be written safely.

        Managed ROMs compare the level's growth against Foundry-managed free
        space. Unmanaged ROMs check whether object or enemy streams would
        overlap original neighboring level data. The returned reason strings are
        user-facing diagnostics for save prompts and warnings.

        Returns
        -------
        tuple[bool, str, str]
            True when the level can be saved without violating size limits.
        """
        is_safe = True
        reason = ""
        additional_info = ""

        if not self.level_ref:
            return is_safe, reason, additional_info

        if ROM.additional_data.managed_level_positions:
            free_space_in_bank = ROM.additional_data.free_space_for_object_set(self.level.object_set_number)
            free_space_for_enemies = ROM.additional_data.free_space_for_enemies()

            additional_level_data = self.level.current_object_size() - self.level.object_size_on_disk
            additional_enemy_data = self.level.current_enemies_size() - self.level.enemy_size_on_disk

            if free_space_in_bank < additional_level_data:
                is_safe = False
                reason = "Not enough space in ROM"
                additional_info = "There is not enough space in the ROM for this level."

            elif free_space_for_enemies < additional_enemy_data:
                is_safe = False
                reason = "Not enough space in ROM"
                additional_info = "There is not enough space in the ROM for the enemies/items in this Level."

        else:
            if self.level_ref.too_many_level_objects():
                level = self._cuts_into_other_objects()

                is_safe = False
                reason = "Too many level objects."

                if level:
                    additional_info = f"Would overwrite data of original level '{level}'."
                else:
                    additional_info = (
                        "It wouldn't overwrite another level, but it might still overwrite other important data."
                    )

                additional_info += (
                    " If you deleted a bunch of objects and saved the level afterwards, this is probably a false alarm."
                )
            elif self.level_ref.too_many_enemies_or_items():
                level = self._cuts_into_other_enemies()

                is_safe = False
                reason = "Too many enemies or items."

                if level:
                    additional_info = f"Would probably overwrite enemy/item data of original level '{level}'."
                else:
                    additional_info = (
                        "It wouldn't overwrite enemy/item data of another level, "
                        "but it might still overwrite other important data."
                    )

                additional_info += (
                    " If you deleted a bunch of enemies and saved the level afterwards, this is probably a false alarm."
                )

        return is_safe, reason, additional_info

    def _cuts_into_other_enemies(self) -> str:
        """Identify the original level whose enemy data would be overlapped.

        The check compares the edited enemy-stream end against the stock ROM's
        enemy-offset table so unmanaged saves can warn about the most likely
        victim if the level has grown.

        Returns
        -------
        str
            Display name of the overlapped level, or an empty string.

        Raises
        ------
        ValueError
            If the input data or current state is invalid.
        """
        if self.level_ref is None:
            raise ValueError("Level is None")

        enemies_end = self.level_ref.enemies_end

        levels_by_enemy_offset = sorted(Level.offsets, key=lambda level: level.enemy_offset)

        level_index = bisect_right([level.enemy_offset for level in levels_by_enemy_offset], enemies_end) - 1

        found_level = levels_by_enemy_offset[level_index]

        if found_level.enemy_offset == self.level_ref.enemy_offset:
            return ""
        else:
            return f"World {found_level.game_world} - {found_level.name}"

    def _cuts_into_other_objects(self) -> str:
        """Identify the original level whose object data would be overlapped.

        The check compares the edited object-stream end against the sorted
        stock level-address table to identify the next original level that
        would most likely be overwritten by unmanaged growth.

        Returns
        -------
        str
            Display name of the overlapped level, or an empty string.

        Raises
        ------
        ValueError
            If the input data or current state is invalid.
        """
        if self.level_ref is None:
            raise ValueError("Level is None")

        end_of_level_objects = self.level_ref.objects_end

        level_index = (
            bisect_right(
                [level.rom_level_offset - HEADER_LENGTH for level in Level.sorted_offsets],
                end_of_level_objects,
            )
            - 1
        )

        found_level = Level.sorted_offsets[level_index]

        if found_level.rom_level_offset == self.level_ref.object_offset:
            return ""
        else:
            return f"World {found_level.game_world} - {found_level.name}"

    def from_m3l(self, data: bytearray):
        """Load level data from an M3L byte stream.

        Parameters
        ----------
        data : bytearray
            Raw bytes or bytearray being parsed.
        """
        self.level_ref.from_m3l(data)

    def add_enemy(self, enemy_type: int, q_point: QPoint, index=-1):
        """Add an enemy/item at a widget position.

        This helper converts widget coordinates into level coordinates before
        delegating to the model, which keeps enemy ordering and serialization
        rules inside ``Level`` rather than in the view.

        Parameters
        ----------
        enemy_type : int
            Enemy type identifier to place.
        q_point : QPoint
            Point in widget coordinates.
        index : int, optional
            Zero-based index of the item to access.

        Returns
        -------
        EnemyItem
            Enemy or item added to the level.
        """
        level_pos = self.to_level_point(q_point)

        return self.level_ref.add_enemy(enemy_type, level_pos, index)

    def dropEvent(self, event: QDropEvent):
        """Place a toolbar object dropped onto the level view.

        Parameters
        ----------
        event : QDropEvent
            Qt event delivered to the widget.
        """
        level_object = self._object_from_mime_data(event.mimeData())

        self.level.clear_selection()

        if isinstance(level_object, LevelObject):
            self.undo_stack.push(
                AddLevelObjectAt(
                    self,
                    event.position().toPoint(),
                    level_object.domain,
                    level_object.obj_index,
                    length=level_object.length,
                    selected=True,
                )
            )
        else:
            self.undo_stack.push(AddEnemyAt(self, event.position().toPoint(), level_object.obj_index, selected=True))

        event.accept()

        self.currently_dragged_object = None

        self.level_ref.data_changed.emit()
