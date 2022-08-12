from typing import List, Optional

from PySide6.QtCore import QPoint, QSize, QTimer
from PySide6.QtGui import QCursor, QKeySequence, QMouseEvent, QPainter, QPixmap, QShortcut, QUndoStack, Qt
from PySide6.QtWidgets import QToolTip, QWidget

from foundry import get_level_thumbnail
from foundry.game.ObjectSet import OBJECT_SET_NAMES
from foundry.game.gfx.Palette import load_palette_group
from foundry.game.gfx.drawable.Block import get_tile, get_worldmap_tile
from foundry.game.gfx.objects import LevelObject, MapTile
from foundry.game.gfx.objects.world_map.map_object import MapObject
from foundry.game.level.LevelRef import LevelRef
from foundry.game.level.WorldMap import WorldMap
from foundry.gui.MainView import (
    MODE_DRAG,
    MODE_FREE,
    MODE_PUT_TILE,
    MODE_SELECTION_SQUARE,
    MainView,
)
from foundry.gui.WorldDrawer import WorldDrawer
from foundry.gui.settings import Settings
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
from smb3parse.constants import TILE_MUSHROOM_HOUSE_1, TILE_MUSHROOM_HOUSE_2, TILE_NAMES, TILE_SPADE_HOUSE
from smb3parse.data_points import Position
from smb3parse.levels import FIRST_VALID_ROW, WORLD_MAP_BLANK_TILE_ID, WORLD_MAP_HEIGHT


class WorldView(MainView):
    context_menu: WorldContextMenu

    def __init__(
        self,
        parent: Optional[QWidget],
        level: LevelRef,
        settings: Settings,
        context_menu: Optional[WorldContextMenu] = None,
    ):
        self.drawer = WorldDrawer()
        self.redraw_timer: Optional[QTimer] = None

        super(WorldView, self).__init__(parent, level, settings, context_menu)

        level.palette_changed.connect(self.update_palette)
        level.palette_changed.connect(self.update_anim_timer)
        level.level_changed.connect(self.update_anim_timer)

        self.update_anim_timer()

        self._tile_to_put: int = WORLD_MAP_BLANK_TILE_ID

        self.mouse_mode = MODE_FREE

        self.drag_start_point = Position.from_xy(0, 0)
        self.last_mouse_position = Position.from_xy(0, 0)

        self.selected_object: Optional[MapObject] = None

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

        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_A), self, self.select_all)

    def next_anim_step(self):
        self.drawer.anim_frame += 1
        self.drawer.anim_frame %= 4
        get_tile.cache_clear()

        self.repaint()

    def update_anim_timer(self):
        if not self.level_ref:
            return

        if self.redraw_timer is not None:
            self.redraw_timer.stop()
            self.drawer.anim_frame = 0
            get_tile.cache_clear()

        if self.world.data.frame_tick_count and self.settings.value("world view/animated tiles"):
            self.redraw_timer = QTimer(self)
            self.redraw_timer.setInterval(1000 / 60 * self.world.data.frame_tick_count)
            self.redraw_timer.timeout.connect(self.next_anim_step)
            self.redraw_timer.start()

    def sizeHint(self) -> QSize:
        size = super(WorldView, self).sizeHint()

        if self.settings.value("world view/show border"):
            size += QSize(0, 3) * self.block_length

        return size

    @property
    def settings(self):
        return self.drawer.settings

    @settings.setter
    def settings(self, value):
        self.drawer.settings = value

    @property
    def undo_stack(self) -> QUndoStack:
        return self.window().findChild(QUndoStack, "undo_stack")

    @property
    def world(self) -> WorldMap:
        return self.level_ref.level

    def update_palette(self):
        for map_tile in self.world.objects:
            map_tile.block.palette_group = load_palette_group(self.world.object_set, self.world.data.palette_index)
            map_tile.change_type(map_tile.block.index)

        self.update()

    def set_mouse_mode(self, new_mode: int, event: Optional[QMouseEvent]):
        if new_mode == MODE_PUT_TILE:
            tile_pixmap = QPixmap(QSize(self.block_length, self.block_length))

            painter = QPainter(tile_pixmap)
            get_worldmap_tile(self._tile_to_put, self.world.data.palette_index).draw(painter, 0, 0, self.block_length)
            painter.end()

            self.setCursor(QCursor(tile_pixmap))

        elif new_mode == MODE_SELECTION_SQUARE:
            if event is None:
                return

            if self.settings.value("world view/show border"):
                self.selection_square.set_offset(0, 0)
            else:
                self.selection_square.set_offset(0, FIRST_VALID_ROW)

            self.selection_square.start(event.pos())

        elif new_mode == MODE_DRAG:
            if event is None:
                return

            self.drag_start_point = self.to_level_point(event.pos())
            self.last_mouse_position = self.drag_start_point
            self.setCursor(Qt.ClosedHandCursor)

        elif new_mode == MODE_FREE:
            self._tile_to_put = WORLD_MAP_BLANK_TILE_ID

            self._object_was_selected_on_last_click = False
            self.setCursor(Qt.ArrowCursor)

        self.mouse_mode = new_mode

    def on_put_tile(self, tile_id: int):
        self._tile_to_put = tile_id
        self.set_mouse_mode(MODE_PUT_TILE, None)

    def mouseMoveEvent(self, event: QMouseEvent):
        should_display_level = self.mouse_mode == MODE_FREE and self.settings.value("world view/show level previews")

        if not should_display_level or not self._set_level_thumbnail(event):
            # clear tooltip if supposed to show one, but no level thumbnail was available (e.g. no level there)
            if self.cursor().shape() == Qt.PointingHandCursor:
                self.setCursor(Qt.ArrowCursor)

            self.setToolTip("")
            QToolTip.hideText()

        if self.read_only:
            return super(WorldView, self).mouseMoveEvent(event)

        if self.mouse_mode == MODE_PUT_TILE and event.buttons() & Qt.LeftButton:
            level_pos = self.to_level_point(event.pos())

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
        if self.mouse_mode != MODE_FREE:
            return False

        x, y = self.to_level_point(event.pos()).xy

        if not self.world.point_in(x, y):
            return False

        try:
            # TODO make this check based on the object set of the level pointer, not the tile
            if self.world.tile_at(x, y) in [TILE_SPADE_HOUSE, TILE_MUSHROOM_HOUSE_1, TILE_MUSHROOM_HOUSE_2]:
                return False
        except ValueError:
            return False

        if (level_pointer := self.world.level_pointer_at(x, y)) is None:
            return False

        if self.read_only:
            self.setCursor(Qt.PointingHandCursor)

        try:
            level_name = self.world.level_name_at_position(x, y)

            object_set_name = OBJECT_SET_NAMES[level_pointer.data.object_set]

            image_data = get_level_thumbnail(
                level_pointer.data.object_set, level_pointer.data.level_address, level_pointer.data.enemy_address
            )

            self.setToolTip(
                f"<b>{level_name}</b><br/>"
                f"<u>Type:</u> {object_set_name} "
                f"<u>Objects:</u> {hex(level_pointer.data.level_address)} "
                f"<u>Enemies:</u> {hex(level_pointer.data.enemy_address)}<br/>"
                f"<img src='data:image/png;base64,{image_data}'>"
            )

            return True
        except ValueError:
            return False

    def _on_right_mouse_button_up(self, event):
        if not self.mouse_mode == MODE_FREE:
            self.set_mouse_mode(MODE_FREE, event)
        else:
            menu_pos = self.mapToGlobal(event.pos())

            self.context_menu.popup(menu_pos)

    def _fill_tile(self, tile_to_fill_in: int, x, y):
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
        pos = super(WorldView, self).to_level_point(q_point)

        if not self.settings.value("world view/show border"):
            pos += Position.from_xy(0, FIRST_VALID_ROW)

        return pos

    def _on_middle_mouse_button_down(self, event: QMouseEvent):
        x, y = self.to_level_point(event.pos()).xy

        if not self.world.point_in(x, y):
            return

        if self.mouse_mode != MODE_FREE:
            return

        obj = self.world.objects[Position.from_xy(x, y).tile_data_index]

        assert obj is not None

        self.on_put_tile(obj.type)

    def _visible_object_at(self, point: QPoint) -> MapObject:
        level_x, level_y = self.to_level_point(point).xy

        obj = None

        if self.drawer.settings.value("world view/show pipes"):
            obj = self.world.pipe_at(level_x, level_y)

        if not obj and self.drawer.settings.value("world view/show locks"):
            obj = self.world.locks_at(level_x, level_y)

        if not obj and self.drawer.settings.value("world view/show airship paths"):
            obj = self.world.airship_point_at(
                level_x, level_y, self.drawer.settings.value("world view/show airship paths")
            )

        if not obj and self.drawer.settings.value("world view/show start position"):
            if self.world.start_pos.pos == Position.from_xy(level_x, level_y):
                obj = self.world.start_pos

        if not obj and self.drawer.settings.value("world view/show sprites"):
            obj = self.world.sprite_at(level_x, level_y)

        if not obj and self.drawer.settings.value("world view/show level pointers"):
            obj = self.world.level_pointer_at(level_x, level_y)

        if not obj:
            obj = self.world.objects[Position.from_xy(level_x, level_y).tile_data_index]

        assert obj is not None

        return obj

    def _on_left_mouse_button_down(self, event: QMouseEvent):
        x, y = self.to_level_point(event.pos()).xy

        if not self.world.point_in(x, y):
            return

        if self.mouse_mode == MODE_PUT_TILE:
            tile = self.world.object_at(x, y)

            assert tile is not None

            tile_to_put_name = TILE_NAMES[self._tile_to_put]

            if event.modifiers() & Qt.ShiftModifier:
                self.undo_stack.beginMacro(f"Fill in '{tile.name}' with '{tile_to_put_name}'")
                self._fill_tile(tile.type, x, y)
            else:
                self.undo_stack.beginMacro(f"Place '{tile_to_put_name}'")
                self.undo_stack.push(PutTile(self.world, Position.from_xy(x, y), self._tile_to_put))

            self.update()

            return

        if event.modifiers() & Qt.ControlModifier:
            self.set_mouse_mode(MODE_SELECTION_SQUARE, event)
            return

        obj = self._visible_object_at(event.pos())

        # if shirt is pressed, toggle selection, while keeping current selection
        # if shift is not pressed, remove selection and only select obj under cursor

        if not obj.selected and not event.modifiers() & Qt.ShiftModifier:
            self._select_object(None)

            self.select_object_like(obj)
            self._object_was_selected_on_last_click = True

        self.set_mouse_mode(MODE_DRAG, event)

        self.update()

    def _dragging(self, event: QMouseEvent):
        level_pos = self.to_level_point(event.pos())

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
        if self.mouse_mode == MODE_PUT_TILE:
            self.undo_stack.endMacro()
            return

        obj = self.object_at(event.pos())

        if self.mouse_mode == MODE_DRAG and self.dragging_happened:
            drag_end_point = self.to_level_point(event.pos())

            if self.get_selected_objects():
                self._move_selected_tiles(drag_end_point)

            if self.selected_object and not isinstance(self.selected_object, MapTile):
                self.undo_stack.push(
                    MoveMapObject(self.world, self.selected_object, start=self.drag_start_point, end=drag_end_point)
                )

            self.dragging_happened = False

        elif self.selection_square.active:
            self._stop_selection_square()

        elif obj and not self._object_was_selected_on_last_click:
            # handle selected object on release to allow dragging
            selected_objects = self.get_selected_objects().copy()

            if event.modifiers() & Qt.ShiftModifier:
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
        if self.selected_object is not None:
            self.selected_object.selected = False

        if obj is None:
            return

        self.selected_object = obj
        self.selected_object.selected = True

        self.update()

    def select_sprite(self, index: int):
        self.select_object_like(self.world.sprites[index])

    def select_level_pointer(self, index: int):
        self.select_object_like(self.world.level_pointers[index])

    def select_locks_and_bridges(self, index: int):
        self.select_object_like(self.world.locks_and_bridges[index])

    def clear_tiles(self):
        self.undo_stack.beginMacro("Clear Tiles")

        for map_tile in self.world.get_all_objects():
            self.undo_stack.push(PutTile(self.world, map_tile.pos, WORLD_MAP_BLANK_TILE_ID))

        self.undo_stack.endMacro()

    def clear_sprites(self):
        self.undo_stack.beginMacro("Clear Sprites")

        for sprite in self.world.sprites:
            self.undo_stack.push(SetSpriteType(sprite.data, 0))
            self.undo_stack.push(SetSpriteItem(sprite.data, 0))
            self.undo_stack.push(MoveMapObject(self.world, sprite, Position.from_xy(0, FIRST_VALID_ROW)))

        self.undo_stack.endMacro()

    def clear_level_pointers(self):
        self.undo_stack.beginMacro("Clear Level Pointers")

        for level_pointer in self.world.level_pointers:
            self.undo_stack.push(SetLevelAddress(level_pointer.data, 0))
            self.undo_stack.push(SetEnemyAddress(level_pointer.data, 0))
            self.undo_stack.push(SetObjectSet(level_pointer.data, 0))
            self.undo_stack.push(MoveMapObject(self.world, level_pointer, Position.from_xy(0, FIRST_VALID_ROW)))

        self.undo_stack.endMacro()

    def scroll_to_objects(self, objects: List[LevelObject]):
        if not objects:
            return

        min_x = min([obj.x_position for obj in objects]) * self.block_length
        min_y = min([obj.y_position for obj in objects]) * self.block_length

        self.parent().parent().ensureVisible(min_x, min_y)
