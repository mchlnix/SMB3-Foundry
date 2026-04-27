"""Shared editing view for level and world-map rendering surfaces.

This module provides ``MainView``, the Qt widget base class used by both
editable level views and editable world-map views. It owns the interaction
rules that stay stable across those domains: grid-to-widget coordinate
conversion, zoom-dependent sizing, shared selection writes into ``LevelRef``,
toolbar drag/drop decoding, marquee selection, screenshot capture, and the
dispatch layer that hands concrete mouse gestures to specialized subclasses.

New maintainers usually want to read this file together with the concrete
renderers and view-specific interaction code in ``foundry.gui.visualization``.

See Also
--------
foundry.gui.visualization.level.LevelDrawer : Draws level data onto the shared
    widget surface.
foundry.gui.visualization.world.WorldDrawer : Draws world-map data onto the
    shared widget surface.
foundry.game.level.LevelRef : Shared editor reference that carries the loaded
    model and active selection.
"""

from contextlib import suppress
from typing import Sequence
from warnings import warn

from PySide6.QtCore import QMimeData, QPoint, QSize
from PySide6.QtGui import (
    QContextMenuEvent,
    QDragEnterEvent,
    QDragMoveEvent,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    Qt,
)
from PySide6.QtWidgets import QSizePolicy, QWidget

from foundry import ctrl_is_pressed
from foundry.game.gfx.block_cache import draw_enemy_item, draw_level_object
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects.in_level.enemy_item import EnemyItem
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from foundry.game.gfx.objects.in_level.level_object import LevelObject
from foundry.game.gfx.objects.object_like import ObjectLike
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.ContextMenu import ContextMenu
from foundry.gui.settings import Settings
from smb3parse.data_points import Position

from .level.LevelDrawer import LevelDrawer
from .SelectionSquare import SelectionSquare
from .world.WorldDrawer import WorldDrawer

MIME_DATA_DROP_OBJECT = "application/level-object"

HIGHEST_ZOOM_LEVEL = 8  # on linux, at least
LOWEST_ZOOM_LEVEL = 1 / 16  # on linux, but makes sense with 16x16 blocks


DROP_TYPE_LEVEL_OBJECT = 0
DROP_TYPE_ENEMY = 1

# mouse modes
MODE_FREE = 0
MODE_DRAG = 1
MODE_RESIZE_HORIZ = 2
MODE_RESIZE_VERT = 4
MODE_PUT_TILE = 8
MODE_SELECTION_SQUARE = 16
MODE_MOVE_MARIO = 32
MODE_RESIZE_DIAG = MODE_RESIZE_HORIZ | MODE_RESIZE_VERT
RESIZE_MODES = [MODE_RESIZE_HORIZ, MODE_RESIZE_VERT, MODE_RESIZE_DIAG]


class MainView(QWidget):
    """Base widget for editable level and world-map views.

    ``MainView`` is the shared interaction shell for both level and world-map
    editors. It defines the widget-side rules that stay the same across both
    domains: conversion between Qt pixels and editor grid coordinates, zoom-
    dependent sizing, selection synchronization with ``LevelRef``, drag/drop
    previews from the object toolbars, drag-selection rectangles, screenshots,
    and dispatch into subclass-specific mouse modes. Concrete views supply the
    renderer and the domain-specific handlers that turn those gestures into
    undoable commands.

    Parameters
    ----------
    parent : QWidget | None
        Parent Qt widget that owns this object.
    level : LevelRef
        Reference to the edited level or world map.
    settings : Settings
        Application settings used to configure the widget behavior.
    context_menu : ContextMenu | None
        Context menu populated or displayed by the widget.

    Attributes
    ----------
    _object_was_selected_on_last_click : bool
        Whether the active mouse press already changed selection.
    block_length : int
        Pixel size of one editor grid cell at the active zoom factor.
    context_menu : ContextMenu | None
        Context menu shown for object or background actions in the concrete view.
    currently_dragged_object : InLevelObject | None
        Toolbar object previewed over the view during drag/drop.
    drawer : LevelDrawer | WorldDrawer
        Renderer supplied by the concrete view class.
    last_mouse_position : Position
        Last editor-grid position seen during a drag or hover gesture.
    level_ref : LevelRef
        Shared model reference holding the edited map/level and current selection.
    mouse_mode : int
        Interaction mode currently interpreted by subclass mouse handlers.
    read_only : bool
        Whether editing gestures should be ignored and forwarded to Qt only.
    selection_square : SelectionSquare
        Rectangle helper that tracks marquee-selection state in widget space.
    settings : Settings
        View settings object delegated to the drawer and interaction code.
    zoom : float
        Active zoom multiplier used to size grid cells and rendering output.
    """

    drawer: LevelDrawer | WorldDrawer

    def __init__(
        self,
        parent: QWidget | None,
        level: LevelRef,
        settings: Settings,
        context_menu: ContextMenu | None,
    ):
        """Create the shared editable view state.

        The base widget starts in read/write mode with drag/drop enabled,
        connects redraw signals from ``LevelRef``, and initializes the shared
        coordinate and selection helpers that both view types build on.

        Parameters
        ----------
        parent : QWidget | None
            Parent Qt widget that owns this object.
        level : LevelRef
            Reference to the edited level or world map.
        settings : Settings
            Application settings used to configure the widget behavior.
        context_menu : ContextMenu | None
            Context menu populated or displayed by the widget.
        """
        super(MainView, self).__init__(parent)

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)

        self.level_ref: LevelRef = level
        self.level_ref.data_changed.connect(self.update)
        self.level_ref.needs_redraw.connect(self.update)

        self.settings = settings

        self.context_menu = context_menu
        self.last_mouse_position = Position.from_xy(0, 0)

        self.zoom = 1.0
        self.block_length = int(Block.SIDE_LENGTH * self.zoom)
        self.selection_square = SelectionSquare()

        self.read_only = False

        self._object_was_selected_on_last_click = False
        """whether an object was selected with the current click; will be cleared, on release of the mouse button"""

        # dragged in from the object toolbar
        self.currently_dragged_object: InLevelObject | None = None

    @property
    def settings(self):
        """Drawer settings shared by rendering and interaction code.

        The view and its drawer read the same settings object so zoom, overlay,
        and preview decisions stay coordinated across repaint and input paths.

        Returns
        -------
        Settings
            Settings object used by the renderer and view logic.
        """
        return self.drawer.settings

    @settings.setter
    def settings(self, value):
        """Store one settings object on the active drawer.

        Parameters
        ----------
        value : Settings
            Settings object used by the renderer and view logic.
        """
        self.drawer.settings = value

    def sizeHint(self) -> QSize:
        """Qt widget size implied by model bounds and zoom level.

        The size hint keeps scroll areas, drag previews, and screenshot output
        aligned with the same grid dimensions used for painting, hit tests, and
        the view's resize/update workflow.

        Returns
        -------
        QSize
            The recommended Qt size.
        """
        if not self.level_ref:
            return super(MainView, self).sizeHint()
        else:
            width, height = self.level_ref.size

            return QSize(width * self.block_length, height * self.block_length)

    def update(self):
        """Resize to model bounds before the next repaint pass.

        ``LevelRef`` redraw signals route through this override so geometry and
        paint state stay synchronized after zoom or data changes.
        """
        self.resize(self.sizeHint())

        super(MainView, self).update()

    def get_painter(self):
        """Painter bound to the Qt view surface for one repaint pass.

        Concrete level and world views use this helper when they need a paint
        device that matches the widget's live rendering state.

        Returns
        -------
        QPainter
            Painter targeting this widget.
        """
        return QPainter(self)

    def _select_objects_on_click(self, event: QMouseEvent) -> bool:
        """Select the object under the cursor on mouse press.

        Mouse-down selection updates ``LevelRef`` before drag or resize modes
        begin, which keeps later gesture handling and menu actions pointed at
        the same selected editor objects.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.

        Returns
        -------
        bool
            ``True`` when the click hit an object.
        """
        self.last_mouse_position = self.to_level_point(event.position().toPoint())

        clicked_object = self.object_at(event.position().toPoint())

        clicked_on_background = clicked_object is None

        if clicked_on_background:
            self._select_object(None)
        else:
            if event.button() & Qt.MouseButton.LeftButton:
                self.mouse_mode = MODE_DRAG

            selected_objects = self.get_selected_objects()

            nothing_selected = not selected_objects

            # selected objects are handled on click release
            if nothing_selected or clicked_object not in selected_objects:
                self._select_object(clicked_object)
                self._object_was_selected_on_last_click = True

        return not clicked_on_background

    def mousePressEvent(self, event: QMouseEvent):
        """Dispatch mouse presses to concrete view handlers.

        The base class owns the button-to-mode routing shared by level and
        world views, while subclasses provide the domain-specific editing
        behavior for each button path in the same input-state workflow.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.

        Returns
        -------
        object
            Result returned by the subclass or base Qt handler, if any.
        """
        if self.read_only:
            return super(MainView, self).mousePressEvent(event)

        pressed_button = event.button()

        if pressed_button == Qt.MouseButton.LeftButton:
            return self._on_left_mouse_button_down(event)

        elif pressed_button == Qt.MouseButton.MiddleButton:
            return self._on_middle_mouse_button_down(event)

        elif pressed_button == Qt.MouseButton.RightButton:
            return self._on_right_mouse_button_down(event)

        else:
            return super(MainView, self).mousePressEvent(event)

    def _on_left_mouse_button_down(self, event: QMouseEvent):
        """Hook for subclass left-button press handling.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.
        """
        pass

    def _on_middle_mouse_button_down(self, event: QMouseEvent):
        """Hook for subclass middle-button press handling.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.
        """
        pass

    def _on_right_mouse_button_down(self, event: QMouseEvent):
        """Hook for subclass right-button press handling.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.
        """
        pass

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Dispatch mouse releases to concrete view handlers.

        Release routing mirrors ``mousePressEvent`` so drag, resize, and
        placement workflows can finish in subclass code without duplicating the
        shared button dispatch.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.

        Returns
        -------
        object
            Result returned by the subclass or base Qt handler, if any.
        """
        if self.read_only:
            return super(MainView, self).mouseReleaseEvent(event)

        released_button = event.button()

        if released_button == Qt.MouseButton.LeftButton:
            return self._on_left_mouse_button_up(event)

        elif released_button == Qt.MouseButton.RightButton:
            return self._on_right_mouse_button_up(event)
        else:
            return super(MainView, self).mouseReleaseEvent(event)

    def _on_left_mouse_button_up(self, event: QMouseEvent):
        """Hook for subclass left-button release handling.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.
        """
        pass

    def _on_right_mouse_button_up(self, event: QMouseEvent):
        """Hook for subclass right-button release handling.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.
        """
        pass

    def select_objects(self, objects, replace_selection=False):
        """Publish one selection update through ``LevelRef`` and repaint.

        Mouse clicks, marquee drags, paste operations, and drag/drop insertion
        all flow through this method so every editor surface sees the same
        selected-object set. The helper delegates the actual selection write to
        ``_set_selected_objects`` so Ctrl-extended selection and explicit
        replacement follow the same rules before the repaint/update path
        refreshes the view, status widgets, and context-menu state.

        Parameters
        ----------
        objects : Sequence[ObjectLike]
            Level objects and enemies or items to select.
        replace_selection : bool, optional
            Whether to replace the existing selection instead of extending it.
        """
        self._set_selected_objects(objects, replace_selection)

        self.update()

    def _select_object(self, obj=None):
        """Select one object or clear selection.

        Parameters
        ----------
        obj : ObjectLike | None, optional
            Object to select.
        """
        if obj is not None:
            self.select_objects([obj])
        else:
            self.select_objects([])

    def _set_selected_objects(self, objects, replace_selection=False):
        """Write one selection set into the shared editor reference.

        Selection lives on ``LevelRef`` so lists, views, and status widgets can
        all react to the same state instead of each widget tracking its own
        copy.

        Parameters
        ----------
        objects : Sequence[ObjectLike]
            Objects to select.
        replace_selection : bool, optional
            Whether to replace rather than extend the existing selection.
        """
        if self.level_ref.selected_objects == objects:
            return

        if ctrl_is_pressed() and not replace_selection:
            selected_items = self.level_ref.selected_objects.copy()

            for level_object in objects:
                if level_object not in selected_items:
                    selected_items.append(level_object)
        else:
            selected_items = objects

        self.level_ref.selected_objects = selected_items

    def get_selected_objects(self):
        """Selection state owned by the shared editor reference.

        Lists, views, and status widgets read this shared state so every UI
        surface reacts to the same selection workflow.

        Returns
        -------
        list[ObjectLike]
            Currently selected objects.
        """
        return self.level_ref.selected_objects

    def select_all(self):
        """Select every object exposed by the active model."""
        self.select_objects(self.level_ref.get_all_objects())

    def to_level_point(self, q_point: QPoint) -> Position:
        """Convert widget coordinates to model grid coordinates.

        Hit testing, drag previews, and paste anchors all pass through this
        coordinate conversion so they stay on the same block grid as painting.

        Parameters
        ----------
        q_point : QPoint
            Point in widget coordinates.

        Returns
        -------
        Position
            Point converted into level coordinates.
        """
        screen_x = q_point.x()
        screen_y = q_point.y()

        level_x = screen_x // self.block_length
        level_y = screen_y // self.block_length

        return Position.from_xy(level_x, level_y)

    def from_level_point(self, x, y):
        """Convert model grid coordinates to widget coordinates.

        This is the inverse mapping used by cursor feedback, selection frames,
        and preview overlays that need Qt pixel positions from block-grid data.

        Parameters
        ----------
        x : int
            Horizontal coordinate.
        y : int
            Vertical coordinate.

        Returns
        -------
        QPoint
            Widget-coordinate center of the model grid cell.
        """
        screen_x = x * self.block_length + self.block_length // 2
        screen_y = y * self.block_length + self.block_length // 2

        return QPoint(screen_x, screen_y)

    def object_at(self, q_point: QPoint) -> ObjectLike | None:
        """Hit-test the active model at one Qt view position.

        This gives selection and context-menu code a single hit-test entry point that converts Qt
        widget coordinates into level coordinates internally.

        Parameters
        ----------
        q_point : QPoint
            Point in widget coordinates.

        Returns
        -------
        ObjectLike | None
            Object at the queried coordinates, if one exists.
        """
        return self.level_ref.level.object_at(*self.to_level_point(q_point).xy)

    def make_screenshot(self):
        """Capture the rendered widget surface as a Qt pixmap.

        Debug export and helper tooling use this after layout and paint state
        have already been synchronized by ``update``.

        Returns
        -------
        QPixmap | None
            Screenshot pixmap, or ``None`` when no level is loaded.
        """
        if self.level_ref is None:
            return

        return self.grab()

    def contextMenuEvent(self, event: QContextMenuEvent):
        """Gate Qt context menus based on editable view state.

        Read-only surfaces skip editor actions here so the same widget can be
        reused for preview-only contexts without exposing mutation commands.

        Parameters
        ----------
        event : QContextMenuEvent
            Qt event delivered to the widget.

        Returns
        -------
        object
            Result returned by the base Qt handler, if any.
        """
        if self.read_only:
            return False
        else:
            return super(MainView, self).contextMenuEvent(event)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Accept toolbar object drags.

        Parameters
        ----------
        event : QDragEnterEvent
            Qt event delivered to the widget.
        """
        if event.mimeData().hasFormat(MIME_DATA_DROP_OBJECT):
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragMoveEvent):
        """Preview the dragged toolbar object at the hovered cell.

        Parameters
        ----------
        event : QDragMoveEvent
            Qt event delivered to the widget.
        """
        level_object = self._object_from_mime_data(event.mimeData())

        level_object.set_position(*self.to_level_point(event.position().toPoint()).xy)

        self.currently_dragged_object = level_object

        self.repaint()

    def dragLeaveEvent(self, event):
        """Clear the drag preview when the cursor leaves the view.

        Parameters
        ----------
        event : QDragLeaveEvent
            Qt event delivered to the widget.
        """
        self.currently_dragged_object = None

        self.repaint()

    def _object_from_mime_data(self, mime_data: QMimeData) -> InLevelObject:
        """Decode one toolbar drag payload into a placeable editor object.

        Drag/drop uses this bridge to turn MIME bytes back into the same
        object-factory products that placement commands, drag previews, and
        undoable insertion workflows expect.

        Parameters
        ----------
        mime_data : QMimeData
            Data for the mime value.

        Returns
        -------
        InLevelObject
            Object decoded from MIME data.
        """
        object_type, *object_bytes = mime_data.data(MIME_DATA_DROP_OBJECT).data()

        if object_type == DROP_TYPE_LEVEL_OBJECT:
            domain = object_bytes[0] >> 5
            object_index = object_bytes[2]

            if len(object_bytes) > 3:
                length: int | None = object_bytes[3]
            else:
                length = None

            return self.level_ref.level.object_factory.from_properties(domain, object_index, 0, 0, length, 999)

        else:
            enemy_id = object_bytes[0]

            return self.level_ref.level.enemy_item_factory.from_properties(enemy_id, 0, 0)

    def paste_objects_at(self, paste_data: tuple[Sequence[ObjectLike], Position], pos: Position):
        """Paste copied objects relative to a target position.

        The copied origin is preserved so multi-object pastes keep their local
        layout while moving as one group through the editor workflow.

        Parameters
        ----------
        paste_data : tuple[Sequence[ObjectLike], Position]
            Copied objects and their copied-origin anchor.
        pos : Position
            Target paste position.
        """
        objects, origin = paste_data

        pasted_objects = []

        for obj in objects:
            obj_pos = Position.from_xy(*obj.get_position())

            paste_pos = pos + (obj_pos - origin)

            try:
                pasted_objects.append(self.level_ref.paste_object_at(paste_pos, obj))
            except ValueError:
                warn("Tried pasting outside of level.", RuntimeWarning)

        self.select_objects(pasted_objects)

    def set_zoom(self, zoom):
        """Apply one zoom factor to the shared grid-size state.

        Zoom updates the block length that drives coordinate conversion,
        screenshot sizing, drag previews, and the next repaint pass.

        Parameters
        ----------
        zoom : float
            Zoom factor used for display scaling.
        """
        if not (LOWEST_ZOOM_LEVEL <= zoom <= HIGHEST_ZOOM_LEVEL):
            return

        self.zoom = zoom
        self.block_length = int(Block.SIDE_LENGTH * self.zoom)

        # TODO Create a signal the main window can connect to instead? level selector throws attribute error
        with suppress(AttributeError):
            self.parent().parent().parent().update()  # update the main window

        self.update()

    def zoom_out(self):
        """Decrease zoom by one step."""
        self.set_zoom(self.zoom - 0.25)

    def zoom_in(self):
        """Increase zoom by one step."""
        self.set_zoom(self.zoom + 0.25)

    def _start_selection_square(self, point: QPoint):
        """Start drag-selection at a widget point.

        Parameters
        ----------
        point : QPoint
            Widget-coordinate drag start point.
        """
        self.selection_square.start(point)

    def _set_selection_end(self, event: QMouseEvent):
        """Update drag-selection and selected objects.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.
        """
        if not self.selection_square.is_active():
            return

        self.selection_square.set_current_end(event.position().toPoint())

        sel_rect = self.selection_square.get_adjusted_rect(self.block_length, self.block_length)

        touched_objects = [obj for obj in self.level_ref.get_all_objects() if sel_rect.intersects(obj.get_rect())]

        if touched_objects != self.level_ref.selected_objects:
            self._set_selected_objects(
                touched_objects,
                not event.modifiers() & Qt.KeyboardModifier.ShiftModifier,
            )

        self.update()

    def _stop_selection_square(self):
        """Stop drag-selection and repaint."""
        self.selection_square.stop()

        self.update()

    def paintEvent(self, event: QPaintEvent):
        # !!! Don't put breakpoints here, the cursor will get stuck and you'll have to pkill pycharm.
        """Draw the model, selection rectangle, and drag preview.

        Parameters
        ----------
        event : QPaintEvent
            Qt event delivered to the widget.
        """
        painter = self.get_painter()

        if not self.level_ref:
            return

        self.drawer.block_length = self.block_length

        self.drawer.draw(painter, self.level_ref.level)

        self.selection_square.draw(painter)

        if self.currently_dragged_object is not None:
            if isinstance(self.currently_dragged_object, LevelObject):
                draw_level_object(
                    self.currently_dragged_object,
                    painter,
                    self.block_length,
                    self.settings.value("level_view/block_transparency"),
                    self.settings.value("level_view/block_animation"),
                )
            else:
                assert isinstance(self.currently_dragged_object, EnemyItem)

                draw_enemy_item(
                    self.currently_dragged_object,
                    painter,
                    self.block_length,
                )


def object_to_mime_data(in_level_object: InLevelObject) -> QMimeData:
    """Serialize an object for toolbar drag-and-drop.

    Parameters
    ----------
    in_level_object : InLevelObject
        Object to serialize.

    Returns
    -------
    QMimeData
        MIME data containing the object kind and raw bytes.
    """
    mime_data = QMimeData()

    object_bytes = bytearray()

    if isinstance(in_level_object, LevelObject):
        object_bytes.append(DROP_TYPE_LEVEL_OBJECT)
    else:
        object_bytes.append(DROP_TYPE_ENEMY)

    object_bytes.extend(in_level_object.to_bytes())

    mime_data.setData(MIME_DATA_DROP_OBJECT, object_bytes)

    return mime_data
