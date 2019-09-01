import wx

from gui.Events import (
    EVT_UNDO_CLEARED,
    EVT_UNDO_COMPLETE,
    EVT_REDO_COMPLETE,
    EVT_UNDO_SAVED,
    UndoEvent,
    RedoEvent,
)
from gui.LevelView import LevelView

ID_SPIN_DOMAIN = 1000
ID_SPIN_TYPE = 1001
ID_SPIN_LENGTH = 1002

ID_TOOL_ZOOM_OUT = 1101
ID_TOOL_ZOOM_IN = 1102

ID_TOOL_UNDO = 1103
ID_TOOL_REDO = 1104

MAX_DOMAIN = 0x07
MAX_TYPE = 0xFF
MAX_LENGTH = 0xFF


class SpinnerPanel(wx.Panel):
    def __init__(self, parent: wx.Window, level_view_ref: LevelView):
        super(SpinnerPanel, self).__init__(parent)

        self.level_view_ref = level_view_ref

        self.toolbar = wx.ToolBar(self)
        self.toolbar.AddTool(
            ID_TOOL_UNDO,
            "Undo",
            wx.ArtProvider.GetBitmap(id=wx.ART_UNDO, client=wx.ART_TOOLBAR),
        ).Enable(False)
        self.toolbar.AddTool(
            ID_TOOL_REDO,
            "Redo",
            wx.ArtProvider.GetBitmap(id=wx.ART_REDO, client=wx.ART_TOOLBAR),
        ).Enable(False)

        self.toolbar.AddStretchableSpace()

        self.toolbar.AddTool(
            ID_TOOL_ZOOM_OUT,
            "Zoom out",
            wx.ArtProvider.GetBitmap(id=wx.ART_MINUS, client=wx.ART_TOOLBAR),
        )
        self.toolbar.AddTool(
            ID_TOOL_ZOOM_IN,
            "Zoom in",
            wx.ArtProvider.GetBitmap(id=wx.ART_PLUS, client=wx.ART_TOOLBAR),
        )

        self.toolbar.Realize()

        self.panel_sizer = wx.BoxSizer(wx.VERTICAL)

        self.spin_domain = wx.SpinCtrl(self, ID_SPIN_DOMAIN, max=MAX_DOMAIN)
        self.spin_domain.SetBase(16)
        self.spin_domain.Enable(False)
        self.spin_type = wx.SpinCtrl(self, ID_SPIN_TYPE, max=MAX_TYPE)
        self.spin_type.SetBase(16)
        self.spin_type.Enable(False)
        self.spin_length = wx.SpinCtrl(self, ID_SPIN_LENGTH, max=MAX_LENGTH)
        self.spin_length.SetBase(16)
        self.spin_length.Enable(False)

        spinner_sizer = wx.FlexGridSizer(cols=2, vgap=0, hgap=0)
        spinner_sizer.AddGrowableCol(0)

        spinner_sizer.Add(
            wx.StaticText(self, label="Bank/Domain: "),
            flag=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT,
        )
        spinner_sizer.Add(self.spin_domain)
        spinner_sizer.Add(
            wx.StaticText(self, label="Type: "),
            flag=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT,
        )
        spinner_sizer.Add(self.spin_type)
        spinner_sizer.Add(
            wx.StaticText(self, label="Length: "),
            flag=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT,
        )
        spinner_sizer.Add(self.spin_length)

        self.panel_sizer.Add(self.toolbar, flag=wx.EXPAND)
        self.panel_sizer.Add(spinner_sizer, flag=wx.ALIGN_CENTER_HORIZONTAL)

        self.SetSizerAndFit(self.panel_sizer)

        self.Bind(wx.EVT_TOOL, self.on_toolbox)

    def on_toolbox(self, event):
        tool_id = event.GetId()

        if tool_id == ID_TOOL_ZOOM_OUT:
            self.level_view_ref.zoom_out()

        elif tool_id == ID_TOOL_ZOOM_IN:
            self.level_view_ref.zoom_in()

        elif tool_id == ID_TOOL_UNDO:
            self.enable_redo()

            # todo make events work
            if self.level_view_ref.undo_stack.undo_index - 1 <= 0:
                self.disable_undo()

            wx.PostEvent(self.GetParent(), UndoEvent(self.GetId()))

        elif tool_id == ID_TOOL_REDO:
            wx.PostEvent(self.GetParent(), RedoEvent(self.GetId()))

    def disable_buttons(self, event):
        evt_id = event.GetEventType()

        if evt_id == EVT_UNDO_CLEARED.typeId:
            self.disable_undo()
            self.disable_redo()

        elif evt_id == EVT_UNDO_SAVED.typeId:
            self.enable_undo()
            self.disable_redo()

        elif evt_id == EVT_UNDO_COMPLETE.typeId:
            self.enable_redo()
            if not event.undos_left:
                self.disable_undo()

        elif evt_id == EVT_REDO_COMPLETE.typeId:
            self.enable_undo()
            if not event.redos_left:
                self.disable_redo()

    def disable_undo(self):
        self.toolbar.EnableTool(ID_TOOL_UNDO, False)

    def enable_undo(self):
        self.toolbar.EnableTool(ID_TOOL_UNDO, True)

    def disable_redo(self):
        self.toolbar.EnableTool(ID_TOOL_REDO, False)

    def enable_redo(self):
        self.toolbar.EnableTool(ID_TOOL_REDO, True)

    def get_type(self):
        return self.spin_type.GetValue()

    def set_type(self, object_type: int):
        self.spin_type.SetValue(object_type)
        self.spin_type.Enable()

    def get_domain(self):
        return self.spin_domain.GetValue()

    def set_domain(self, domain: int):
        self.spin_domain.SetValue(domain)
        self.spin_domain.Enable()

    def get_length(self) -> int:
        return self.spin_length.GetValue()

    def set_length(self, length: int):
        self.spin_length.SetValue(length)
        self.spin_length.Enable()

    def enable_type(self, enable: bool, value: int = 0):
        self.spin_type.SetValue(value)
        self.spin_type.Enable(enable)

    def enable_domain(self, enable: bool, value: int = 0):
        self.spin_domain.SetValue(value)
        self.spin_domain.Enable(enable)

    def enable_length(self, enable: bool, value: int = 0):
        self.spin_length.SetValue(value)
        self.spin_length.Enable(enable)

    def clear_spinners(self):
        self.set_type(0x00)
        self.set_domain(0x00)
        self.set_length(0x00)

    def disable_all(self):
        self.clear_spinners()

        self.enable_type(False)
        self.enable_domain(False)
        self.enable_length(False)

    @staticmethod
    def is_length_spinner(spinner_id: int) -> bool:
        return spinner_id == ID_SPIN_LENGTH
