from typing import List, Optional, Tuple, Union, overload
from warnings import warn

from PySide6.QtCore import QMimeData, QPoint, QSize
from PySide6.QtGui import QContextMenuEvent, QDragEnterEvent, QDragMoveEvent, QMouseEvent, QPaintEvent, QPainter, Qt
from PySide6.QtWidgets import QApplication, QSizePolicy, QWidget

from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects.EnemyItem import EnemyObject
from foundry.game.gfx.objects.LevelObject import LevelObject
from foundry.game.gfx.objects.ObjectLike import ObjectLike
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.ContextMenu import LevelContextMenu
from foundry.gui.LevelDrawer import LevelDrawer
from foundry.gui.SelectionSquare import SelectionSquare
from foundry.gui.WorldDrawer import WorldDrawer

HIGHEST_ZOOM_LEVEL = 8  # on linux, at least
LOWEST_ZOOM_LEVEL = 1 / 16  # on linux, but makes sense with 16x16 blocks

# mouse modes
MODE_FREE = 0
MODE_DRAG = 1
MODE_RESIZE_HORIZ = 2
MODE_RESIZE_VERT = 4
MODE_PLACE_TILE = 8
MODE_SELECTION_SQUARE = 16
MODE_RESIZE_DIAG = MODE_RESIZE_HORIZ | MODE_RESIZE_VERT
RESIZE_MODES = [MODE_RESIZE_HORIZ, MODE_RESIZE_VERT, MODE_RESIZE_DIAG]


def ctrl_is_pressed():
    return bool(QApplication.queryKeyboardModifiers() & Qt.ControlModifier)


def shift_is_pressed():
    return bool(QApplication.queryKeyboardModifiers() & Qt.ShiftModifier)


def undoable(func):
    def wrapped(self, *args):
        func(self, *args)
        self.level_ref.save_level_state()

    return wrapped


class MainView(QWidget):
    def __init__(self, parent: Optional[QWidget], level: LevelRef, context_menu: Optional[LevelContextMenu]):
        super(MainView, self).__init__(parent)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)

        self.level_ref: LevelRef = level
        self.level_ref.data_changed.connect(self.update)
        self.level_ref.needs_redraw.connect(self.update)

        self.context_menu = context_menu

        self.zoom = 1
        self.block_length = Block.SIDE_LENGTH * self.zoom
        self.selection_square = SelectionSquare()

        self.read_only = False

        self._object_was_selected_on_last_click = False
        """whether an object was selected with the current click; will be cleared, on release of the mouse button"""

        # dragged in from the object toolbar
        self.currently_dragged_object: Optional[Union[LevelObject, EnemyObject]] = None

        self.drawer: Union[LevelDrawer, WorldDrawer] = LevelDrawer()
        self.transparency = False

    @property
    def transparency(self):
        return self.drawer.transparency

    @transparency.setter
    def transparency(self, value):
        self.drawer.transparency = value

    def sizeHint(self) -> QSize:
        if not self.level_ref:
            return super(MainView, self).sizeHint()
        else:
            width, height = self.level_ref.size

            return QSize(width * self.block_length, height * self.block_length)

    def update(self):
        self.resize(self.sizeHint())

        super(MainView, self).update()

    def get_painter(self):
        return QPainter(self)

    def _select_objects_on_click(self, event: QMouseEvent) -> bool:
        level_x, level_y = self._to_level_point(event.pos())

        self.last_mouse_position = level_x, level_y

        clicked_object = self.object_at(event.pos())

        clicked_on_background = clicked_object is None

        if clicked_on_background:
            self._select_object(None)
        else:
            self.mouse_mode = MODE_DRAG

            selected_objects = self.get_selected_objects()

            nothing_selected = not selected_objects

            # selected objects are handled on click release
            if nothing_selected or clicked_object not in selected_objects:
                self._select_object(clicked_object)
                self._object_was_selected_on_last_click = True

        return not clicked_on_background

    def mousePressEvent(self, event: QMouseEvent):
        if self.read_only:
            return super(MainView, self).mousePressEvent(event)

        pressed_button = event.button()

        if pressed_button == Qt.LeftButton:
            self._on_left_mouse_button_down(event)
        elif pressed_button == Qt.RightButton:
            self._on_right_mouse_button_down(event)
        else:
            return super(MainView, self).mousePressEvent(event)

    def _on_left_mouse_button_down(self, event: QMouseEvent):
        pass

    def _on_right_mouse_button_down(self, event: QMouseEvent):
        pass

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.read_only:
            return super(MainView, self).mouseReleaseEvent(event)

        released_button = event.button()

        if released_button == Qt.LeftButton:
            self._on_left_mouse_button_up(event)
        elif released_button == Qt.RightButton:
            self._on_right_mouse_button_up(event)
        else:
            return super(MainView, self).mouseReleaseEvent(event)

    def _on_left_mouse_button_up(self, event: QMouseEvent):
        pass

    def _on_right_mouse_button_up(self, event: QMouseEvent):
        pass

    def select_objects(self, objects, replace_selection=False):
        """
        Selects the given objects. Depending on if Ctrl is pressed, the current selection is reserved.

        :param objects: Level objects and enemies/items to select.
        :param replace_selection: Whether to ignore the current selected objects and only select the given objects.
        """
        self._set_selected_objects(objects, replace_selection)

        self.update()

    def _select_object(self, obj=None):
        if obj is not None:
            self.select_objects([obj])
        else:
            self.select_objects([])

    def _set_selected_objects(self, objects, replace_selection=False):
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

    def get_selected_objects(self) -> List[ObjectLike]:
        return self.level_ref.selected_objects

    def select_all(self):
        self.select_objects(self.level_ref.get_all_objects())

    @overload
    def _to_level_point(self, q_point: QPoint) -> Tuple[int, int]:
        ...

    @overload
    def _to_level_point(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        ...

    def _to_level_point(self, *args):
        if len(args) == 2:
            screen_x, screen_y = args
        else:
            assert isinstance(args[0], QPoint), f"{args} needs to be a QPoint or two integers"
            screen_x, screen_y = args[0].toTuple()

        level_x = screen_x // self.block_length
        level_y = screen_y // self.block_length

        return level_x, level_y

    @overload
    def object_at(self, q_point: QPoint) -> Optional[ObjectLike]:
        ...

    @overload
    def object_at(self, x: int, y: int) -> Optional[ObjectLike]:
        ...

    def object_at(self, *args):
        """
        Returns an enemy or level object at the position. The x and y is relative to the View (for example, when you
        receive a mouse event) and will be converted into level coordinates internally.

        :param int x: X position on the View, where the object is queried at.
        :param int y: Y position on the View, where the object is queried at.

        :return: An enemy/level object, or None, if none is at the position.
        """
        level_x, level_y = self._to_level_point(*args)

        return self.level_ref.level.object_at(level_x, level_y)

    def make_screenshot(self):
        if self.level_ref is None:
            return

        return self.grab()

    def contextMenuEvent(self, event: QContextMenuEvent):
        if self.read_only:
            return False
        else:
            return super(MainView, self).contextMenuEvent(event)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasFormat("application/level-object"):
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragMoveEvent):
        x, y = self._to_level_point(event.pos())

        level_object = self._object_from_mime_data(event.mimeData())

        level_object.set_position(x, y)

        self.currently_dragged_object = level_object

        self.repaint()

    def dragLeaveEvent(self, event):
        self.currently_dragged_object = None

        self.repaint()

    def _object_from_mime_data(self, mime_data: QMimeData) -> Union[LevelObject, EnemyObject]:
        object_type, *object_bytes = mime_data.data("application/level-object")

        if object_type == b"\x00":
            domain = int.from_bytes(object_bytes[0], "big") >> 5
            object_index = int.from_bytes(object_bytes[2], "big")

            return self.level_ref.level.object_factory.from_properties(domain, object_index, 0, 0, None, 999)
        else:
            enemy_id = int.from_bytes(object_bytes[0], "big")

            return self.level_ref.level.enemy_item_factory.from_properties(enemy_id, 0, 0)

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

    def _set_selection_end(self, position, always_replace_selection=False):
        if not self.selection_square.is_active():
            return

        self.selection_square.set_current_end(position)

        sel_rect = self.selection_square.get_adjusted_rect(self.block_length, self.block_length)

        touched_objects = [obj for obj in self.level_ref.get_all_objects() if sel_rect.intersects(obj.get_rect())]

        if touched_objects != self.level_ref.selected_objects:
            self._set_selected_objects(touched_objects, replace_selection=False)

        self.update()

    def _stop_selection_square(self):
        self.selection_square.stop()

        self.update()

    def paintEvent(self, event: QPaintEvent):
        painter = self.get_painter()

        if self.level_ref is None:
            return

        self.drawer.block_length = self.block_length

        self.drawer.draw(painter, self.level_ref.level)

        self.selection_square.draw(painter)

        if self.currently_dragged_object is not None:
            self.currently_dragged_object.draw(painter, self.block_length, self.transparency)
