from PySide2.QtCore import QRect, QSize
from PySide2.QtGui import QColor, QImage, QPainter, Qt

from foundry.game.ObjectDefinitions import enemy_handle_x, enemy_handle_x2, enemy_handle_y
from foundry.game.ObjectSet import ObjectSet
from foundry.game.gfx.Palette import NESPalette
from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx.drawable import apply_selection_overlay
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects.ObjectLike import ObjectLike
from smb3parse.objects.object_set import ENEMY_ITEM_GRAPHICS_SET, ENEMY_ITEM_OBJECT_SET

MASK_COLOR = [0xFF, 0x33, 0xFF]


class EnemyObject(ObjectLike):
    def __init__(self, data, png_data, palette_group):
        super(EnemyObject, self).__init__()

        self.is_4byte = False
        self.is_single_block = True
        self.length = 0

        self.obj_index = data[0]
        self.x_position = data[1] - int(enemy_handle_x2[self.obj_index])
        self.y_position = data[2]

        self.domain = 0

        self.graphics_set = GraphicsSet(ENEMY_ITEM_GRAPHICS_SET)
        self.palette_group = palette_group

        self.object_set = ObjectSet(ENEMY_ITEM_OBJECT_SET)

        self.bg_color = NESPalette[palette_group[0][0]]

        self.png_data = png_data

        self.rect = QRect()

        self.selected = False

        self._setup()

    def _setup(self):
        obj_def = self.object_set.get_definition_of(self.obj_index)

        self.description = obj_def.description

        self.width = obj_def.bmp_width
        self.height = obj_def.bmp_height

        self.rect = QRect(self.x_position, self.y_position, self.width, self.height)

        self._render(obj_def)

    def _render(self, obj_def):
        self.blocks = []

        block_ids = obj_def.object_design

        for block_id in block_ids:
            x = (block_id % 64) * Block.WIDTH
            y = (block_id // 64) * Block.WIDTH

            self.blocks.append(self.png_data.copy(QRect(x, y, Block.WIDTH, Block.HEIGHT)))

    def render(self):
        # nothing to re-render since enemies are just copied over
        pass

    def draw(self, painter: QPainter, block_length, _):
        for i, image in enumerate(self.blocks):
            x = self.x_position + (i % self.width)
            y = self.y_position + (i // self.width)

            x_offset = int(enemy_handle_x[self.obj_index])
            y_offset = int(enemy_handle_y[self.obj_index])

            x += x_offset
            y += y_offset

            block = image.copy()

            mask = block.createMaskFromColor(QColor(*MASK_COLOR).rgb(), Qt.MaskOutColor)
            block.setAlphaChannel(mask)

            # todo better effect
            if self.selected:
                apply_selection_overlay(block, mask)

            if block_length != Block.SIDE_LENGTH:
                block = block.scaled(block_length, block_length)

            painter.drawImage(x * block_length, y * block_length, block)

    def get_status_info(self):
        return [("Name", self.description), ("X", self.x_position), ("Y", self.y_position)]

    def __contains__(self, item):
        x, y = item

        return self.point_in(x, y)

    def point_in(self, x, y):
        return self.rect.contains(x, y)

    def set_position(self, x, y):
        # todo also check for the upper bounds
        x = max(0, x)
        y = max(0, y)

        self.x_position = x
        self.y_position = y

        self.rect = QRect(self.x_position, self.y_position, self.width, self.height)

    def move_by(self, dx, dy):
        new_x = self.x_position + dx
        new_y = self.y_position + dy

        self.set_position(new_x, new_y)

    def get_position(self):
        return self.x_position, self.y_position

    def resize_by(self, dx, dy):
        pass

    @property
    def type(self):
        return self.obj_index

    def change_type(self, new_type):
        self.obj_index = new_type

        self._setup()

    def increment_type(self):
        self.obj_index = min(0xFF, self.obj_index + 1)

        self._setup()

    def decrement_type(self):
        self.obj_index = max(0, self.obj_index - 1)

        self._setup()

    def to_bytes(self):
        return bytearray([self.obj_index, self.x_position + int(enemy_handle_x2[self.obj_index]), self.y_position])

    def as_image(self) -> QImage:
        image = QImage(QSize(self.width * Block.SIDE_LENGTH, self.height * Block.SIDE_LENGTH), QImage.Format_RGBA8888,)

        image.fill(QColor(0, 0, 0, 0))

        painter = QPainter(image)

        self.draw(painter, Block.SIDE_LENGTH, True)

        return image

    def __repr__(self):
        return f"EnemyObject {self.description} at {self.x_position}, {self.y_position}"
