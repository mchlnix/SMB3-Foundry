import wx

from Graphics import LevelObject, LevelObjectFactory
from LevelSelector import OBJECT_SET_ITEMS
from Sprite import Block

ID_SPIN_DOMAIN = 1
ID_SPIN_TYPE = 2
ID_SPIN_LENGTH = 3
ID_OBJECT_SET_DROPDOWN = 4
ID_GFX_SET_DROPDOWN = 5

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

        self.object_set_dropdown = wx.ComboBox(
            parent=self, id=ID_OBJECT_SET_DROPDOWN, choices=OBJECT_SET_ITEMS[1:]
        )
        self.object_set_dropdown.SetSelection(0)

        self.graphic_set_dropdown = wx.ComboBox(
            parent=self,
            id=ID_GFX_SET_DROPDOWN,
            choices=[f"Graphics Set {gfx_set}" for gfx_set in range(32)],
        )
        self.graphic_set_dropdown.SetSelection(1)

        spin_sizer.Add(self.object_set_dropdown)
        spin_sizer.Add(self.graphic_set_dropdown)

        self.object_set = 1

        self.drawing_area = ObjectDrawArea(self, self.object_set)

        self.status_bar = wx.StatusBar(parent=self)
        self.status_bar.SetStatusText(self.drawing_area.current_object.description)

        vert_sizer = wx.BoxSizer(wx.VERTICAL)

        vert_sizer.Add(spin_sizer, flag=wx.EXPAND)
        vert_sizer.Add(self.drawing_area, proportion=1, flag=wx.EXPAND)
        vert_sizer.Add(self.status_bar, flag=wx.EXPAND)

        self.SetSizer(vert_sizer)

        self.drawing_area.Refresh()

        self.resize()

        self.Bind(wx.EVT_COMBOBOX, self.on_combo)
        self.Bind(wx.EVT_CLOSE, self.on_exit)
        self.Bind(wx.EVT_SIZE, self.resize)
        self.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_press)

    def on_key_press(self, event):
        key = event.GetKeyCode()

        if key == wx.WXK_ESCAPE:
            self.on_exit(None)

    def on_combo(self, event):
        dropdown_id = event.GetId()

        if dropdown_id == ID_OBJECT_SET_DROPDOWN:
            self.object_set = self.object_set_dropdown.GetSelection() + 1
            gfx_set = self.object_set

            self.graphic_set_dropdown.SetSelection(gfx_set)

            self.drawing_area.change_object_set(self.object_set)
        elif dropdown_id == ID_GFX_SET_DROPDOWN:
            gfx_set = self.graphic_set_dropdown.GetSelection()
        else:
            return

        self.drawing_area.change_graphic_set(gfx_set)
        self.status_bar.SetStatusText(self.drawing_area.current_object.description)

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

        self.drawing_area.update_object(object_data)

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
    def __init__(self, parent, object_set, graphic_set=1, palette_index=0):
        super(ObjectDrawArea, self).__init__(parent)

        self.object_factory = LevelObjectFactory(object_set, graphic_set, palette_index, False)

        self.current_object = None

        self.update_object([0x0, 0x0, 0x0])

        self.resize()

        self.Bind(wx.EVT_PAINT, self.draw)

    def change_object_set(self, object_set):
        self.object_factory.set_object_set(object_set)

        self.update_object()

    def change_graphic_set(self, graphic_set):
        self.object_factory.set_graphic_set(graphic_set)
        self.update_object()

    def resize(self):
        self.SetMinSize(
            wx.Size(
                self.current_object.rendered_width * Block.WIDTH,
                self.current_object.rendered_height * Block.HEIGHT,
            )
        )
        self.Fit()

    def update_object(self, object_data=None):
        # todo remove after fixing ground map
        LevelObject.ground_map = []
        if object_data is None:
            object_data = self.current_object.data

        self.current_object = self.object_factory.from_data(object_data, 0)

        self.resize()
        self.Refresh()

    def draw(self, _):
        dc = wx.BufferedPaintDC(self)

        dc.Clear()

        dc.SetDeviceOrigin(
            -Block.WIDTH * self.current_object.rendered_base_x,
            -Block.HEIGHT * self.current_object.rendered_base_y,
        )

        self.current_object.draw(dc, transparent=True)
