import wx

from Graphics import LevelObject, PatternTable
from Level import _load_rom_object_definition, Level
from Sprite import Block


class ObjectViewer(wx.Frame):
    def __init__(self, parent):
        super(ObjectViewer, self).__init__(parent, title="Object Viewer")

        self.object_set = 1

        self.object_definitions = _load_rom_object_definition(self.object_set)

        self.drawing_area = ObjectDrawArea(self, self.object_set, self.object_definitions)

        self.Bind(wx.EVT_CLOSE, self.on_exit)

    def on_exit(self, _):
        self.Hide()


class ObjectDrawArea(wx.Panel):
    def __init__(self, parent, object_set, object_definitions, graphic_set=1, palette_index=0):
        super(ObjectDrawArea, self).__init__(parent)

        self.object_set = object_set
        self.palette_group = Level.palettes[self.object_set][palette_index]
        self.pattern_table = PatternTable(graphic_set)
        self.current_object = LevelObject([0x0, 0x00, 0x0], object_set, object_definitions, self.palette_group,
                                          self.pattern_table)

        self.resize()

        self.Bind(wx.EVT_PAINT, self.draw)

    def resize(self):
        self.SetSize(self.current_object.rendered_width * Block.WIDTH,
                     self.current_object.rendered_height * Block.HEIGHT)

        self.GetParent().SetClientSize(self.GetSize())
        self.GetParent().Fit()

    def draw(self, _):
        dc = wx.BufferedPaintDC(self)

        dc.Clear()

        self.current_object.draw(dc, transparent=True)
