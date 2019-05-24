import wx

from Level import Level, WorldMap
from SelectionSquare import SelectionSquare
from Sprite import Block
from UndoStack import UndoStack

HIGHEST_ZOOM_LEVEL = 8  # on linux, at least
LOWEST_ZOOM_LEVEL = 1 / 16  # on linux, but makes sense with 16x16 blocks


# TODO a lot of functionality from MainWindow can be put here
class LevelView(wx.Panel):
    def __init__(self, parent):
        super(LevelView, self).__init__(parent)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)

        self.level = None
        self.undo_stack = UndoStack(self)

        self.grid_lines = False
        self.grid_pen = wx.Pen(colour=wx.Colour(0x80, 0x80, 0x80, 0x80), width=1)

        self.zoom = 1
        self.block_length = Block.SIDE_LENGTH * self.zoom

        self.changed = False

        self.transparency = True

        self.selected_objects = []

        self.selection_square = SelectionSquare()

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
        self.block_length = Block.SIDE_LENGTH * self.zoom

        self.resize()

    def zoom_out(self):
        self.set_zoom(self.zoom / 2)

    def zoom_in(self):
        self.set_zoom(self.zoom * 2)

    def resize(self):
        if self.level is not None:
            self.SetMinSize(
                wx.Size(*[side * self.block_length for side in self.level.size.Get()])
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
            self.select_objects(None)

    def select_objects(self, objects):
        for obj in self.selected_objects:
            obj.selected = False

        self.selected_objects.clear()

        if objects is None:
            return

        for obj in objects:
            obj.selected = True

        self.selected_objects = objects

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

    def load_level(self, world, level, object_set=None):
        if world == 0:
            self.level = WorldMap(level)
        else:
            self.level = Level(world, level, object_set)

        self.undo_stack.clear(self.level.to_bytes())

        self.resize()

        print(f"Drawing {self.level.name}")

    def from_m3l(self, data):
        self.load_level(1, 1, 1)

        self.level.from_m3l(data)

        self.undo_stack.clear(self.level.to_bytes())

        self.resize()

    def object_at(self, x, y):
        return self.level.object_at(x, y)

    def to_level_point(self, x, y):
        return self.level.to_level_point(x, y)

    def on_size(self, _):
        self.Refresh()

    def on_paint(self, event):
        event.Skip()

        dc = wx.BufferedPaintDC(self)
        dc.Clear()

        if self.level is None:
            return

        self.level.draw(dc, self.block_length, self.transparency)

        if self.grid_lines:
            dc.SetPen(self.grid_pen)

            panel_width, panel_height = self.GetSize().Get()

            for x in range(0, panel_width, self.block_length):
                dc.DrawLine(x, 0, x, panel_height)
            for y in range(0, panel_height, self.block_length):
                dc.DrawLine(0, y, panel_width, y)

        self.selection_square.draw(dc)

        return
