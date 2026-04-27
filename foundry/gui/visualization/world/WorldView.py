"""Interactive world-map editing view for SMB3 overworld data.

This module owns the Qt view that turns world-map model state into an editable
surface. :class:`WorldView` sits between
:class:`~foundry.game.level.WorldMap.WorldMap` and
:class:`~foundry.gui.visualization.world.WorldDrawer.WorldDrawer`: it converts
mouse gestures into undoable world-map commands, manages hover and selection
state, and keeps tooltip previews, drag staging, and tile-paint workflow
aligned with the visible world-map layers.

See Also
--------
foundry.game.level.WorldMap
    World-map model mutated and queried by the view.
foundry.gui.visualization.MainView
    Shared visualization base class that provides selection and coordinate
    conversion helpers.
foundry.gui.visualization.world.WorldDrawer
    Renderer that paints the world-map layers and animation frames owned by the
    view workflow.
"""

from typing import cast

from PySide6.QtCore import QPoint, QSize, QTimer
from PySide6.QtGui import (
    QCursor,
    QKeySequence,
    QMouseEvent,
    QPainter,
    QPixmap,
    QShortcut,
    Qt,
    QUndoStack,
)
from PySide6.QtWidgets import QToolTip, QWidget

from foundry import get_level_thumbnail, pixmap_to_base64
from foundry.game.gfx import BlockCache
from foundry.game.gfx.block_cache import get_worldmap_tile
from foundry.game.gfx.objects.in_level.level_object import LevelObject
from foundry.game.gfx.objects.world_map.map_object import MapObject
from foundry.game.gfx.objects.world_map.map_tile import MapTile
from foundry.game.gfx.Palette import load_palette_group
from foundry.game.level.LevelRef import LevelRef
from foundry.game.level.WorldMap import WorldMap
from foundry.gui.settings import Settings
from foundry.gui.visualization.MainView import (
    MODE_DRAG,
    MODE_FREE,
    MODE_PUT_TILE,
    MODE_SELECTION_SQUARE,
    MainView,
)
from foundry.gui.visualization.world.WorldDrawer import WorldDrawer
from scribe.gui.commands import (
    MoveMapObject,
    MoveTile,
    PutTile,
    SetEnemyAddress,
    SetLevelAddress,
    SetObjectSet,
    SetSpriteItem,
    SetSpriteType,
)
from scribe.gui.world_view_context_menu import WorldContextMenu
from smb3parse.constants import (
    MUSHROOM_OBJECT_SET,
    OBJECT_SET_NAMES,
    SPADE_BONUS_OBJECT_SET,
    TILE_NAMES,
)
from smb3parse.data_points import Position
from smb3parse.levels import FIRST_VALID_ROW, WORLD_MAP_BLANK_TILE_ID, WORLD_MAP_HEIGHT


class WorldView(MainView):
    """Interactive editor view for SMB3 world maps.

    The view converts Qt mouse input into world-map tile edits, object
    selection, map-object movement, fill operations, and undo-stack commands.
    Rendering is delegated to
    :class:`~foundry.gui.visualization.world.WorldDrawer.WorldDrawer` while
    this class owns hit testing, paint/fill mode, map-object selection,
    level-preview tooltips, and the staging state used to turn drags and tile
    painting into Scribe world-map commands.

    Parameters
    ----------
    parent : QWidget | None
        Parent Qt widget that owns this object.
    level : LevelRef
        Reference to the edited world map.
    settings : Settings
        Application settings used to configure the widget behavior.
    context_menu : WorldContextMenu | None, optional
        Context menu populated or displayed by the widget.

    Attributes
    ----------
    _tile_to_put : int
        Tile id staged for paint and flood-fill mode.
    context_menu : WorldContextMenu
        Context menu used for world-map editing actions.
    drag_start_point : Position
        World-map grid position where the active drag began.
    dragging_happened : bool
        Whether the active drag gesture moved a tile or map object.
    drawer : WorldDrawer
        Renderer for world-map layers, overlays, and animation state.
    last_mouse_position : Position
        Last world-map grid position seen during a drag gesture.
    mouse_mode : int
        Active interaction mode such as free, drag, paint-tile, or marquee select.
    redraw_timer : QTimer | None
        Timer that advances animated world-map tiles when enabled.
    selected_object : MapObject | None
        Selected non-tile map object moved independently of tile selection.
    """

    context_menu: WorldContextMenu

    def __init__(
        self,
        parent: QWidget | None,
        level: LevelRef,
        settings: Settings,
        context_menu: WorldContextMenu | None = None,
    ):
        """Create the world-map editor view.

        The view installs a
        :class:`~foundry.gui.visualization.world.WorldDrawer.WorldDrawer`,
        hooks animation and palette refreshes to world-map changes,
        initializes the tile-painting state, and prepares the transient drag
        state later consumed by Scribe undo commands.

        Parameters
        ----------
        parent : QWidget | None
            Parent Qt widget that owns this object.
        level : LevelRef
            Reference to the edited world map.
        settings : Settings
            Application settings used to configure the widget behavior.
        context_menu : WorldContextMenu | None, optional
            Context menu populated or displayed by the widget.
        """
        self.drawer = WorldDrawer()
        self.redraw_timer: QTimer | None = None

        super(WorldView, self).__init__(parent, level, settings, context_menu)

        level.palette_changed.connect(self.update_palette)
        level.palette_changed.connect(self.update_anim_timer)
        level.level_changed.connect(self.update_anim_timer)

        self.update_anim_timer()

        self._tile_to_put: int = WORLD_MAP_BLANK_TILE_ID

        self.mouse_mode = MODE_FREE

        self.drag_start_point = Position.from_xy(0, 0)
        self.last_mouse_position = Position.from_xy(0, 0)

        self.selected_object: MapObject | None = None

        self.dragging_happened = False

        # TODO: update
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

        QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_A), self, self.select_all)

    def next_anim_step(self):
        """Advance animated map tiles and repaint the view."""
        BlockCache.next_frame()
        self.drawer.anim_frame += 1
        self.drawer.anim_frame %= 4

        self.repaint()

    def update_anim_timer(self):
        """Start or stop the world-map animation timer."""
        if not self.level_ref:
            return

        if self.redraw_timer is not None:
            self.redraw_timer.stop()
            self.drawer.anim_frame = 0

        if self.world.data.frame_tick_count and self.settings.value("world_view/animated_tiles"):
            redraw_timer = QTimer(self)
            redraw_timer.setInterval(1000 / 60 * self.world.data.frame_tick_count)
            redraw_timer.timeout.connect(self.next_anim_step)
            redraw_timer.start()

            self.redraw_timer = redraw_timer

    def sizeHint(self) -> QSize:
        """Report the drawable world-map extent to Qt layout code.

        Scroll areas and parent layouts read this size before the widget paints
        or translates cursor coordinates into overworld positions. Using the
        edited map dimensions here keeps the optional border rows, drawer
        output, hover previews, and drag-selection geometry aligned to the
        same grid that later mouse handlers and undoable edit commands use.

        Returns
        -------
        QSize
            The recommended Qt size.
        """
        size = super(WorldView, self).sizeHint()

        if self.settings.value("world_view/show_border"):
            size += QSize(0, 3) * self.block_length

        return size

    @property
    def settings(self):
        """Drawer settings shared by world-map painting and hover workflow.

        Border visibility, animation, and level-preview behavior all read this
        same settings object while the view is rendering and handling input.

        Returns
        -------
        Settings
            Settings object used for world-map rendering and interaction options.
        """
        return self.drawer.settings

    @settings.setter
    def settings(self, value):
        """Store one settings object on the world-map drawer.

        Parameters
        ----------
        value : Settings
            Settings object used for world-map rendering and interaction options.
        """
        self.drawer.settings = value

    @property
    def undo_stack(self) -> QUndoStack:
        """Undo stack used for committed Scribe world-map commands.

        Tile painting, pointer edits, sprite movement, and fill operations all
        commit through this shared stack instead of mutating map state
        invisibly.

        Returns
        -------
        QUndoStack
            Main-window undo stack used by committed world-map edits.
        """
        return cast(QUndoStack, self.window().findChild(QUndoStack, "undo_stack"))

    @property
    def world(self) -> WorldMap:
        """Edited world-map model behind the active view workflow.

        Input handlers, hover previews, and drawing all route through this
        typed accessor instead of repeatedly unpacking :attr:`level_ref`.

        Returns
        -------
        foundry.game.level.WorldMap.WorldMap
            World-map model referenced by :attr:`level_ref`.
        """
        return self.level_ref.level

    def update_palette(self):
        """Reload map-tile palette data after a palette change."""
        for map_tile in self.world.objects:
            map_tile.block._palette_group = load_palette_group(
                self.world.object_set.number, self.world.data.palette_index
            )
            map_tile.change_type(map_tile.block.index)

        self.update()

    def set_mouse_mode(self, new_mode: int, event: QMouseEvent | None):
        """Switch the world-map interaction mode.

        Cursor state, drag anchors, and selection-square offsets all change
        here so later mouse events can interpret the same shared world-view
        mode consistently.

        Parameters
        ----------
        new_mode : int
            Interaction mode constant.
        event : QMouseEvent | None
            Qt event delivered to the widget.
        """
        if new_mode == MODE_PUT_TILE:
            tile_pixmap = QPixmap(QSize(self.block_length, self.block_length))

            painter = QPainter(tile_pixmap)
            get_worldmap_tile(self._tile_to_put, self.world.data.palette_index).draw(painter, 0, 0, self.block_length)
            painter.end()

            self.setCursor(QCursor(tile_pixmap))

        elif new_mode == MODE_SELECTION_SQUARE:
            if event is None:
                return

            if self.settings.value("world_view/show_border"):
                self.selection_square.set_offset(0, 0)
            else:
                self.selection_square.set_offset(0, FIRST_VALID_ROW)

            self._start_selection_square(event.position().toPoint())

        elif new_mode == MODE_DRAG:
            if event is None:
                return

            self.drag_start_point = self.to_level_point(event.position().toPoint())
            self.last_mouse_position = self.drag_start_point
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

        elif new_mode == MODE_FREE:
            self._tile_to_put = WORLD_MAP_BLANK_TILE_ID

            self._object_was_selected_on_last_click = False
            self.setCursor(Qt.CursorShape.ArrowCursor)

        self.mouse_mode = new_mode

    def on_put_tile(self, tile_id: int):
        """Enter tile painting mode with a tile id.

        Parameters
        ----------
        tile_id : int
            Identifier of the tile.
        """
        self._tile_to_put = tile_id
        self.set_mouse_mode(MODE_PUT_TILE, None)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Update hover previews, tile painting, dragging, or selection.

        The method coordinates transient world-view state for tile painting,
        drag previews, and level-entry tooltips before any undo command is
        committed.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.

        Returns
        -------
        object
            Result returned by the base view handler, if any.
        """
        x, y = self.to_level_point(event.position().toPoint()).xy
        level_under_cursor = self.world.level_pointer_at(x, y) is not None

        if level_under_cursor:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

        show_level_preview = self.mouse_mode == MODE_FREE and self.settings.value("world_view/show_level_previews")

        if not show_level_preview or not self._set_level_thumbnail(event):
            self.setToolTip("")
            QToolTip.hideText()

        if self.read_only:
            return super(WorldView, self).mouseMoveEvent(event)

        if self.mouse_mode == MODE_PUT_TILE and event.buttons() & Qt.MouseButton.LeftButton:
            level_pos = self.to_level_point(event.position().toPoint())

            tile = self.world.object_at(*level_pos.xy)

            if tile is not None and tile.type != self._tile_to_put:
                self.undo_stack.push(PutTile(self.world, level_pos, self._tile_to_put))
                self.update()
        elif self.mouse_mode == MODE_DRAG:
            self._dragging(event)

        elif self.selection_square.active:
            self._set_selection_end(event)

        return super(WorldView, self).mouseMoveEvent(event)

    def _set_level_thumbnail(self, event: QMouseEvent):
        """Update the tooltip preview for the hovered level entry.

        Pointer hit testing, thumbnail generation, and tooltip visibility all
        flow through this helper so hover state stays coordinated.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.

        Returns
        -------
        bool
            ``True`` when a thumbnail tooltip was shown.
        """
        if self.mouse_mode != MODE_FREE:
            return False

        x, y = self.to_level_point(event.position().toPoint()).xy

        if not self.world.point_in(x, y):
            return False

        if (level_pointer := self.world.level_pointer_at(x, y)) is None:
            return False

        if level_pointer.data.object_set in (MUSHROOM_OBJECT_SET, SPADE_BONUS_OBJECT_SET):
            return False

        if self.read_only:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

        try:
            level_name = self.world.level_name_at_position(x, y)

            object_set_name = OBJECT_SET_NAMES[level_pointer.data.object_set]

            image_data = get_level_thumbnail(
                level_pointer.data.object_set,
                level_pointer.data.level_address,
                level_pointer.data.enemy_address,
            )

            self.setToolTip(
                f"<b>{level_name}</b><br/>"
                f"<u>Type:</u> {object_set_name} "
                f"<u>Objects:</u> {level_pointer.data.level_address:#x} "
                f"<u>Enemies:</u> {level_pointer.data.enemy_address:#x}<br/>"
                f"<img src='data:image/png;base64,{pixmap_to_base64(image_data)}'>"
            )

            return True
        except ValueError:
            return False

    def _on_right_mouse_button_up(self, event):
        """Cancel the active mode or open the world context menu.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.
        """
        if not self.mouse_mode == MODE_FREE:
            self.set_mouse_mode(MODE_FREE, event)
        else:
            menu_pos = self.mapToGlobal(event.position().toPoint())

            self.context_menu.popup(menu_pos)

    def _fill_tile(self, tile_to_fill_in: int, x, y):
        """Flood-fill matching map tiles from one starting coordinate.

        Shift-fill uses this recursive helper to stage a connected tile-region
        replacement before the enclosing undo macro is closed.

        Parameters
        ----------
        tile_to_fill_in : int
            Tile id being replaced.
        x : int
            Horizontal coordinate.
        y : int
            Vertical coordinate.
        """
        if tile_to_fill_in == self._tile_to_put:
            return

        if x < 0 or x >= self.world.internal_world_map.width:
            return

        if y < FIRST_VALID_ROW or y >= FIRST_VALID_ROW + WORLD_MAP_HEIGHT:
            return

        if (tile := self.world.object_at(x, y)) is not None and tile.type == tile_to_fill_in:
            self.undo_stack.push(PutTile(self.world, Position.from_xy(x, y), self._tile_to_put))
        else:
            return

        self._fill_tile(tile_to_fill_in, x + 1, y)
        self._fill_tile(tile_to_fill_in, x - 1, y)
        self._fill_tile(tile_to_fill_in, x, y + 1)
        self._fill_tile(tile_to_fill_in, x, y - 1)

    def to_level_point(self, q_point) -> Position:
        """Convert widget coordinates to world-map tile coordinates.

        The conversion also accounts for the optional border rows so hit
        testing and paint operations land on the same world-map data cells.

        Parameters
        ----------
        q_point : QPoint
            Point in widget coordinates.

        Returns
        -------
        Position
            Point converted into level coordinates.
        """
        pos = super(WorldView, self).to_level_point(q_point)

        if not self.settings.value("world_view/show_border"):
            pos += Position.from_xy(0, FIRST_VALID_ROW)

        return pos

    def _on_middle_mouse_button_down(self, event: QMouseEvent):
        """Pick the map tile under the cursor for painting.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.
        """
        x, y = self.to_level_point(event.position().toPoint()).xy

        if not self.world.point_in(x, y):
            return

        if self.mouse_mode != MODE_FREE:
            return

        obj = self.world.objects[Position.from_xy(x, y).tile_data_index]

        assert obj is not None

        self.on_put_tile(obj.type)

    def _visible_object_at(self, point: QPoint) -> MapObject:
        """Resolve a view position to the topmost visible world-map object.

        Visibility settings are checked in draw order so selection and dragging
        operate on the same object layer stack the person can currently see,
        and the resolved object can feed the left-click path that decides
        whether the gesture should select tiles, pointers, sprites, or map
        structures before the drag workflow captures that target.

        Parameters
        ----------
        point : QPoint
            Point being converted, tested, or applied.

        Returns
        -------
        MapObject
            Visible object at the queried position, if one exists.
        """
        level_x, level_y = self.to_level_point(point).xy

        obj = None

        if self.drawer.settings.value("world_view/show_pipes"):
            obj = self.world.pipe_at(level_x, level_y)

        if not obj and self.drawer.settings.value("world_view/show_locks"):
            obj = self.world.locks_at(level_x, level_y)

        if not obj and self.drawer.settings.value("world_view/show_airship_paths"):
            obj = self.world.airship_point_at(
                level_x,
                level_y,
                self.drawer.settings.value("world_view/show_airship_paths"),
            )

        if not obj and self.drawer.settings.value("world_view/show_start_position"):
            if self.world.start_pos.pos == Position.from_xy(level_x, level_y):
                obj = self.world.start_pos

        if not obj and self.drawer.settings.value("world_view/show_sprites"):
            obj = self.world.sprite_at(level_x, level_y)

        if not obj and self.drawer.settings.value("world_view/show_level_pointers"):
            obj = self.world.level_pointer_at(level_x, level_y)

        if not obj:
            obj = self.world.objects[Position.from_xy(level_x, level_y).tile_data_index]

        assert obj is not None

        return obj

    def _on_left_mouse_button_down(self, event: QMouseEvent):
        """Start tile placement, selection, or dragging from a left click.

        This method is the main world-map gesture entry point. It decides
        whether the click begins painting, flood fill, marquee selection, or a
        drag of tiles or map objects, and stages the mode and selection state
        later consumed by drag and release handlers before any undo command is
        finalized.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.
        """
        x, y = self.to_level_point(event.position().toPoint()).xy

        if not self.world.point_in(x, y):
            return

        if self.mouse_mode == MODE_PUT_TILE:
            tile = self.world.object_at(x, y)

            assert tile is not None

            tile_to_put_name = TILE_NAMES[self._tile_to_put]

            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self.undo_stack.beginMacro(f"Fill in '{tile.name}' with '{tile_to_put_name}'")
                self._fill_tile(tile.type, x, y)
            else:
                self.undo_stack.beginMacro(f"Place '{tile_to_put_name}'")
                self.undo_stack.push(PutTile(self.world, Position.from_xy(x, y), self._tile_to_put))

            self.update()

            return

        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.set_mouse_mode(MODE_SELECTION_SQUARE, event)
            return

        obj = self._visible_object_at(event.position().toPoint())

        # if shirt is pressed, toggle selection, while keeping current selection
        # if shift is not pressed, remove selection and only select obj under cursor

        if not obj.selected and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            self._select_object(None)

            self.select_object_like(obj)
            self._object_was_selected_on_last_click = True

        self.set_mouse_mode(MODE_DRAG, event)

        self.update()

    def _dragging(self, event: QMouseEvent):
        """Advance a world-map drag gesture using the latest cursor position.

        Dragging updates tile or map-object positions temporarily so release
        handlers can later decide whether to commit an undo command.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.
        """
        level_pos = self.to_level_point(event.position().toPoint())

        dx, dy = (level_pos - self.last_mouse_position).xy

        if dx == dy == 0:
            return

        self.dragging_happened = True

        self.last_mouse_position = level_pos

        for selected_obj in self.get_selected_objects():
            selected_obj.move_by(dx, dy)

        if not self.get_selected_objects() and self.selected_object:
            self.selected_object.move_by(dx, dy)

        self.level_ref.data_changed.emit()
        self.update()

    def _on_left_mouse_button_up(self, event: QMouseEvent):
        """Commit tile painting, movement, or selection changes.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.
        """
        if self.mouse_mode == MODE_PUT_TILE:
            self.undo_stack.endMacro()
            return

        obj = self.object_at(event.position().toPoint())

        if self.mouse_mode == MODE_DRAG and self.dragging_happened:
            drag_end_point = self.to_level_point(event.position().toPoint())

            if self.get_selected_objects():
                self._move_selected_tiles(drag_end_point)

            if self.selected_object and not isinstance(self.selected_object, MapTile):
                move_command = MoveMapObject(
                    self.world, self.selected_object, start=self.drag_start_point, end=drag_end_point
                )

                x, y = self.to_level_point(event.position().toPoint()).xy

                if not self.world.point_in(x, y):
                    # Move went outside the world area. easy way to undo the move, without tracking it in the undo stack
                    move_command.redo()
                    move_command.undo()
                else:
                    self.undo_stack.push(move_command)

            self.dragging_happened = False

        elif self.selection_square.active:
            self._stop_selection_square()

        elif obj and not self._object_was_selected_on_last_click:
            # handle selected object on release to allow dragging
            selected_objects = self.get_selected_objects().copy()

            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                if obj.selected:
                    # take selected object under cursor out of current selection
                    selected_objects.remove(obj)
                else:
                    selected_objects.append(obj)

                obj.selected = obj.selected

                self.select_objects(selected_objects, replace_selection=True)
            else:
                # replace selection with only selected object
                self.select_objects([obj], replace_selection=True)

        self.set_mouse_mode(MODE_FREE, event)

    def _move_selected_tiles(self, drag_end_point: Position):
        """Commit a dragged tile selection to the undo stack.

        Multi-tile motion is replayed here as one macro so the moved rectangle
        keeps its relative layout when the command is undone or redone.

        Parameters
        ----------
        drag_end_point : Position
            World-map position where the drag ended.
        """
        dx, dy = (drag_end_point - self.drag_start_point).xy

        if dx == dy == 0:
            return

        sel_objects = self.get_selected_objects().copy()

        self.select_objects([], replace_selection=True)

        if (no_of_sel_objects := len(sel_objects)) > 1:
            self.undo_stack.beginMacro(f"Move {no_of_sel_objects} Tiles")

        old_objects = self.world.objects.copy()

        if dx > 0 or dy > 0:
            sel_objects.reverse()

        for selected_obj in sel_objects:
            if not isinstance(selected_obj, MapTile):
                continue

            end = selected_obj.pos.copy()

            selected_obj.move_by(-dx, -dy)

            start = selected_obj.pos.copy()

            # we don't actually move the map position in the end, just change the type at both positions

            # if we are moving only one tile, then move it back, if more, reset them
            if no_of_sel_objects > 1 or self.world.point_in(*end.xy):
                cmd = MoveTile(self.world, start, old_objects[start.tile_data_index].type, end)

                self.undo_stack.push(cmd)

        if no_of_sel_objects > 1:
            self.undo_stack.endMacro()

    def select_object_like(self, obj: MapObject):
        """Select one non-tile map object.

        Parameters
        ----------
        obj : MapObject
            Map object to select.
        """
        if self.selected_object is not None:
            self.selected_object.selected = False

        if obj is None:
            return

        self.selected_object = obj
        self.selected_object.selected = True

        self.update()

    def select_sprite(self, index: int):
        """Select a sprite by index.

        Parameters
        ----------
        index : int
            Zero-based index of the item to access.
        """
        self.select_object_like(self.world.sprites[index])

    def select_level_pointer(self, index: int):
        """Select a level pointer by index.

        Parameters
        ----------
        index : int
            Zero-based index of the item to access.
        """
        self.select_object_like(self.world.level_pointers[index])

    def select_locks_and_bridges(self, index: int):
        """Select a lock or bridge object by index.

        Parameters
        ----------
        index : int
            Zero-based index of the item to access.
        """
        self.select_object_like(self.world.locks_and_bridges[index])

    def clear_tiles(self):
        """Replace every map tile with a blank tile via undo commands."""
        self.undo_stack.beginMacro("Clear Tiles")

        for map_tile in self.world.get_all_objects():
            self.undo_stack.push(PutTile(self.world, map_tile.pos, WORLD_MAP_BLANK_TILE_ID))

        self.undo_stack.endMacro()

    def clear_sprites(self):
        """Clear all world-map sprites via undo commands."""
        self.undo_stack.beginMacro("Clear Sprites")

        for sprite in self.world.sprites:
            self.undo_stack.push(SetSpriteType(sprite.data, 0))
            self.undo_stack.push(SetSpriteItem(sprite.data, 0))
            self.undo_stack.push(MoveMapObject(self.world, sprite, Position.from_xy(0, FIRST_VALID_ROW)))

        self.undo_stack.endMacro()

    def clear_level_pointers(self):
        """Clear all level pointers via undo commands."""
        self.undo_stack.beginMacro("Clear Level Pointers")

        for level_pointer in self.world.level_pointers:
            self.undo_stack.push(SetLevelAddress(level_pointer.data, 0))
            self.undo_stack.push(SetEnemyAddress(level_pointer.data, 0))
            self.undo_stack.push(SetObjectSet(level_pointer.data, 0))
            self.undo_stack.push(MoveMapObject(self.world, level_pointer, Position.from_xy(0, FIRST_VALID_ROW)))

        self.undo_stack.endMacro()

    def scroll_to_objects(self, objects: list[LevelObject]):
        """Scroll the containing view to the first related objects.

        Parameters
        ----------
        objects : list[foundry.game.gfx.objects.in_level.level_object.LevelObject]
            Objects whose positions should be made visible.
        """
        if not objects:
            return

        min_x = min([obj.x_position for obj in objects]) * self.block_length
        min_y = min([obj.y_position for obj in objects]) * self.block_length

        self.parent().parent().ensureVisible(min_x, min_y)
