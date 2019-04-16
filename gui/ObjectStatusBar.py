import wx

from Graphics import LevelObject


class ObjectStatusBar(wx.StatusBar):
    def __init__(self, parent):
        super(ObjectStatusBar, self).__init__(parent=parent)

    def clear(self):
        for i in range(self.GetFieldsCount()):
            self.SetStatusText("", i)

    def fill(self, obj: LevelObject):
        self.SetFieldsCount(6)

        self.SetStatusText(f"x: {obj.rendered_base_x}", 0)
        self.SetStatusText(f"y: {obj.rendered_base_y}", 1)

        self.SetStatusText(f"width: {obj.rendered_width}", 2)
        self.SetStatusText(f"height: {obj.rendered_height}", 3)

        self.SetStatusText(f"orientation: {obj.orientation}", 4)
        self.SetStatusText(f"ends: {obj.ending}", 5)
