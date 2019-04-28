import wx

from Level import Level, WorldMap


# TODO a lot of functionality from MainWindow can be put here


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

        self.selected_object = None

    def select_object(self, obj=None):
        if self.selected_object is not None:
            self.selected_object.selected = False

        if obj is not None:
            obj.selected = True

        self.selected_object = obj

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
            rate_x=self.level.block_width, rate_y=self.level.block_height
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

    def on_size(self, event):
        event.Skip()
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

        return
