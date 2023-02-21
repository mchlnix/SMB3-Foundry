from typing import Sequence
from warnings import warn

from PySide6.QtCore import QMimeData, QPoint, QSize
from PySide6.QtGui import QContextMenuEvent, QDragEnterEvent, QDragMoveEvent, QMouseEvent, QPaintEvent, QPainter, Qt
from PySide6.QtWidgets import QSizePolicy, QWidget

from foundry import ctrl_is_pressed
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from foundry.game.gfx.objects.object_like import ObjectLike
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.ContextMenu import ContextMenu
from foundry.gui.LevelDrawer import LevelDrawer
from foundry.gui.SelectionSquare import SelectionSquare
from foundry.gui.WorldDrawer import WorldDrawer
from foundry.gui.settings import Settings
from smb3parse.data_points import Position

HIGHEST_ZOOM_LEVEL = 8  # on linux, at least
LOWEST_ZOOM_LEVEL = 1 / 16  # on linux, but makes sense with 16x16 blocks

# mouse modes
MODE_FREE = 0
MODE_DRAG = 1
MODE_RESIZE_HORIZ = 2
MODE_RESIZE_VERT = 4
MODE_PUT_TILE = 8
MODE_SELECTION_SQUARE = 16
MODE_RESIZE_DIAG = MODE_RESIZE_HORIZ | MODE_RESIZE_VERT
RESIZE_MODES = [MODE_RESIZE_HORIZ, MODE_RESIZE_VERT, MODE_RESIZE_DIAG]


class MainView(QWidget):
    drawer: LevelDrawer | WorldDrawer

    def __init__(self, parent: QWidget | None, level: LevelRef, settings: Settings, context_menu: ContextMenu | None):
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

        self.zoom = 1
        self.block_length = Block.SIDE_LENGTH * self.zoom
        self.selection_square = SelectionSquare()

        self.read_only = False

        self._object_was_selected_on_last_click = False
        """whether an object was selected with the current click; will be cleared, on release of the mouse button"""

        # dragged in from the object toolbar
        self.currently_dragged_object: InLevelObject | None = None

    @property
    def settings(self):
        return self.drawer.settings

    @settings.setter
    def settings(self, value):
        self.drawer.settings = value

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
        if self.read_only:
            return super(MainView, self).mousePressEvent(event)

        pressed_button = event.button()

        if pressed_button == Qt.MouseButton.LeftButton:
            self._on_left_mouse_button_down(event)
        elif pressed_button == Qt.MouseButton.MiddleButton:
            self._on_middle_mouse_button_down(event)
        elif pressed_button == Qt.MouseButton.RightButton:
            self._on_right_mouse_button_down(event)
        else:
            return super(MainView, self).mousePressEvent(event)

    def _on_left_mouse_button_down(self, event: QMouseEvent):
        pass

    def _on_middle_mouse_button_down(self, event: QMouseEvent):
        pass

    def _on_right_mouse_button_down(self, event: QMouseEvent):
        pass

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.read_only:
            return super(MainView, self).mouseReleaseEvent(event)

        released_button = event.button()

        if released_button == Qt.MouseButton.LeftButton:
            self._on_left_mouse_button_up(event)
        elif released_button == Qt.MouseButton.RightButton:
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

    def get_selected_objects(self):
        return self.level_ref.selected_objects

    def select_all(self):
        self.select_objects(self.level_ref.get_all_objects())

    def to_level_point(self, q_point: QPoint) -> Position:
        screen_x = q_point.x()
        screen_y = q_point.y()

        level_x = screen_x // self.block_length
        level_y = screen_y // self.block_length

        return Position.from_xy(level_x, level_y)

    def object_at(self, q_point: QPoint) -> ObjectLike | None:
        """
        Returns an enemy or level object at the position. The x and y is relative to the View (for example, when you
        receive a mouse event) and will be converted into level coordinates internally.

        :return: An enemy/level object, or None, if none is at the position.
        """
        return self.level_ref.level.object_at(*self.to_level_point(q_point).xy)

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
        level_object = self._object_from_mime_data(event.mimeData())

        level_object.set_position(*self.to_level_point(event.position().toPoint()).xy)

        self.currently_dragged_object = level_object

        self.repaint()

    def dragLeaveEvent(self, event):
        self.currently_dragged_object = None

        self.repaint()

    def _object_from_mime_data(self, mime_data: QMimeData) -> InLevelObject:
        object_type, *object_bytes = mime_data.data("application/level-object").data()

        if object_type == 0:
            domain = object_bytes[0] >> 5
            object_index = object_bytes[2]

            return self.level_ref.level.object_factory.from_properties(domain, object_index, 0, 0, None, 999)
        else:
            enemy_id = object_bytes[0]

            return self.level_ref.level.enemy_item_factory.from_properties(enemy_id, 0, 0)

    def paste_objects_at(self, paste_data: tuple[Sequence[ObjectLike], Position], q_point: QPoint | None):
        if q_point is None:
            # when keyboard shortcut was used
            pos = self.last_mouse_position
        else:
            pos = self.to_level_point(q_point)

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

    def _start_selection_square(self, point: QPoint):
        self.selection_square.start(point)

    def _set_selection_end(self, event: QMouseEvent):
        if not self.selection_square.is_active():
            return

        self.selection_square.set_current_end(event.position().toPoint())

        sel_rect = self.selection_square.get_adjusted_rect(self.block_length, self.block_length)

        touched_objects = [obj for obj in self.level_ref.get_all_objects() if sel_rect.intersects(obj.get_rect())]

        if touched_objects != self.level_ref.selected_objects:
            self._set_selected_objects(touched_objects, not event.modifiers() & Qt.KeyboardModifier.ShiftModifier)

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
            self.currently_dragged_object.draw(
                painter, self.block_length, self.settings.value("level view/block_transparency")
            )
