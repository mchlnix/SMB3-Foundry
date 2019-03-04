import wx


class Spritesheet(wx.Bitmap):
    def __init__(self, source, sprite_width=16, sprite_height=16, *args, **kwargs):
        super(Spritesheet, self).__init__(*args, **kwargs)

        self.source = wx.Bitmap(source)
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height

        self.sprite_cache = dict()

    def get_sprite(self, x, y, width=None, height=None):
        if width is None:
            width = self.sprite_width

        if height is None:
            height = self.sprite_height

        x, y = x * self.sprite_width, y * self.sprite_height

        key = (x, y, width, height)

        if key not in self.sprite_cache:
            cut_out = wx.Rect(*key)

            new_bitmap = self.source.GetSubBitmap(cut_out)

            self.sprite_cache[key] = new_bitmap

        return self.sprite_cache[key]
