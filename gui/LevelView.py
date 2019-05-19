import wx

from Level import Level, WorldMap


# TODO a lot of functionality from MainWindow can be put here
from SelectionSquare import SelectionSquare


class LevelView(wx.Panel):
    def __init__(self, parent):
        super(LevelView, self).__init__(parent)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)

        self.level = None

        self.grid_lines = False
        self.grid_pen = wx.Pen(colour=wx.Colour(0x80, 0x80, 0x80, 0x80), width=1)

        self.changed = False

        self.transparency = True

        self.selected_objects = []

        self.selection_square = SelectionSquare()

    def resize(self):
        if self.level is not None:
            self.SetMinSize(wx.Size(*self.level.size))
            self.SetSize(self.GetMinSize())

            self.GetParent().SetupScrolling(
                rate_x=self.level.block_width,
                rate_y=self.level.block_height,
                scrollToTop=False,
            )

    def start_selection_square(self, position):
        self.selection_square.start(position)

    def set_selection_end(self, position):
        if not self.selection_square.is_active():
            return

        self.selection_square.set_current_end(position)

        sel_rect = self.selection_square.get_adjusted_rect(
            self.level.block_width, self.level.block_height
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

        self.GetParent().SetupScrolling(
            rate_x=self.level.block_width,
            rate_y=self.level.block_height,
            scrollToTop=False,
        )

        self.SetMinSize(wx.Size(*self.level.size))
        self.SetSize(self.GetMinSize())

        print(f"Drawing {self.level.name}")

    def unload_level(self):
        self.level = None

        self.Refresh()

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

        self.level.draw(dc, transparency=self.transparency)

        if self.grid_lines:
            dc.SetPen(self.grid_pen)

            pixel_width = self.level.width * self.level.block_width
            pixel_height = self.level.height * self.level.block_height

            for x in range(0, self.level.width):
                dc.DrawLine(
                    x * self.level.block_width,
                    0,
                    x * self.level.block_width,
                    pixel_height,
                )
            for y in range(0, self.level.height):
                dc.DrawLine(
                    0,
                    y * self.level.block_height,
                    pixel_width,
                    y * self.level.block_height,
                )

        self.selection_square.draw(dc)

        return
