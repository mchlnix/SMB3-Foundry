import wx

ENDING_STR = {
    0: "Uniform",
    1: "Top or Left",
    2: "Bottom or Right",
    3: "Top & Bottom/Left & Right"
}

ORIENTATION_TO_STR = {
    0: "Horizontal",
    1: "Vertical",
    2: "Diagonal ↙",
    3: "Desert Pipe Box",
    4: "Diagonal ↘",
    5: "Diagonal ↗",
    6: "Horizontal to the Ground",
    7: "Horizontal Alternative",
    8: "Diagonal Weird",  # up left?
    9: "Single Block",
    10: "Centered",
    11: "Pyramid to Ground",
    12: "Pyramid Alternative",
    13: "To the Sky",
    14: "Ending"
}


class ObjectStatusBar(wx.StatusBar):
    def __init__(self, parent):
        super(ObjectStatusBar, self).__init__(parent=parent)

    def clear(self):
        for i in range(self.GetFieldsCount()):
            self.SetStatusText("", i)

    def fill(self, obj):
        self.SetFieldsCount(6)

        self.SetStatusText(f"x: {obj.rendered_base_x}", 0)
        self.SetStatusText(f"y: {obj.rendered_base_y}", 1)

        self.SetStatusText(f"Width: {obj.rendered_width}", 2)
        self.SetStatusText(f"Height: {obj.rendered_height}", 3)

        self.SetStatusText(f"Orientation: {ORIENTATION_TO_STR[obj.orientation]}", 4)
        self.SetStatusText(f"Ends: {ENDING_STR[obj.ending]}", 5)
