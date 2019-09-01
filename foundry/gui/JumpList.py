import wx

from gui.Events import JumpAdded, JumpRemoved

ID_ADD_JUMP = 1
ID_DEL_JUMP = 2
ID_EDIT_JUMP = 3


class JumpList(wx.ListBox):
    def __init__(self, parent: wx.Window):
        super(JumpList, self).__init__(parent)

        self.Bind(wx.EVT_RIGHT_UP, self.on_right_click)
        self.Bind(wx.EVT_MENU, self.on_menu)

    def set_jumps(self, event):
        jumps = event.jumps

        self.SetItems([str(jump) for jump in jumps])

    def on_right_click(self, event):
        index = self.HitTest(event.GetPosition())

        menu = wx.Menu()

        if index == wx.NOT_FOUND:
            menu.Append(id=ID_ADD_JUMP, item="Add jump")

        else:
            menu = wx.Menu()

            menu.Append(id=ID_EDIT_JUMP, item="Edit Jump")
            menu.Append(id=ID_DEL_JUMP, item="Remove Jump")

        self.PopupMenu(menu)

    def update(self):
        # todo make an event or something
        jumps = self.GetParent().GetParent().GetParent().level_view.level.jumps

        self.SetItems([str(jump) for jump in jumps])

    def on_menu(self, event):
        menu_item = event.GetId()

        if menu_item == ID_EDIT_JUMP:
            evt = wx.ListEvent(wx.wxEVT_LISTBOX_DCLICK, id=wx.ID_ANY)
            evt.SetInt(self.GetSelection())

            wx.PostEvent(self, evt)
        elif menu_item == ID_ADD_JUMP:
            evt = JumpAdded(id=wx.ID_ANY)

            wx.PostEvent(self, evt)

        elif menu_item == ID_DEL_JUMP:
            evt = JumpRemoved(id=wx.ID_ANY)
            evt.SetInt(self.GetSelection())

            wx.PostEvent(self, evt)
