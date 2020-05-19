from bisect import bisect_right
from typing import List, Optional, Tuple, Union

from PySide2.QtCore import QMimeData, QPoint, QRect, QSize
from PySide2.QtGui import (
    QBrush,
    QColor,
    QDragEnterEvent,
    QDragMoveEvent,
    QImage,
    QMouseEvent,
    QPaintEvent,
    QPainter,
    QPen,
    QWheelEvent,
    Qt,
)
from PySide2.QtWidgets import QSizePolicy, QWidget

from foundry import data_dir
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects.EnemyItem import EnemyObject
from foundry.game.gfx.objects.LevelObject import LevelObject, SCREEN_HEIGHT, SCREEN_WIDTH
from foundry.game.gfx.objects.ObjectLike import EXPANDS_BOTH, EXPANDS_HORIZ, EXPANDS_VERT
from foundry.game.level.Level import Level
from foundry.game.level.LevelRef import LevelRef
from foundry.game.level.WorldMap import WorldMap
from foundry.gui.ContextMenu import ContextMenu
from foundry.gui.SelectionSquare import SelectionSquare
from foundry.gui.settings import RESIZE_LEFT_CLICK, RESIZE_RIGHT_CLICK, SETTINGS

HIGHEST_ZOOM_LEVEL = 8  # on linux, at least
LOWEST_ZOOM_LEVEL = 1 / 16  # on linux, but makes sense with 16x16 blocks

# mouse modes

MODE_FREE = 0
MODE_DRAG = 1
MODE_RESIZE_HORIZ = 2
MODE_RESIZE_VERT = 4
MODE_RESIZE_DIAG = MODE_RESIZE_HORIZ | MODE_RESIZE_VERT
RESIZE_MODES = [MODE_RESIZE_HORIZ, MODE_RESIZE_VERT, MODE_RESIZE_DIAG]


def undoable(func):
    def wrapped(self, *args):
        func(self, *args)
        self.level_ref.save_level_state()

    return wrapped


class LevelView(QWidget):
    def __init__(self, parent: Optional[QWidget], level: LevelRef, context_menu: ContextMenu):
        super(LevelView, self).__init__(parent)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)

        self.level_ref: LevelRef = level
        self.level_ref.data_changed.connect(self.update)

        self.context_menu = context_menu

        self.grid_lines = False
        self.jumps = False
        self.transparency = True
        self.show_expansion = False
        self.mario = True

        self.grid_pen = QPen(QColor(0x80, 0x80, 0x80, 0x80), width=1)
        self.screen_pen = QPen(QColor(0xFF, 0x00, 0x00, 0xFF), width=1)

        self.zoom = 1
        self.block_length = Block.SIDE_LENGTH * self.zoom

        self.changed = False

        self.selection_square = SelectionSquare()

        self.mouse_mode = MODE_FREE

        self.last_mouse_position = 0, 0

        self.drag_start_point = 0, 0

        self.dragging_happened = True

        self.resize_mouse_start_x = 0
        self.resize_obj_start_point = 0, 0

        self.resizing_happened = False

        # dragged in from the object toolbar
        self.currently_dragged_object: Optional[Union[LevelObject, EnemyObject]] = None

    def mousePressEvent(self, event: QMouseEvent):
        pressed_button = event.button()

        if pressed_button == Qt.LeftButton:
            self.on_left_mouse_button_down(event)
        elif pressed_button == Qt.RightButton:
            self.on_right_mouse_button_down(event)
        else:
            return super(LevelView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.mouse_mode == MODE_DRAG:
            self.setCursor(Qt.ClosedHandCursor)
            self.dragging(event)

        elif self.mouse_mode in RESIZE_MODES:
            previously_selected_objects = self.level_ref.selected_objects

            self.resizing(event)

            self.level_ref.selected_objects = previously_selected_objects

        elif self.selection_square.active:
            self.set_selection_end(event.pos())

        elif SETTINGS["resize_mode"] == RESIZE_LEFT_CLICK:
            self.set_cursor_for_position(event)

        return super(LevelView, self).mouseMoveEvent(event)

    def set_cursor_for_position(self, event: QMouseEvent):
        level_object = self.object_at(*event.pos().toTuple())

        if level_object is not None:
            is_resizable = not level_object.is_single_block

            edges = self.cursor_on_edge_of_object(level_object, event.pos())

            if is_resizable and edges:
                if edges == Qt.RightEdge and level_object.expands() & EXPANDS_HORIZ:
                    cursor = Qt.SizeHorCursor
                elif edges == Qt.BottomEdge and level_object.expands() & EXPANDS_VERT:
                    cursor = Qt.SizeVerCursor
                elif (level_object.expands() & EXPANDS_BOTH) == EXPANDS_BOTH:
                    cursor = Qt.SizeFDiagCursor
                else:
                    return

                if self.cursor() not in [Qt.SizeHorCursor, Qt.SizeVerCursor, Qt.SizeFDiagCursor]:
                    self.setCursor(cursor)

                return

        if self.mouse_mode not in RESIZE_MODES:
            self.setCursor(Qt.ArrowCursor)

    def cursor_on_edge_of_object(self, level_object: Union[LevelObject, EnemyObject], pos: QPoint, edge_width: int = 4):
        right = (level_object.get_rect().left() + level_object.get_rect().width()) * self.block_length
        bottom = (level_object.get_rect().top() + level_object.get_rect().height()) * self.block_length

        on_right_edge = pos.x() in range(right - edge_width, right)
        on_bottom_edge = pos.y() in range(bottom - edge_width, bottom)

        edges = 0

        if on_right_edge:
            edges |= Qt.RightEdge

        if on_bottom_edge:
            edges |= Qt.BottomEdge

        return edges

    def mouseReleaseEvent(self, event: QMouseEvent):
        released_button = event.button()

        if released_button == Qt.LeftButton:
            self.on_left_mouse_button_up(event)
        elif released_button == Qt.RightButton:
            self.on_right_mouse_button_up(event)
        else:
            super(LevelView, self).mouseReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        x, y = event.pos().toTuple()

        obj_under_cursor = self.object_at(x, y)

        if obj_under_cursor is None:
            return False

        if isinstance(self.level_ref.level, WorldMap):
            return False

        # scrolling through the level could unintentionally change objects, if the cursor would wander onto them.
        # this is annoying (to me) so only change already selected objects
        if obj_under_cursor not in self.level_ref.selected_objects:
            return False

        self.change_object_on_mouse_wheel(event.pos(), event.angleDelta().y())

        return True

    @undoable
    def change_object_on_mouse_wheel(self, cursor_position: QPoint, y_delta: int):
        x, y = cursor_position.toTuple()

        obj_under_cursor = self.object_at(x, y)

        if y_delta > 0:
            obj_under_cursor.increment_type()
        else:
            obj_under_cursor.decrement_type()

        obj_under_cursor.selected = True

    def sizeHint(self) -> QSize:
        if not self.level_ref:
            return super(LevelView, self).sizeHint()
        else:
            width, height = self.level_ref.size

            return QSize(width * self.block_length, height * self.block_length)

    def update(self):
        self.resize(self.sizeHint())

        super(LevelView, self).update()

    def on_right_mouse_button_down(self, event: QMouseEvent):
        if self.mouse_mode == MODE_DRAG:
            return

        x, y = event.pos().toTuple()
        level_x, level_y = self.to_level_point(x, y)

        self.last_mouse_position = level_x, level_y

        if self.select_objects_on_click(event) and SETTINGS["resize_mode"] == RESIZE_RIGHT_CLICK:
            self.try_start_resize(MODE_RESIZE_DIAG, event)

    def try_start_resize(self, resize_mode: int, event: QMouseEvent):
        if resize_mode not in RESIZE_MODES:
            return

        x, y = event.pos().toTuple()
        level_x, level_y = self.to_level_point(x, y)

        self.mouse_mode = resize_mode

        self.resize_mouse_start_x = level_x

        obj = self.object_at(x, y)

        if obj is not None:
            self.resize_obj_start_point = obj.x_position, obj.y_position

    def resizing(self, event: QMouseEvent):
        self.resizing_happened = True

        if isinstance(self.level_ref.level, WorldMap):
            return

        x, y = event.pos().toTuple()

        level_x, level_y = self.to_level_point(x, y)

        dx = dy = 0

        if self.mouse_mode & MODE_RESIZE_HORIZ:
            dx = level_x - self.resize_obj_start_point[0]

        if self.mouse_mode & MODE_RESIZE_VERT:
            dy = level_y - self.resize_obj_start_point[1]

        self.last_mouse_position = level_x, level_y

        selected_objects = self.get_selected_objects()

        for obj in selected_objects:
            obj.resize_by(dx, dy)

            self.level_ref.changed = True

        self.update()

    def on_right_mouse_button_up(self, event):
        if self.resizing_happened:
            x, y = event.pos().toTuple()

            resize_end_x, _ = self.to_level_point(x, y)

            if self.resize_mouse_start_x != resize_end_x:
                self.stop_resize(event)
        else:
            if self.get_selected_objects():
                menu = self.context_menu.as_object_menu()
            else:
                menu = self.context_menu.as_background_menu()

            self.context_menu.set_position(event.pos())

            menu_pos = self.mapToGlobal(event.pos())

            menu.popup(menu_pos)

        self.resizing_happened = False
        self.mouse_mode = MODE_FREE
        self.setCursor(Qt.ArrowCursor)

    def stop_resize(self, _):
        if self.resizing_happened:
            self.level_ref.save_level_state()

        self.resizing_happened = False
        self.mouse_mode = MODE_FREE
        self.setCursor(Qt.ArrowCursor)

    def on_left_mouse_button_down(self, event: QMouseEvent):
        if self.select_objects_on_click(event):
            x, y = event.pos().toTuple()

            obj = self.object_at(x, y)

            if obj is not None:
                edge = self.cursor_on_edge_of_object(obj, event.pos())

                if SETTINGS["resize_mode"] == RESIZE_LEFT_CLICK and edge:

                    self.try_start_resize(self._resize_mode_from_edge(edge), event)
                else:
                    self.drag_start_point = obj.x_position, obj.y_position
        else:
            self.start_selection_square(event.pos())

    @staticmethod
    def _resize_mode_from_edge(edge: int):
        mode = 0

        if edge & Qt.RightEdge:
            mode |= MODE_RESIZE_HORIZ

        if edge & Qt.BottomEdge:
            mode |= MODE_RESIZE_VERT

        return mode

    def dragging(self, event: QMouseEvent):
        self.dragging_happened = True

        x, y = event.pos().toTuple()

        level_x, level_y = self.to_level_point(x, y)

        dx = level_x - self.last_mouse_position[0]
        dy = level_y - self.last_mouse_position[1]

        self.last_mouse_position = level_x, level_y

        selected_objects = self.get_selected_objects()

        for obj in selected_objects:
            obj.move_by(dx, dy)

            self.level_ref.changed = True

        self.update()

    def on_left_mouse_button_up(self, event: QMouseEvent):
        if self.mouse_mode == MODE_DRAG and self.dragging_happened:
            x, y = event.pos().toTuple()

            obj = self.object_at(x, y)

            if obj is not None:
                drag_end_point = obj.x_position, obj.y_position

                if self.drag_start_point != drag_end_point:
                    self.stop_drag()
                else:
                    self.dragging_happened = False
        else:
            self.stop_selection_square()

        self.mouse_mode = MODE_FREE
        self.setCursor(Qt.ArrowCursor)

    def stop_drag(self):
        if self.dragging_happened:
            self.level_ref.save_level_state()

        self.dragging_happened = False

    def select_objects_on_click(self, event: QMouseEvent) -> bool:
        x, y = event.pos().toTuple()
        level_x, level_y = self.to_level_point(x, y)

        self.last_mouse_position = level_x, level_y

        clicked_object = self.object_at(x, y)

        clicked_on_background = clicked_object is None

        if clicked_on_background:
            self.select_object(None)
        else:
            self.mouse_mode = MODE_DRAG

            selected_objects = self.get_selected_objects()

            nothing_selected = not selected_objects

            if nothing_selected or clicked_object not in selected_objects:
                self.select_object(clicked_object)

        return not clicked_on_background

    def set_zoom(self, zoom):
        if not (LOWEST_ZOOM_LEVEL <= zoom <= HIGHEST_ZOOM_LEVEL):
            return

        self.zoom = zoom
        self.block_length = int(Block.SIDE_LENGTH * self.zoom)

        self.update()

    def zoom_out(self):
        self.set_zoom(self.zoom / 2)

    def zoom_in(self):
        self.set_zoom(self.zoom * 2)

    def start_selection_square(self, position):
        self.selection_square.start(position)

    def set_selection_end(self, position):
        if not self.selection_square.is_active():
            return

        self.selection_square.set_current_end(position)

        sel_rect = self.selection_square.get_adjusted_rect(self.block_length, self.block_length)

        touched_objects = [obj for obj in self.level_ref.get_all_objects() if sel_rect.intersects(obj.get_rect())]

        if touched_objects != self.level_ref.selected_objects:
            self._set_selected_objects(touched_objects)

        self.update()

    def stop_selection_square(self):
        self.selection_square.stop()

        self.update()

    def select_all(self):
        self.select_objects(self.level_ref.get_all_objects())

    def select_object(self, obj=None):
        if obj is not None:
            self.select_objects([obj])
        else:
            self.select_objects([])

    def select_objects(self, objects):
        self._set_selected_objects(objects)

        self.update()

    def _set_selected_objects(self, objects):
        if self.level_ref.selected_objects == objects:
            return

        self.level_ref.selected_objects = objects

    def get_selected_objects(self) -> List[Union[LevelObject, EnemyObject]]:
        return self.level_ref.selected_objects

    def remove_selected_objects(self):
        for obj in self.level_ref.selected_objects:
            self.level_ref.remove_object(obj)

    def was_changed(self) -> bool:
        if self.level_ref is None:
            return False
        else:
            return self.level_ref.changed

    def level_safe_to_save(self) -> Tuple[bool, str, str]:
        is_safe = True
        reason = ""
        additional_info = ""

        if self.level_ref.too_many_level_objects():
            level = self.cuts_into_other_objects()

            is_safe = False
            reason = "Too many level objects."

            if level:
                additional_info = f"Would overwrite data of '{level}'."
            else:
                additional_info = (
                    "It wouldn't overwrite another level, " "but it might still overwrite other important data."
                )

        elif self.level_ref.too_many_enemies_or_items():
            level = self.cuts_into_other_enemies()

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

    def cuts_into_other_enemies(self) -> str:
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

    def cuts_into_other_objects(self) -> str:
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

    def object_at(self, x: int, y: int) -> Optional[Union[LevelObject, EnemyObject]]:
        level_x, level_y = self.to_level_point(x, y)

        return self.level_ref.level.object_at(level_x, level_y)

    def to_level_point(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        level_x = screen_x // self.block_length
        level_y = screen_y // self.block_length

        return level_x, level_y

    def index_of(self, obj: Union[LevelObject, EnemyObject]) -> int:
        return self.level_ref.index_of(obj)

    def get_object(self, index: int) -> Union[LevelObject, EnemyObject]:
        return self.level_ref.get_object(index)

    def create_object_at(self, x: int, y: int, domain: int = 0, object_index: int = 0):
        level_x, level_y = self.to_level_point(x, y)

        self.level_ref.create_object_at(level_x, level_y, domain, object_index)

        self.update()

    def create_enemy_at(self, x: int, y: int):
        level_x, level_y = self.to_level_point(x, y)

        self.level_ref.create_enemy_at(level_x, level_y)

    def add_object(self, domain: int, obj_index: int, x: int, y: int, length: int, index: int = -1):
        level_x, level_y = self.to_level_point(x, y)

        self.level_ref.add_object(domain, obj_index, level_x, level_y, length, index)

    def add_enemy(self, enemy_index: int, x: int, y: int, index: int):
        level_x, level_y = self.to_level_point(x, y)

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
            level_x, level_y = self.to_level_point(x, y)

        objects, origin = paste_data

        ori_x, ori_y = origin

        pasted_objects = []

        for obj in objects:
            obj_x, obj_y = obj.get_position()

            offset_x, offset_y = obj_x - ori_x, obj_y - ori_y

            try:
                pasted_objects.append(self.level_ref.paste_object_at(level_x + offset_x, level_y + offset_y, obj))
            except ValueError:
                print("Tried pasting outside of level.")

        self.select_objects(pasted_objects)

    def get_object_names(self):
        return self.level_ref.get_object_names()

    def make_screenshot(self):
        if self.level_ref is None:
            return

        return self.grab()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasFormat("application/level-object"):
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragMoveEvent):
        x, y = self.to_level_point(*event.pos().toTuple())

        level_object = self.get_object_from_mime_data(event.mimeData())

        level_object.set_position(x, y)

        self.currently_dragged_object = level_object

        self.repaint()

    def dragLeaveEvent(self, event):
        self.currently_dragged_object = None

        self.repaint()

    @undoable
    def dropEvent(self, event):
        x, y = self.to_level_point(*event.pos().toTuple())

        level_object = self.get_object_from_mime_data(event.mimeData())

        if isinstance(level_object, LevelObject):
            self.level_ref.level.add_object(level_object.domain, level_object.obj_index, x, y, None)
        else:
            self.level_ref.level.add_enemy(level_object.obj_index, x, y)

        event.accept()

        self.currently_dragged_object = None

        self.level_ref.data_changed.emit()

    def get_object_from_mime_data(self, mime_data: QMimeData) -> Union[LevelObject, EnemyObject]:
        object_type, *object_bytes = mime_data.data("application/level-object")

        if object_type == b"\x00":
            domain = int.from_bytes(object_bytes[0], "big") >> 5
            object_index = int.from_bytes(object_bytes[2], "big")

            return self.level_ref.level.object_factory.from_properties(domain, object_index, 0, 0, None, 999)
        else:
            enemy_id = int.from_bytes(object_bytes[0], "big")

            return self.level_ref.level.enemy_item_factory.from_properties(enemy_id, 0, 0)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)

        if self.level_ref is None:
            return

        self.level_ref.draw(painter, self.block_length, self.transparency, self.show_expansion)

        if self.grid_lines:
            panel_width, panel_height = self.size().toTuple()

            painter.setPen(self.grid_pen)

            for x in range(0, panel_width, self.block_length):
                painter.drawLine(x, 0, x, panel_height)
            for y in range(0, panel_height, self.block_length):
                painter.drawLine(0, y, panel_width, y)

            painter.setPen(self.screen_pen)

            if self.level_ref.is_vertical:
                for y in range(0, panel_height, self.block_length * SCREEN_HEIGHT):
                    painter.drawLine(0, y, panel_width, y)
            else:
                for x in range(0, panel_width, self.block_length * SCREEN_WIDTH):
                    painter.drawLine(x, 0, x, panel_height)

        if self.jumps:
            for jump in self.level_ref.jumps:
                painter.setBrush(QBrush(QColor(0xFF, 0x00, 0x00), Qt.FDiagPattern))

                screen = jump.screen_index

                if self.level_ref.is_vertical:
                    painter.drawRect(
                        0,
                        self.block_length * SCREEN_WIDTH * screen,
                        self.block_length * SCREEN_WIDTH,
                        self.block_length * SCREEN_HEIGHT,
                    )
                else:
                    painter.drawRect(
                        self.block_length * SCREEN_WIDTH * screen,
                        0,
                        self.block_length * SCREEN_WIDTH,
                        self.block_length * 27,
                    )

        self.selection_square.draw(painter)

        if self.currently_dragged_object is not None:
            self.currently_dragged_object.draw(painter, self.block_length, self.transparency)

        if self.mario:
            self.draw_mario(painter)

        return

    def draw_mario(self, painter):
        mario_actions = QImage(str(data_dir / "mario.png"))

        mario_actions.convertTo(QImage.Format_RGBA8888)

        mario_position = QPoint(*self.level_ref.header.mario_position()) * self.block_length

        x_offset = 32 * self.level_ref.level.start_action

        mario_cutout = mario_actions.copy(QRect(x_offset, 0, 32, 32)).scaled(32 * self.zoom, 32 * self.zoom)

        painter.drawImage(mario_position, mario_cutout)
