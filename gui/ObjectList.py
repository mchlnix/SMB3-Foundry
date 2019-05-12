import wx


class ObjectList(wx.ListBox):
    def __init__(self, parent):
        super(ObjectList, self).__init__(parent=parent)

    def remove_selected(self):
        index = self.GetSelection()

        if index > -1:
            self.Delete(index)

    def update(self):
        level_objects = self.Parent.level_view.level.get_all_objects()

        if len(self.GetItems()) != len(level_objects):
            self._full_update()
            return

        index = self.GetSelection()

        if index == -1:
            return

        item = self.GetString(index)

        description = level_objects[index].description

        if item != description:
            self.SetString(index, description)

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
