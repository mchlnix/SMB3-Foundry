from typing import List, Optional, Tuple, Union

from PySide6.QtCore import QMimeData, QSize
from PySide6.QtGui import QDragEnterEvent, QDragMoveEvent, QMouseEvent, Qt
from PySide6.QtWidgets import QApplication, QSizePolicy, QWidget

from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects.EnemyItem import EnemyObject
from foundry.game.gfx.objects.LevelObject import LevelObject
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.ContextMenu import ContextMenu
from foundry.gui.LevelDrawer import LevelDrawer

HIGHEST_ZOOM_LEVEL = 8  # on linux, at least
LOWEST_ZOOM_LEVEL = 1 / 16  # on linux, but makes sense with 16x16 blocks

# mouse modes
MODE_FREE = 0
MODE_DRAG = 1
MODE_RESIZE_HORIZ = 2
MODE_RESIZE_VERT = 4
MODE_RESIZE_DIAG = MODE_RESIZE_HORIZ | MODE_RESIZE_VERT
RESIZE_MODES = [MODE_RESIZE_HORIZ, MODE_RESIZE_VERT, MODE_RESIZE_DIAG]


def ctrl_is_pressed():
    return bool(QApplication.queryKeyboardModifiers() & Qt.ControlModifier)


def undoable(func):
    def wrapped(self, *args):
        func(self, *args)
        self.level_ref.save_level_state()

    return wrapped


class MainView(QWidget):
    def __init__(self, parent: Optional[QWidget], level: LevelRef, context_menu: ContextMenu):
        super(MainView, self).__init__(parent)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)

        self.level_ref: LevelRef = level
        self.level_ref.data_changed.connect(self.update)

        self.context_menu = context_menu

        self.zoom = 1
        self.block_length = Block.SIDE_LENGTH * self.zoom

        self._object_was_selected_on_last_click = False
        """whether an object was selected with the current click; will be cleared, on release of the mouse button"""

        # dragged in from the object toolbar
        self.currently_dragged_object: Optional[Union[LevelObject, EnemyObject]] = None
        self.drawer = LevelDrawer()

    def sizeHint(self) -> QSize:
        if not self.level_ref:
            return super(MainView, self).sizeHint()
        else:
            width, height = self.level_ref.size

            return QSize(width * self.block_length, height * self.block_length)

    def update(self):
        self.resize(self.sizeHint())

        super(MainView, self).update()

    def _select_objects_on_click(self, event: QMouseEvent) -> bool:
        x, y = event.pos().toTuple()
        level_x, level_y = self._to_level_point(x, y)

        self.last_mouse_position = level_x, level_y

        clicked_object = self.object_at(x, y)

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

    def get_selected_objects(self) -> List[Union[LevelObject, EnemyObject]]:
        return self.level_ref.selected_objects

    def _to_level_point(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        level_x = screen_x // self.block_length
        level_y = screen_y // self.block_length

        return level_x, level_y

    def object_at(self, x: int, y: int) -> Optional[Union[LevelObject, EnemyObject]]:
        """
        Returns an enemy or level object at the position. The x and y is relative to the View (for example, when you
        receive a mouse event) and will be converted into level coordinates internally.

        :param int x: X position on the View, where the object is queried at.
        :param int y: Y position on the View, where the object is queried at.

        :return: An enemy/level object, or None, if none is at the position.
        """
        level_x, level_y = self._to_level_point(x, y)

        return self.level_ref.level.object_at(level_x, level_y)

    def make_screenshot(self):
        if self.level_ref is None:
            return

        return self.grab()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasFormat("application/level-object"):
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragMoveEvent):
        x, y = self._to_level_point(*event.pos().toTuple())

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
