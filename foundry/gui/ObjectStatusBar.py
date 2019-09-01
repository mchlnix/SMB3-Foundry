from typing import Union

import wx

from game.gfx.objects.EnemyItem import EnemyObject
from game.gfx.objects.LevelObject import LevelObject


class ObjectStatusBar(wx.StatusBar):
    def __init__(self, parent: wx.Window):
        super(ObjectStatusBar, self).__init__(parent=parent)

    def clear(self):
        for i in range(self.GetFieldsCount()):
            self.SetStatusText("", i)

    def fill(self, obj: Union[LevelObject, EnemyObject]):
        info = obj.get_status_info()

        self.SetFieldsCount(len(info))

        for index, (key, value) in enumerate(info):
            self.SetStatusText(f"{key}: {value}", index)
