import wx


class ObjectStatusBar(wx.StatusBar):
    def __init__(self, parent):
        super(ObjectStatusBar, self).__init__(parent=parent)

    def clear(self):
        for i in range(self.GetFieldsCount()):
            self.SetStatusText("", i)

    def fill(self, obj):
        info = obj.get_status_info()

        self.SetFieldsCount(len(info))

        for index, (key, value) in enumerate(info):
            self.SetStatusText(f"{key}: {value}", index)
