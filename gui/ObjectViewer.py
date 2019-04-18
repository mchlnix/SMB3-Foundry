import wx

from Graphics import LevelObject, PatternTable
from Level import _load_rom_object_definition, Level
from Sprite import Block

ID_SPIN_DOMAIN = 1
ID_SPIN_TYPE = 2
ID_SPIN_LENGTH = 3

MAX_DOMAIN = 7
MAX_TYPE = 0xFF
MAX_LENGTH = 0xFF


class ObjectViewer(wx.Frame):
    def __init__(self, parent):
        super(ObjectViewer, self).__init__(parent, title="Object Viewer")

        self.spin_domain = wx.SpinCtrl(self, ID_SPIN_DOMAIN, max=MAX_DOMAIN)
        self.spin_domain.SetBase(16)
        self.spin_type = wx.SpinCtrl(self, ID_SPIN_TYPE, max=MAX_TYPE)
        self.spin_type.SetBase(16)
        self.spin_length = wx.SpinCtrl(self, ID_SPIN_LENGTH, max=MAX_LENGTH)
        self.spin_length.SetBase(16)
        self.spin_length.Enable(False)

        spin_sizer = wx.BoxSizer(wx.HORIZONTAL)

        spin_sizer.Add(self.spin_domain)
        spin_sizer.Add(self.spin_type)
        spin_sizer.Add(self.spin_length)

        self.object_set = 1

        self.object_definitions = _load_rom_object_definition(self.object_set)

        self.drawing_area = ObjectDrawArea(self, self.object_set, self.object_definitions)

        self.status_bar = wx.StatusBar(parent=self)
        self.status_bar.SetStatusText(self.drawing_area.current_object.description)

        vert_sizer = wx.BoxSizer(wx.VERTICAL)

        vert_sizer.Add(spin_sizer, flag=wx.EXPAND)
        vert_sizer.Add(self.drawing_area, proportion=1, flag=wx.EXPAND)
        vert_sizer.Add(self.status_bar, flag=wx.EXPAND)

        self.SetSizer(vert_sizer)

        self.drawing_area.Refresh()

        self.resize()

        self.Bind(wx.EVT_CLOSE, self.on_exit)
        self.Bind(wx.EVT_SIZE, self.resize)
        self.Bind(wx.EVT_SPINCTRL, self.on_spin)

    def resize(self, _=None):
        self.SetMinSize(wx.Size(1, 1))
        self.Layout()
        self.Fit()
        self.SetMinSize(self.GetSize())

    def on_spin(self, event):
        _id = event.GetId()

        object_data = bytearray(4)

        object_data[0] = self.spin_domain.GetValue() << 5
        object_data[1] = 0
        object_data[2] = self.spin_type.GetValue()
        object_data[3] = self.spin_length.GetValue()

        self.drawing_area.change_object(object_data)

        if _id != ID_SPIN_LENGTH:
            if self.drawing_area.current_object.is_4byte:
                self.spin_length.Enable(True)
            else:
                self.spin_length.SetValue(0)
                self.spin_length.Enable(False)

        self.drawing_area.Refresh()

        self.status_bar.SetStatusText(self.drawing_area.current_object.description)

        self.resize()

    def on_exit(self, _):
        self.Hide()


class ObjectDrawArea(wx.Panel):
    def __init__(self, parent, object_set, object_definitions, graphic_set=1, palette_index=0):
        super(ObjectDrawArea, self).__init__(parent)

        self.object_set = object_set
        self.object_definitions = object_definitions
        self.palette_group = Level.palettes[self.object_set][palette_index]
        self.pattern_table = PatternTable(graphic_set)

        self.current_object = None

        self.change_object([0x0, 0x0, 0x0])

        self.resize()

        self.Bind(wx.EVT_PAINT, self.draw)

    def resize(self):
        self.SetMinSize(wx.Size(self.current_object.rendered_width * Block.WIDTH,
                                self.current_object.rendered_height * Block.HEIGHT))
        self.Fit()

    def change_object(self, object_data):
        LevelObject.ground_map = []
        self.current_object = LevelObject(object_data, self.object_set, self.object_definitions, self.palette_group,
                                          self.pattern_table)

        self.resize()

    def draw(self, _):
        dc = wx.BufferedPaintDC(self)

        dc.Clear()

        self.current_object.draw(dc, transparent=True)
