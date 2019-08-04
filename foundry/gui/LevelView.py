import wx

from game.gfx.drawable.Block import Block
from game.gfx.objects.LevelObject import SCREEN_WIDTH, SCREEN_HEIGHT
from game.level.Level import Level
from game.level.WorldMap import WorldMap
from gui.Events import ObjectListUpdateEvent, JumpListUpdate
from gui.SelectionSquare import SelectionSquare
from gui.UndoStack import UndoStack

HIGHEST_ZOOM_LEVEL = 8  # on linux, at least
LOWEST_ZOOM_LEVEL = 1 / 16  # on linux, but makes sense with 16x16 blocks

# mouse modes

MODE_FREE = 0
MODE_DRAG = 1
MODE_RESIZE = 2


class LevelView(wx.Panel):
    def __init__(self, parent, context_menu):
        super(LevelView, self).__init__(parent)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        self.level = None
        self.undo_stack = UndoStack(self)

        self.context_menu = context_menu

        self.grid_lines = False
        self.jumps = False
        self.grid_pen = wx.Pen(colour=wx.Colour(0x80, 0x80, 0x80, 0x80), width=1)
        self.screen_pen = wx.Pen(colour=wx.Colour(0xFF, 0x00, 0x00, 0xFF), width=1)

        self.zoom = 1
        self.block_length = Block.SIDE_LENGTH * self.zoom

        self.changed = False

        self.transparency = True

        self.selected_objects = []

        self.selection_square = SelectionSquare()

        self.mouse_mode = MODE_FREE

        self.last_mouse_position = 0, 0

        self.drag_start_point = 0, 0

        self.dragging_happened = True

        self.resize_mouse_start_x = 0
        self.resize_obj_start_point = 0, 0

        self.resizing_happened = False

        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)

        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_mouse_button_down)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_right_mouse_button_down)
        self.Bind(wx.EVT_MOTION, self.on_mouse_motion)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_mouse_button_up)
        self.Bind(wx.EVT_RIGHT_UP, self.on_right_mouse_button_up)

    def on_mouse_motion(self, event):
        if self.mouse_mode == MODE_DRAG:
            self.dragging(event)
        elif self.mouse_mode == MODE_RESIZE:
            self.resizing(event)
        else:
            if self.selection_square.active:
                self.set_selection_end(event.GetPosition())

    def on_right_mouse_button_down(self, event):
        if self.mouse_mode == MODE_DRAG:
            return

        x, y = event.GetPosition().Get()
        level_x, level_y = self.to_level_point(x, y)

        self.last_mouse_position = level_x, level_y

        if self.select_objects_on_click(event):
            self.mouse_mode = MODE_RESIZE

            self.resize_mouse_start_x = level_x

            obj = self.object_at(x, y)

            self.resize_obj_start_point = obj.x_position, obj.y_position

    def resizing(self, event):
        self.resizing_happened = True

        if isinstance(self.level, WorldMap):
            return

        x, y = event.GetPosition().Get()

        level_x, level_y = self.to_level_point(x, y)

        dx = level_x - self.resize_obj_start_point[0]
        dy = level_y - self.resize_obj_start_point[1]

        self.last_mouse_position = level_x, level_y

        selected_objects = self.get_selected_objects()

        for obj in selected_objects:
            obj.resize_by(dx, dy)

            self.level.changed = True

        self.Refresh()

    def on_right_mouse_button_up(self, event):
        if self.resizing_happened:
            x, y = event.GetPosition().Get()

            resize_end_x, _ = self.to_level_point(x, y)

            if self.resize_mouse_start_x != resize_end_x:
                self.stop_resize(event)
        else:
            if self.get_selected_objects():
                menu = self.context_menu.as_object_menu()
            else:
                menu = self.context_menu.as_background_menu()

            adjusted_for_scrolling = self.ScreenToClient(
                self.ClientToScreen(event.GetPosition())
            )

            self.context_menu.set_position(event.GetPosition())

            self.PopupMenu(menu, adjusted_for_scrolling)

        self.resizing_happened = False
        self.mouse_mode = MODE_FREE

    def stop_resize(self, _):
        if self.resizing_happened:
            self.save_level_state()

        self.resizing_happened = False
        self.mouse_mode = MODE_FREE

    def on_left_mouse_button_down(self, event):
        if self.mouse_mode == MODE_RESIZE:
            return

        if self.select_objects_on_click(event):
            x, y = event.GetPosition().Get()

            obj = self.object_at(x, y)

            self.drag_start_point = obj.x_position, obj.y_position
        else:
            self.start_selection_square(event.GetPosition())

    def dragging(self, event):
        self.dragging_happened = True

        x, y = event.GetPosition().Get()

        level_x, level_y = self.to_level_point(x, y)

        dx = level_x - self.last_mouse_position[0]
        dy = level_y - self.last_mouse_position[1]

        self.last_mouse_position = level_x, level_y

        selected_objects = self.get_selected_objects()

        for obj in selected_objects:
            obj.move_by(dx, dy)

            self.level.changed = True

        self.Refresh()

    def on_left_mouse_button_up(self, event):
        if self.mouse_mode == MODE_DRAG and self.dragging_happened:
            x, y = event.GetPosition().Get()

            obj = self.object_at(x, y)

            drag_end_point = obj.x_position, obj.y_position

            if self.drag_start_point != drag_end_point:
                self.stop_drag()
            else:
                self.dragging_happened = False
        else:
            self.stop_selection_square()

        self.mouse_mode = MODE_FREE

    def stop_drag(self):
        if self.dragging_happened:
            self.save_level_state()

        self.dragging_happened = False

    def select_objects_on_click(self, event):
        x, y = event.GetPosition().Get()
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

    def undo(self):
        self.level.from_bytes(*self.undo_stack.undo())

        self.resize()
        self.Refresh()

    def redo(self):
        self.level.from_bytes(*self.undo_stack.redo())

        self.resize()
        self.Refresh()

    def save_level_state(self):
        self.undo_stack.save_state(self.level.to_bytes())

    def set_zoom(self, zoom):
        if not (LOWEST_ZOOM_LEVEL <= zoom <= HIGHEST_ZOOM_LEVEL):
            return

        self.zoom = zoom
        self.block_length = int(Block.SIDE_LENGTH * self.zoom)

        self.resize()

    def zoom_out(self):
        self.set_zoom(self.zoom / 2)

    def zoom_in(self):
        self.set_zoom(self.zoom * 2)

    def resize(self):
        if self.level is not None:
            self.SetMinSize(
                wx.Size(*[side * self.block_length for side in self.level.size])
            )
            self.SetSize(self.GetMinSize())

            self.GetParent().SetupScrolling(
                rate_x=self.block_length, rate_y=self.block_length, scrollToTop=False
            )

    def start_selection_square(self, position):
        self.selection_square.start(position)

    def set_selection_end(self, position):
        if not self.selection_square.is_active():
            return

        self.selection_square.set_current_end(position)

        sel_rect = self.selection_square.get_adjusted_rect(
            self.block_length, self.block_length
        )

        touched_objects = [
            obj
            for obj in self.level.get_all_objects()
            if sel_rect.Intersects(obj.get_rect())
        ]

        self.select_objects(touched_objects)

        self.Refresh()

    def stop_selection_square(self):
        self.selection_square.stop()

        self.Refresh()

    def select_object(self, obj=None):
        if obj is not None:
            self.select_objects([obj])
        else:
            self.select_objects([])

    def select_objects(self, objects):
        for obj in self.selected_objects:
            obj.selected = False

        for obj in objects:
            obj.selected = True

        self.selected_objects = objects

        selected_object_indexes = [self.index_of(obj) for obj in self.selected_objects]

        evt = ObjectListUpdateEvent(
            id=self.GetId(),
            indexes=selected_object_indexes,
            objects=self.get_selected_objects(),
        )

        wx.PostEvent(self, evt)

        self.Refresh()

    def set_selected_objects_by_index(self, indexes):
        objects = [self.level.get_object(index) for index in indexes]

        self.select_objects(objects)

    def get_selected_objects(self):
        return self.selected_objects

    def remove_selected_objects(self):
        for obj in self.selected_objects:
            self.level.remove_object(obj)

        self.selected_objects.clear()

    def was_changed(self):
        if self.level is None:
            return False
        else:
            return self.level.changed

    def load_level(
        self, world, level, object_data_offset, enemy_data_offset, object_set=None
    ):
        if world == 0:
            self.level = WorldMap(level)
        else:
            self.level = Level(
                world, level, object_data_offset, enemy_data_offset, object_set
            )

            self.send_jump_event()

        self.undo_stack.clear(self.level.to_bytes())

        self.resize()

        print(f"Drawing {self.level.name}")

    def send_jump_event(self):
        evt = JumpListUpdate(id=wx.ID_ANY, jumps=self.level.jumps)

        wx.PostEvent(self, evt)

    def add_jump(self, _):
        self.level.add_jump()

        self.send_jump_event()

    def from_m3l(self, data):
        self.level.from_m3l(data)

        self.send_jump_event()

        self.undo_stack.clear(self.level.to_bytes())

        self.resize()

    def object_at(self, x, y):
        level_x, level_y = self.to_level_point(x, y)

        return self.level.object_at(level_x, level_y)

    def to_level_point(self, screen_x, screen_y):
        level_x = screen_x // self.block_length
        level_y = screen_y // self.block_length

        return level_x, level_y

    def to_screen_point(self, level_x, level_y):
        screen_x = level_x * self.block_length
        screen_y = level_y * self.block_length

        return screen_x, screen_y

    def on_size(self, _):
        self.Refresh()

    def index_of(self, obj):
        return self.level.index_of(obj)

    def get_object(self, index):
        return self.level.get_object(index)

    def create_object_at(self, x, y, domain=0, object_index=0):
        level_x, level_y = self.to_level_point(x, y)

        self.level.create_object_at(level_x, level_y, domain, object_index)

        self.Refresh()

    def create_enemy_at(self, x, y):
        level_x, level_y = self.to_level_point(x, y)

        self.level.create_enemy_at(level_x, level_y)

    def add_object(self, domain, obj_index, x, y, length, index):
        level_x, level_y = self.to_level_point(x, y)

        self.level.add_object(domain, obj_index, level_x, level_y, length, index)

    def add_enemy(self, obj_index, x, y, index):
        level_x, level_y = self.to_level_point(x, y)

        self.level.add_enemy(obj_index, level_x, level_y, index)

    def replace_object(self, obj, domain, obj_index, length):
        self.remove_object(obj)

        x, y = obj.get_position()

        self.level.add_object(domain, obj_index, x, y, length, obj.index)

    def replace_enemy(self, enemy, enemy_index):
        index_in_level = self.level.index_of(enemy)

        self.remove_object(enemy)

        x, y = enemy.get_position()

        self.level.add_enemy(enemy_index, x, y, index_in_level)

    def remove_object(self, obj):
        self.level.remove_object(obj)

    def remove_jump(self, event):
        del self.level.jumps[event.GetInt()]
        self.send_jump_event()
        self.Refresh()

    def paste_objects_at(self, x=None, y=None, paste_data=None):
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
                pasted_objects.append(
                    self.level.paste_object_at(
                        level_x + offset_x, level_y + offset_y, obj
                    )
                )
            except ValueError:
                print("Tried pasting outside of level.")

        self.select_objects(pasted_objects)

    def get_object_names(self):
        return self.level.get_object_names()

    def make_screenshot(self, dc: wx.MemoryDC):
        bitmap = wx.EmptyBitmap(*self.GetSize())

        dc.SelectObject(bitmap)

        self.level.draw(dc, self.block_length, True)

        return bitmap

    def on_paint(self, event):
        event.Skip()

        dc = wx.BufferedPaintDC(self)
        dc.Clear()

        if self.level is None:
            return

        self.level.draw(dc, self.block_length, self.transparency)

        if self.grid_lines:
            panel_width, panel_height = self.GetSize().Get()

            dc.SetPen(self.grid_pen)

            for x in range(0, panel_width, self.block_length):
                dc.DrawLine(x, 0, x, panel_height)
            for y in range(0, panel_height, self.block_length):
                dc.DrawLine(0, y, panel_width, y)

            dc.SetPen(self.screen_pen)

            if self.level.is_vertical:
                for y in range(0, panel_height, self.block_length * SCREEN_HEIGHT):
                    dc.DrawLine(0, y, panel_width, y)
            else:
                for x in range(0, panel_width, self.block_length * SCREEN_WIDTH):
                    dc.DrawLine(x, 0, x, panel_height)

        if self.jumps:
            for jump in self.level.jumps:
                dc.SetBrush(
                    wx.Brush(wx.Colour(0xFF, 0x00, 0x00), wx.BRUSHSTYLE_BDIAGONAL_HATCH)
                )

                screen = jump.screen_index

                if self.level.is_vertical:
                    dc.DrawRectangle(
                        0,
                        self.block_length * SCREEN_WIDTH * screen,
                        self.block_length * SCREEN_WIDTH,
                        self.block_length * SCREEN_HEIGHT,
                    )
                else:
                    dc.DrawRectangle(
                        self.block_length * SCREEN_WIDTH * screen,
                        0,
                        self.block_length * SCREEN_WIDTH,
                        self.block_length * 27,
                    )

        self.selection_square.draw(dc)

        return
