import wx

from Data import NESPalette, ENEMY_OBJ_DEF, enemy_handle_x, enemy_handle_y
from ObjectDefinitions import load_object_definition
from Sprite import Block
from game.gfx.objects.ObjectLike import ObjectLike
from game.gfx.PatternTable import PatternTable
from m3idefs import ObjectDefinition

MASK_COLOR = [0xFF, 0x33, 0xFF]


class EnemyObject(ObjectLike):
    def __init__(self, data, png_data, palette_group):
        super(EnemyObject, self).__init__()

        self.is_4byte = False

        self.obj_index = data[0]
        self.x_position = data[1]
        self.y_position = data[2]

        self.pattern_table = PatternTable(0x4C)
        self.palette_group = palette_group

        self.bg_color = NESPalette[palette_group[0][0]]

        self.png_data = png_data

        self.selected = False

        self._setup()

    def _setup(self):

        obj_data: ObjectDefinition = load_object_definition(ENEMY_OBJ_DEF)[
            self.obj_index
        ]

        self.description = obj_data.description

        self.width = obj_data.bmp_width
        self.height = obj_data.bmp_height

        self.rect = wx.Rect(self.x_position, self.y_position, self.width, self.height)

        self._render(obj_data)

    def _render(self, obj_data):
        self.blocks = []

        block_ids = obj_data.object_design

        for block_id in block_ids:
            x = (block_id % 64) * Block.WIDTH
            y = (block_id // 64) * Block.WIDTH

            self.blocks.append(
                self.png_data.GetSubImage(wx.Rect(x, y, Block.WIDTH, Block.HEIGHT))
            )

    def draw(self, dc, block_length, transparent):
        for i, image in enumerate(self.blocks):
            x = self.x_position + (i % self.width)
            y = self.y_position + (i // self.width)

            x_offset = int(enemy_handle_x[self.obj_index])
            y_offset = int(enemy_handle_y[self.obj_index])

            x += x_offset
            y += y_offset

            block = image.Copy()
            block.SetMaskColour(*MASK_COLOR)

            if not transparent:
                block.Replace(*MASK_COLOR, *self.bg_color)

            # todo better effect
            if self.selected:
                block = block.ConvertToDisabled(127)

            if block_length != Block.SIDE_LENGTH:
                block.Rescale(
                    block_length, block_length, quality=wx.IMAGE_QUALITY_NEAREST
                )

            dc.DrawBitmap(
                block.ConvertToBitmap(),
                x * block_length,
                y * block_length,
                useMask=transparent,
            )

    def get_status_info(self):
        return [
            ("Name", self.description),
            ("X", self.x_position),
            ("Y", self.y_position),
        ]

    def __contains__(self, item):
        x, y = item

        return self.point_in(x, y)

    def point_in(self, x, y):
        return self.rect.Contains(x, y)

    def set_position(self, x, y):
        # todo also check for the upper bounds
        x = max(0, x)
        y = max(0, y)

        self.x_position = x
        self.y_position = y

        self.rect = wx.Rect(self.x_position, self.y_position, self.width, self.height)

    def move_by(self, dx, dy):
        new_x = self.x_position + dx
        new_y = self.y_position + dy

        self.set_position(new_x, new_y)

    def get_position(self):
        return self.x_position, self.y_position

    def resize_to(self, _, __):
        pass

    def resize_by(self, dx, dy):
        new_x = self.x_position + dx
        new_y = self.y_position + dy

        self.resize_to(new_x, new_y)

    def change_type(self, new_type):
        self.obj_index = new_type

        self._setup()

    def get_rect(self):
        return self.rect

    def to_bytes(self):
        return bytearray([self.obj_index, self.x_position, self.y_position])
