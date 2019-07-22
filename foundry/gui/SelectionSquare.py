import wx

STROKE_COLOR = wx.Colour(0x00, 0x00, 0x00, 0x80)


class SelectionSquare:
    def __init__(self):
        self.start_point = wx.Point(0, 0)
        self.end_point = wx.Point(0, 0)

        self.active = False
        self.should_draw = False

        self.rect = wx.Rect(self.start_point, self.end_point)

        self.pen = wx.Pen(STROKE_COLOR, width=1)
        self.brush = wx.TRANSPARENT_BRUSH

    def is_active(self):
        return self.active

    def start(self, point):
        self.active = True

        self.start_point = point

    def set_current_end(self, point):
        if not self.active:
            return

        self.should_draw = True

        self.end_point = point

        self.rect = wx.Rect(self.start_point, self.end_point)

    def stop(self):
        self.active = False
        self.should_draw = False

    def get_rect(self):
        return self.rect

    def get_adjusted_rect(self, horizontal_factor, vertical_factor):
        x, y, width, height = self.rect.Get()

        x //= horizontal_factor
        width //= horizontal_factor

        y //= vertical_factor
        height //= vertical_factor

        return wx.Rect(x, y, width + 1, height + 1)

    def draw(self, dc):
        if self.should_draw:
            dc.SetPen(self.pen)
            dc.SetBrush(self.brush)

            dc.DrawRectangle(self.rect)
