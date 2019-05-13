import wx

ID_CTX_REMOVE = 701
ID_CTX_ADD_OBJECT = 702
ID_CTX_ADD_ENEMY = 703
ID_CTX_COPY = 704
ID_CTX_PASTE = 705
ID_CTX_CUT = 706

MODE_BG = 0
MODE_OBJ = 1
MODE_LIST = 2


class ContextMenu(wx.Menu):
    def __init__(self):
        super(ContextMenu, self).__init__()

        self.copied_objects = None
        self.last_opened_at = wx.Point(0, 0)

        self.Append(id=ID_CTX_CUT, item="Cut")
        self.Append(id=ID_CTX_COPY, item="Copy")
        self.Append(id=ID_CTX_PASTE, item="Paste")
        self.AppendSeparator()
        self.Append(id=ID_CTX_REMOVE, item="Remove")
        self.Append(id=ID_CTX_ADD_OBJECT, item="Add Object")
        self.Append(id=ID_CTX_ADD_ENEMY, item="Add Enemy/Item")

    def set_copied_objects(self, objs):
        self.copied_objects = objs

    def get_copied_objects(self):
        return self.copied_objects

    def set_position(self, position):
        self.last_opened_at = position

    def get_position(self):
        return self.last_opened_at.Get()

    def get_all_menu_item_ids(self):
        return [item.GetId() for item in self.GetMenuItems()]

    def as_object_menu(self):
        self._setup_items(MODE_OBJ)

        return self

    def as_background_menu(self):
        self._setup_items(MODE_BG)

        return self

    def as_list_menu(self):
        self._setup_items(MODE_LIST)

        return self

    def _setup_items(self, mode):
        self.FindItemById(ID_CTX_CUT).Enable(not mode == MODE_BG)
        self.FindItemById(ID_CTX_COPY).Enable(not mode == MODE_BG)
        self.FindItemById(ID_CTX_PASTE).Enable(
            not mode == MODE_LIST and self.copied_objects
        )

        self.FindItemById(ID_CTX_REMOVE).Enable(not mode == MODE_BG)
        self.FindItemById(ID_CTX_ADD_OBJECT).Enable(not mode == MODE_LIST)
        self.FindItemById(ID_CTX_ADD_ENEMY).Enable(not mode == MODE_LIST)
