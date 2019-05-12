import wx

ID_CTX_REMOVE = 701
ID_CTX_ADD_OBJECT = 702
ID_CTX_ADD_ENEMY = 703
ID_CTX_COPY = 704
ID_CTX_PASTE = 705
ID_CTX_CUT = 706


class ContextMenu(wx.Menu):
    def __init__(self):
        super(ContextMenu, self).__init__()

        self.copied_object = None
        self.last_opened_at = wx.Point(0, 0)

        self.Append(id=ID_CTX_CUT, item="Cut")
        self.Append(id=ID_CTX_COPY, item="Copy")
        self.Append(id=ID_CTX_PASTE, item="Paste")
        self.AppendSeparator()
        self.Append(id=ID_CTX_REMOVE, item="Remove")
        self.Append(id=ID_CTX_ADD_OBJECT, item="Add Object")
        self.Append(id=ID_CTX_ADD_ENEMY, item="Add Enemy/Item")

    def set_copied_object(self, obj):
        if obj is not None:
            self.copied_object = obj
        else:
            print("Selected object was None.")

    def get_copied_object(self):
        return self.copied_object

    def set_position(self, position):
        self.last_opened_at = position

    def get_position(self):
        return self.last_opened_at.x, self.last_opened_at.y

    def get_all_menu_item_ids(self):
        return [item.GetId() for item in self.GetMenuItems()]

    def as_object_menu(self):
        self._setup_items(True)

        return self

    def as_background_menu(self):
        self._setup_items(False)

        return self

    def _setup_items(self, as_object_menu):
        self.FindItemById(ID_CTX_PASTE).Enable(bool(self.copied_object))

        self.FindItemById(ID_CTX_COPY).Enable(as_object_menu)
        self.FindItemById(ID_CTX_CUT).Enable(as_object_menu)
        self.FindItemById(ID_CTX_REMOVE).Enable(as_object_menu)
