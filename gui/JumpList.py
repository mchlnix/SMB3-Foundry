import wx


class JumpList(wx.ListBox):
    def __init__(self, parent):
        super(JumpList, self).__init__(parent)

    def set_jumps(self, event):
        jumps = event.jumps

        self.SetItems([str(jump) for jump in jumps])
