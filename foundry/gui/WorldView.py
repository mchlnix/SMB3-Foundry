from bisect import bisect_right
from typing import List, Optional, Tuple, Union
from warnings import warn

from PySide6.QtCore import QPoint, QSize
from PySide6.QtGui import QCursor, QMouseEvent, QPaintEvent, QPainter, QPixmap, QWheelEvent, Qt
from PySide6.QtWidgets import QWidget

from foundry.game.gfx.drawable.Block import Block, get_worldmap_tile
from foundry.game.gfx.objects.EnemyItem import EnemyObject
from foundry.game.gfx.objects.LevelObject import LevelObject, SCREEN_WIDTH
from foundry.game.gfx.objects.sprite import Sprite
from foundry.game.level.Level import Level
from foundry.game.level.LevelRef import LevelRef
from foundry.game.level.WorldMap import WorldMap
from foundry.gui.MainView import (
    HIGHEST_ZOOM_LEVEL,
    LOWEST_ZOOM_LEVEL,
    MODE_DRAG,
    MODE_FREE,
    MODE_PLACE_TILE,
    MainView,
    ctrl_is_pressed,
    undoable,
)
from foundry.gui.SelectionSquare import SelectionSquare
from foundry.gui.WorldDrawer import WorldDrawer
from foundry.gui.settings import SETTINGS
from scribe.gui.world_view_context_menu import WorldContextMenu
from smb3parse.levels import FIRST_VALID_ROW
from smb3parse.levels.WorldMapPosition import WorldMapPosition


class WorldView(MainView):
    context_menu: WorldContextMenu

    def __init__(self, parent: Optional[QWidget], level: LevelRef, context_menu: Optional[WorldContextMenu]):
        super(WorldView, self).__init__(parent, level, context_menu)

        self.drawer = WorldDrawer()

        self.draw_level_pointers = SETTINGS["draw_level_pointers"]
        """Whether to highlight the spaces, which can be used to point to levels."""
        self.draw_sprites = SETTINGS["draw_overworld_sprites"]
        """Whether to draw overworld sprites, like hammer bros and the 'help' speech bubble."""
        self.draw_start = SETTINGS["draw_starting_position"]
        """Whether to highlight the space, that the player starts on, when first coming into the world."""
        self.draw_airship_points = SETTINGS["draw_airship_points"]
        """Whether to show the points and airship can retreat to."""
        self.draw_pipes = SETTINGS["draw_pipes"]
        """Whether to draw positions marked as pipe entrances."""
        self.draw_locks = SETTINGS["draw_locks"]
        """Whether to highlight positions marked as having locks."""

        self.changed = False
        self._tile_to_put: Optional[Block] = None

        self.selection_square = SelectionSquare()

        self.mouse_mode = MODE_FREE

        self.last_mouse_position = 0, 0

        self.drag_start_point = 0, 0
        self.selected_sprite: Optional[Sprite] = None

        self.dragging_happened = True

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

    @property
    def draw_level_pointers(self):
        return self.drawer.draw_level_pointers

    @draw_level_pointers.setter
    def draw_level_pointers(self, value):
        self.drawer.draw_level_pointers = value

    @property
    def draw_sprites(self):
        return self.drawer.draw_sprites

    @draw_sprites.setter
    def draw_sprites(self, value):
        self.drawer.draw_sprites = value

    @property
    def draw_start(self):
        return self.drawer.draw_start

    @draw_start.setter
    def draw_start(self, value):
        self.drawer.draw_start = value

    @property
    def draw_airship_points(self):
        return self.drawer.draw_airship_points

    @draw_airship_points.setter
    def draw_airship_points(self, value):
        self.drawer.draw_airship_points = value

    @property
    def draw_pipes(self):
        return self.drawer.draw_pipes

    @draw_pipes.setter
    def draw_pipes(self, value):
        self.drawer.draw_pipes = value

    @property
    def draw_locks(self):
        return self.drawer.draw_locks

    @draw_locks.setter
    def draw_locks(self, value):
        self.drawer.draw_locks = value

    @property
    def world(self) -> WorldMap:
        return self.level_ref.level

    def on_put_tile(self, tile_id: int):
        self.mouse_mode = MODE_PLACE_TILE
        self._tile_to_put = get_worldmap_tile(tile_id)

        open_hand_px = QPixmap(QSize(Block.SIDE_LENGTH * self.zoom, Block.SIDE_LENGTH * self.zoom))

        painter = QPainter(open_hand_px)
        self._tile_to_put.draw(painter, 0, 0, Block.SIDE_LENGTH * self.zoom)
        painter.end()

        open_hand_cursor = QCursor(open_hand_px)

        self.setCursor(open_hand_cursor)

    def mousePressEvent(self, event: QMouseEvent):
        if self.read_only:
            return super(WorldView, self).mousePressEvent(event)

        pressed_button = event.button()

        if pressed_button == Qt.LeftButton:
            self._on_left_mouse_button_down(event)
        elif pressed_button == Qt.RightButton:
            self._on_right_mouse_button_down(event)
        else:
            return super(WorldView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.read_only:
            return super(WorldView, self).mouseMoveEvent(event)

        if self.mouse_mode == MODE_DRAG:
            self.setCursor(Qt.ClosedHandCursor)
            self._dragging(event)

        elif self.selection_square.active:
            self._set_selection_end(event.pos())

        return super(WorldView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.read_only:
            return super(WorldView, self).mouseReleaseEvent(event)

        released_button = event.button()

        if released_button == Qt.LeftButton:
            self._on_left_mouse_button_up(event)
        elif released_button == Qt.RightButton:
            self._on_right_mouse_button_up(event)
        else:
            return super(WorldView, self).mouseReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        if self.read_only:
            return super(WorldView, self).wheelEvent(event)

        if SETTINGS["object_scroll_enabled"]:
            x, y = event.position().toTuple()

            obj_under_cursor = self.object_at(x, y)

            if obj_under_cursor is None:
                return False

            if isinstance(self.level_ref.level, WorldMap):
                return False

            # scrolling through the level could unintentionally change objects, if the cursor would wander onto them.
            # this is annoying (to me) so only change already selected objects
            if obj_under_cursor not in self.level_ref.selected_objects:
                return False

            self._change_object_on_mouse_wheel(event.position(), event.angleDelta().y())

            return True
        else:
            super(WorldView, self).wheelEvent(event)
            return False

    @undoable
    def _change_object_on_mouse_wheel(self, cursor_position: QPoint, y_delta: int):
        x, y = cursor_position.toTuple()

        obj_under_cursor = self.object_at(x, y)

        if y_delta > 0:
            obj_under_cursor.increment_type()
        else:
            obj_under_cursor.decrement_type()

        obj_under_cursor.selected = True

    def _on_right_mouse_button_down(self, event: QMouseEvent):
        if self.mouse_mode in [MODE_DRAG, MODE_PLACE_TILE]:
            return

        x, y = event.pos().toTuple()
        level_x, level_y = self._to_level_point(x, y)

        self.last_mouse_position = level_x, level_y

        self._select_objects_on_click(event)

    def _on_right_mouse_button_up(self, event):
        if self.mouse_mode == MODE_PLACE_TILE:
            pass
        elif self.context_menu is not None:
            x, y = event.pos().toTuple()

            screen = x // SCREEN_WIDTH + 1

            column, row = self._to_level_point(x, y)

            map_pos = WorldMapPosition(self.world.internal_world_map, screen, column, row)

            menu_pos = self.mapToGlobal(event.pos())

            self.context_menu.setup_menu(map_pos).popup(menu_pos)

        self.mouse_mode = MODE_FREE
        self.setCursor(Qt.ArrowCursor)

    def _on_left_mouse_button_down(self, event: QMouseEvent):
        # 1 if clicking on background: deselect everything, start selection square
        # 2 if clicking on background and ctrl: start selection_square
        # 3 if clicking on selected object: deselect everything and select only this object
        # 4 if clicking on selected object and ctrl: do nothing, deselect this object on release
        # 5 if clicking on unselected object: deselect everything and select only this object
        # 6 if clicking on unselected object and ctrl: select this object
        x, y = event.pos().toTuple()

        sprite = self.world.sprite_at_position(x // self.block_length, y // self.block_length)
        obj = self.object_at(x, y)

        if self.mouse_mode == MODE_PLACE_TILE:
            obj.change_type(self._tile_to_put.index)
            self.update()
        elif sprite is not None:
            self.drag_start_point = sprite.data.x, sprite.data.y
            self.selected_sprite = sprite
            self.mouse_mode = MODE_DRAG
        elif self._select_objects_on_click(event) and obj is not None:
            self.drag_start_point = obj.x_position, obj.y_position
        else:
            self._start_selection_square(event.pos())

    def _dragging(self, event: QMouseEvent):
        self.dragging_happened = True

        x, y = event.pos().toTuple()

        level_x, level_y = self._to_level_point(x, y)

        dx = level_x - self.last_mouse_position[0]
        dy = level_y - self.last_mouse_position[1]

        self.last_mouse_position = level_x, level_y

        if self.selected_sprite is not None:
            screen = level_x // SCREEN_WIDTH
            column = level_x % SCREEN_WIDTH
            row = FIRST_VALID_ROW + level_y

            self.selected_sprite.data.set_pos(screen, row, column)

            self.level_ref.level.changed = True
        else:
            selected_objects = self.get_selected_objects()

            for obj in selected_objects:
                obj.move_by(dx, dy)

                self.world.objects.remove(obj)
                self.world.objects.append(obj)

                self.level_ref.level.changed = True

        self.level_ref.data_changed.emit()
        self.update()

    def _on_left_mouse_button_up(self, event: QMouseEvent):
        x, y = event.pos().toTuple()

        obj = self.object_at(x, y)

        if self.mouse_mode == MODE_PLACE_TILE:
            return
        elif self.mouse_mode == MODE_DRAG and self.dragging_happened:
            if self.selected_sprite is not None:
                drag_end_point = self.selected_sprite.data.x, self.selected_sprite.data.y

                if self.drag_start_point != drag_end_point:
                    self._stop_drag()
                else:
                    self.dragging_happened = False
            if obj is not None:
                drag_end_point = obj.x_position, obj.y_position

                if self.drag_start_point != drag_end_point:
                    self._stop_drag()
                else:
                    self.dragging_happened = False
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

        self.mouse_mode = MODE_FREE
        self._object_was_selected_on_last_click = False
        self.setCursor(Qt.ArrowCursor)

    def _stop_drag(self):
        if self.dragging_happened:
            self.level_ref.save_level_state()

        self.dragging_happened = False

    def _set_zoom(self, zoom):
        if not (LOWEST_ZOOM_LEVEL <= zoom <= HIGHEST_ZOOM_LEVEL):
            return

        self.zoom = zoom
        self.block_length = int(Block.SIDE_LENGTH * self.zoom)

        self.update()

    def zoom_out(self):
        self._set_zoom(self.zoom / 2)

    def zoom_in(self):
        self._set_zoom(self.zoom * 2)

    def _start_selection_square(self, position):
        self.selection_square.start(position)

    def _set_selection_end(self, position):
        if not self.selection_square.is_active():
            return

        self.selection_square.set_current_end(position)

        sel_rect = self.selection_square.get_adjusted_rect(self.block_length, self.block_length)

        touched_objects = [obj for obj in self.level_ref.get_all_objects() if sel_rect.intersects(obj.get_rect())]

        if touched_objects != self.level_ref.selected_objects:
            self._set_selected_objects(touched_objects)

        self.update()

    def _stop_selection_square(self):
        self.selection_square.stop()

        self.update()

    def select_all(self):
        self.select_objects(self.level_ref.get_all_objects())

    def remove_selected_objects(self):
        for obj in self.level_ref.selected_objects:
            self.level_ref.remove_object(obj)

    def scroll_to_objects(self, objects: List[LevelObject]):
        if not objects:
            return

        min_x = min([obj.x_position for obj in objects]) * self.block_length
        min_y = min([obj.y_position for obj in objects]) * self.block_length

        self.parent().parent().ensureVisible(min_x, min_y)

    def level_safe_to_save(self) -> Tuple[bool, str, str]:
        is_safe = True
        reason = ""
        additional_info = ""

        if self.level_ref.too_many_level_objects():
            level = self._cuts_into_other_objects()

            is_safe = False
            reason = "Too many level objects."

            if level:
                additional_info = f"Would overwrite data of '{level}'."
            else:
                additional_info = (
                    "It wouldn't overwrite another level, " "but it might still overwrite other important data."
                )

        elif self.level_ref.too_many_enemies_or_items():
            level = self._cuts_into_other_enemies()

            is_safe = False
            reason = "Too many enemies or items."

            if level:
                additional_info = f"Would probably overwrite enemy/item data of '{level}'."
            else:
                additional_info = (
                    "It wouldn't overwrite enemy/item data of another level, "
                    "but it might still overwrite other important data."
                )

        return is_safe, reason, additional_info

    def _cuts_into_other_enemies(self) -> str:
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
        if self.level_ref is None:
            raise ValueError("Level is None")

        end_of_level_objects = self.level_ref.objects_end

        level_index = (
            bisect_right(
                [level.rom_level_offset - Level.HEADER_LENGTH for level in Level.sorted_offsets], end_of_level_objects
            )
            - 1
        )

        found_level = Level.sorted_offsets[level_index]

        if found_level.rom_level_offset == self.level_ref.object_offset:
            return ""
        else:
            return f"World {found_level.game_world} - {found_level.name}"

    def add_jump(self):
        self.level_ref.add_jump()

    def from_m3l(self, data: bytearray):
        self.level_ref.from_m3l(data)

    def create_object_at(self, x: int, y: int, domain: int = 0, object_index: int = 0):
        level_x, level_y = self._to_level_point(x, y)

        self.level_ref.create_object_at(level_x, level_y, domain, object_index)

        self.update()

    def create_enemy_at(self, x: int, y: int):
        level_x, level_y = self._to_level_point(x, y)

        self.level_ref.create_enemy_at(level_x, level_y)

    def add_object(self, domain: int, obj_index: int, x: int, y: int, length: int, index: int = -1):
        level_x, level_y = self._to_level_point(x, y)

        self.level_ref.add_object(domain, obj_index, level_x, level_y, length, index)

    def add_enemy(self, enemy_index: int, x: int, y: int, index: int):
        level_x, level_y = self._to_level_point(x, y)

        self.level_ref.add_enemy(enemy_index, level_x, level_y, index)

    def replace_object(self, obj: LevelObject, domain: int, obj_index: int, length: int):
        self.remove_object(obj)

        x, y = obj.get_position()

        new_obj = self.level_ref.add_object(domain, obj_index, x, y, length, obj.index_in_level)
        new_obj.selected = obj.selected

    def replace_enemy(self, old_enemy: EnemyObject, enemy_index: int):
        index_in_level = self.level_ref.index_of(old_enemy)

        self.remove_object(old_enemy)

        x, y = old_enemy.get_position()

        new_enemy = self.level_ref.add_enemy(enemy_index, x, y, index_in_level)

        new_enemy.selected = old_enemy.selected

    def remove_object(self, obj):
        self.level_ref.remove_object(obj)

    def remove_jump(self, index: int):
        del self.level_ref.jumps[index]

        self.update()

    def paste_objects_at(
        self,
        paste_data: Tuple[List[Union[LevelObject, EnemyObject]], Tuple[int, int]],
        x: Optional[int] = None,
        y: Optional[int] = None,
    ):
        if x is None or y is None:
            level_x, level_y = self.last_mouse_position
        else:
            level_x, level_y = self._to_level_point(x, y)

        objects, origin = paste_data

        ori_x, ori_y = origin

        pasted_objects = []

        for obj in objects:
            obj_x, obj_y = obj.get_position()

            offset_x, offset_y = obj_x - ori_x, obj_y - ori_y

            try:
                pasted_objects.append(self.level_ref.paste_object_at(level_x + offset_x, level_y + offset_y, obj))
            except ValueError:
                warn("Tried pasting outside of level.", RuntimeWarning)

        self.select_objects(pasted_objects)

    def get_object_names(self):
        return self.level_ref.get_object_names()

    @undoable
    def dropEvent(self, event):
        x, y = self._to_level_point(*event.pos().toTuple())

        level_object = self._object_from_mime_data(event.mimeData())

        if isinstance(level_object, LevelObject):
            self.level_ref.level.add_object(level_object.domain, level_object.obj_index, x, y, None)
        else:
            self.level_ref.level.add_enemy(level_object.obj_index, x, y)

        event.accept()

        self.currently_dragged_object = None

        self.level_ref.data_changed.emit()

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)

        if self.level_ref is None:
            return

        self.drawer.block_length = self.block_length

        self.drawer.draw(painter, self.level_ref.level)

        self.selection_square.draw(painter)

        if self.currently_dragged_object is not None:
            self.currently_dragged_object.draw(painter, self.block_length, self.draw_level_pointers)
