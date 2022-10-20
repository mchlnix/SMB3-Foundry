from PySide6.QtCore import QRect, QSize
from PySide6.QtGui import QColor, QImage, QPainter, Qt

from foundry.game.ObjectDefinitions import enemy_handle_x, enemy_handle_x2, enemy_handle_y
from foundry.game.ObjectSet import ObjectSet
from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx.Palette import PaletteGroup
from foundry.game.gfx.drawable import MASK_COLOR, apply_selection_overlay
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from smb3parse.constants import OBJ_AUTOSCROLL, OBJ_BOOMBOOM, OBJ_FLYING_BOOMBOOM
from smb3parse.objects.object_set import ENEMY_ITEM_GRAPHICS_SET, ENEMY_ITEM_OBJECT_SET


class EnemyItem(InLevelObject):
    def __init__(self, data, png_data, palette_group: PaletteGroup):
        super(EnemyItem, self).__init__()

        self.data = data

        self.is_4byte = False
        self.is_fixed = True
        self.length = 0

        self.obj_index = data[0]

        # boom boom specific
        if self._is_boom_boom():
            # lock index is encoded in high nibble of the y-position
            self.lock_index = max((data[2] >> 4) - 1, 0)
        else:
            self.lock_index = 0

        if self.obj_index == OBJ_AUTOSCROLL:
            self.auto_scroll_type = data[2]
            data[2] = 0
        else:
            self.auto_scroll_type = 0

        x = data[1] - enemy_handle_x2[self.obj_index]
        y = data[2] - self.lock_index * 0x10

        self.set_position(x, y)

        self.domain = 0

        self.graphics_set = GraphicsSet(ENEMY_ITEM_GRAPHICS_SET)
        self.palette_group = palette_group

        self.object_set = ObjectSet(ENEMY_ITEM_OBJECT_SET)

        self.png_data = png_data

        self.selected = False

        self._setup()

    @property
    def rect(self):
        return QRect(
            self.x_position + enemy_handle_x[self.obj_index],
            self.y_position + enemy_handle_y[self.obj_index],
            self.width,
            self.height,
        )

    def _setup(self):
        obj_def = self.object_set.get_definition_of(self.obj_index)

        self.name = obj_def.description

        self.width = self.rendered_width = obj_def.bmp_width
        self.height = self.rendered_height = obj_def.bmp_height

        self._render(obj_def)

    def _render(self, obj_def):
        self.blocks = []

        block_ids = obj_def.object_design

        for block_id in block_ids:
            x = (block_id % 64) * Block.WIDTH
            y = (block_id // 64) * Block.WIDTH

            self.blocks.append(self.png_data.copy(QRect(x, y, Block.WIDTH, Block.HEIGHT)))

    def copy(self):
        return EnemyItem(self.to_bytes(), self.png_data, self.palette_group)

    def render(self):
        # nothing to re-render since enemies are just copied over
        pass

    def draw(self, painter: QPainter, block_length: int, _, use_offsets=True):
        """
        :param painter:
        :param block_length:
        :param _: ignored for enemies
        :param bool use_offsets: Whether to use the additional offsets. Necessary when drawing in level, but not when
            rendering in the object toolbar, or in the object dropdown.
        """
        for i, image in enumerate(self.blocks):
            x = self.x_position + (i % self.width)
            y = self.y_position + (i // self.width)

            if use_offsets:
                x_offset = enemy_handle_x[self.obj_index]
                y_offset = enemy_handle_y[self.obj_index]
            else:
                x_offset = enemy_handle_x2[self.obj_index]
                y_offset = 0

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
        return [("Name", self.name), ("X", self.x_position), ("Y", self.y_position)]

    def set_position(self, x, y):
        # todo also check for the upper bounds
        x = max(0, x)
        y = max(0, y)

        if self._is_auto_scroll():
            y = 0

        self.x_position = x
        self.y_position = y

        self.data = self.to_bytes()

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
        self.data = self.to_bytes()

    def decrement_type(self):
        self.obj_index = max(0, self.obj_index - 1)

        self._setup()
        self.data = self.to_bytes()

    def to_bytes(self):
        y_position = self.y_position

        if self._is_boom_boom():
            y_position += 0x10 * self.lock_index
        elif self._is_auto_scroll():
            y_position = self.auto_scroll_type

        return bytearray([self.obj_index, self.x_position + int(enemy_handle_x2[self.obj_index]), y_position])

    def as_image(self) -> QImage:
        image = QImage(
            QSize(self.width * Block.SIDE_LENGTH, self.height * Block.SIDE_LENGTH),
            QImage.Format_RGBA8888,
        )

        image.fill(QColor(0, 0, 0, 0))

        painter = QPainter(image)

        self.draw(painter, Block.SIDE_LENGTH, True, use_offsets=False)

        return image

    def __str__(self):
        return f"{self.name} at {self.x_position}, {self.y_position}"

    def __repr__(self):
        return f"EnemyObject: {self}"

    def _is_boom_boom(self):
        return self.type in [OBJ_BOOMBOOM, OBJ_FLYING_BOOMBOOM]

    def _is_auto_scroll(self):
        return self.type == OBJ_AUTOSCROLL
