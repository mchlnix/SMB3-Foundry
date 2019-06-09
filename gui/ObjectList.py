import wx

# todo should have a reference to the level_view or a better way to sync the object lists


class ObjectList(wx.ListBox):
    def __init__(self, parent, context_menu):
        super(ObjectList, self).__init__(parent=parent, style=wx.LB_MULTIPLE)

        self.context_menu = context_menu

        self.Bind(wx.EVT_RIGHT_DOWN, self.on_right_down)
        self.Bind(wx.EVT_RIGHT_UP, self.on_right_up)

    def on_right_down(self, event):
        """
        Normally right clicking deselects everything and selects the item under the cursor,
        but with multi-selection we want the selection to be kept, when the right click happens
        on one of the already selected elements. Didn't seem to be supported like that, so
        we need to make our own.

        :param event: wx.MouseEvent
        :return: None
        """
        item_under_mouse = self.HitTest(event.GetPosition())

        if item_under_mouse == wx.NOT_FOUND:
            event.Skip()
            return

        if item_under_mouse not in self.GetSelections():
            self.SetSelection(wx.NOT_FOUND)

            self.SetSelection(item_under_mouse)

            self.GetParent().on_list_select(None)

    def on_right_up(self, event):
        item_under_mouse = self.HitTest(event.GetPosition())

        if item_under_mouse == wx.NOT_FOUND:
            event.Skip()
            return

        self.PopupMenu(self.context_menu.as_list_menu(), event.GetPosition())

    def remove_selected(self):
        indexes = self.GetSelections()

        for index in reversed(indexes):
            self.Delete(index)

    def update(self):
        level_objects = self.Parent.level_view.level.get_all_objects()

        if len(self.GetItems()) != len(level_objects):
            self._full_update()
            return

        indexes = self.GetSelections()

        if not indexes:
            return

        for index in indexes:
            item = self.GetString(index)

            description = level_objects[index].description

            if item != description:
                self.SetString(index, description)

        self.SetSelection(wx.NOT_FOUND)

        for index in indexes:
            self.SetSelection(index)

    def _full_update(self):
        self._remove_orphaned_items()
        self._add_placeholder_objects()

        for index, obj_name in enumerate(
            self.Parent.level_view.level.get_object_names()
        ):
            self.SetString(index, obj_name)

    def _remove_orphaned_items(self):
        level_objects = self.Parent.level_view.level.get_all_objects()

        while len(self.GetItems()) > len(level_objects):
            last_index = len(self.GetItems()) - 1
            self.Delete(last_index)

    def _add_placeholder_objects(self):
        level_objects = self.Parent.level_view.level.get_all_objects()

        while len(self.GetItems()) < len(level_objects):
            self.Append("__PLACEHOLDER")

    def fill(self):
        self.Clear()

        self.SetItems(self.Parent.level_view.level.get_object_names())
