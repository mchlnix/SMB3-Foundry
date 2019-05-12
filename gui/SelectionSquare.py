import wx


class SelectionSquare:
    def __init__(self):
        self.start_point = wx.Point(0, 0)
        self.end_point = wx.Point(0, 0)

        self.active = False
        self.should_draw = False

        self.rect = wx.Rect(self.start_point, self.end_point)

        self.pen = wx.Pen(wx.Colour(0x00, 0x00, 0x00, 0x80), width=1)

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

    def draw(self, dc):
        if self.should_draw:
            dc.SetPen(self.pen)
            dc.SetBrush(wx.NullBrush)

            dc.DrawRectangle(self.rect)
