from itertools import product
from typing import Tuple

from PySide2.QtCore import QPoint, QRect
from PySide2.QtGui import QBrush, QColor, QImage, QPainter, QPen, Qt

from foundry import data_dir
from foundry.game.File import ROM
from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx.Palette import NESPalette, bg_color_for_object_set, load_palette_group
from foundry.game.gfx.drawable import apply_selection_overlay
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects.EnemyItem import EnemyObject, MASK_COLOR
from foundry.game.gfx.objects.LevelObject import GROUND, SCREEN_HEIGHT, SCREEN_WIDTH
from foundry.game.gfx.objects.ObjectLike import EXPANDS_BOTH, EXPANDS_HORIZ, EXPANDS_VERT
from foundry.game.level.Level import Level
from foundry.gui.AutoScrollDrawer import AutoScrollDrawer
from smb3parse.constants import OBJ_AUTOSCROLL
from smb3parse.levels import LEVEL_MAX_LENGTH
from smb3parse.objects.object_set import CLOUDY_OBJECT_SET, DESERT_OBJECT_SET, DUNGEON_OBJECT_SET, ICE_OBJECT_SET

png = QImage(str(data_dir / "gfx.png"))
png.convertTo(QImage.Format_RGB888)


def _make_image_selected(image: QImage) -> QImage:
    alpha_mask = image.createAlphaMask()
    alpha_mask.invertPixels()

    selected_image = QImage(image)

    apply_selection_overlay(selected_image, alpha_mask)

    return selected_image


def _load_from_png(x: int, y: int):
    image = png.copy(QRect(x * 16, y * 16, 16, 16))
    mask = image.createMaskFromColor(QColor(*MASK_COLOR).rgb(), Qt.MaskOutColor)
    image.setAlphaChannel(mask)

    return image


FIRE_FLOWER = _load_from_png(16, 53)
LEAF = _load_from_png(17, 53)
NORMAL_STAR = _load_from_png(18, 53)
CONTINUOUS_STAR = _load_from_png(19, 53)
MULTI_COIN = _load_from_png(20, 53)
ONE_UP = _load_from_png(21, 53)
COIN = _load_from_png(22, 53)
VINE = _load_from_png(23, 53)
P_SWITCH = _load_from_png(24, 53)
SILVER_COIN = _load_from_png(25, 53)
INVISIBLE_COIN = _load_from_png(26, 53)
INVISIBLE_1_UP = _load_from_png(27, 53)

NO_JUMP = _load_from_png(32, 53)
UP_ARROW = _load_from_png(33, 53)
DOWN_ARROW = _load_from_png(34, 53)
LEFT_ARROW = _load_from_png(35, 53)
RIGHT_ARROW = _load_from_png(36, 53)

ITEM_ARROW = _load_from_png(53, 53)

EMPTY_IMAGE = _load_from_png(0, 53)


SPECIAL_BACKGROUND_OBJECTS = [
    "blue background",
    "starry background",
    "underground background under this",
    "sets background to actual background color",
]


def _block_from_index(block_index: int, level: Level) -> Block:
    """
    Returns the block at the given index, from the TSA table for the given level.

    :param block_index:
    :param level:
    :return:
    """

    palette_group = load_palette_group(level.object_set_number, level.header.object_palette_index)
    graphics_set = GraphicsSet(level.header.graphic_set_index)
    tsa_data = ROM().get_tsa_data(level.object_set_number)

    return Block(block_index, palette_group, graphics_set, tsa_data)


class LevelDrawer:
    def __init__(self):
        self.draw_jumps = False
        self.draw_grid = False
        self.draw_expansions = False
        self.draw_mario = False
        self.draw_jumps_on_objects = True
        self.draw_items_in_blocks = True
        self.draw_invisible_items = True
        self.draw_autoscroll = True
        self.transparency = False

        self.block_length = Block.WIDTH

        self.grid_pen = QPen(QColor(0x80, 0x80, 0x80, 0x80), width=1)
        self.screen_pen = QPen(QColor(0xFF, 0x00, 0x00, 0xFF), width=1)

    def draw(self, painter: QPainter, level: Level):
        self._draw_background(painter, level)

        if level.object_set_number == DESERT_OBJECT_SET:
            self._draw_desert_default_graphics(painter, level)
        elif level.object_set_number == DUNGEON_OBJECT_SET:
            self._draw_dungeon_default_graphics(painter, level)
        elif level.object_set_number == ICE_OBJECT_SET:
            self._draw_ice_default_graphics(painter, level)

        # painter.setPen(QPen(QColor(0x00, 0x00, 0x00, 0x80), width=1))
        # painter.setBrush(Qt.NoBrush)

        self._draw_objects(painter, level)

        self._draw_overlays(painter, level)

        if self.draw_expansions:
            self._draw_expansions(painter, level)

        if self.draw_mario:
            self._draw_mario(painter, level)

        if self.draw_jumps:
            self._draw_jumps(painter, level)

        if self.draw_grid:
            self._draw_grid(painter, level)

        if self.draw_autoscroll:
            self._draw_auto_scroll(painter, level)

    def _draw_background(self, painter: QPainter, level: Level):
        painter.save()

        if level.object_set_number == CLOUDY_OBJECT_SET:
            bg_color = NESPalette[load_palette_group(level.object_set_number, level.header.object_palette_index)[3][2]]
        else:
            bg_color = bg_color_for_object_set(level.object_set_number, level.header.object_palette_index)

        painter.fillRect(level.get_rect(self.block_length), bg_color)

        painter.restore()

    def _draw_dungeon_default_graphics(self, painter: QPainter, level: Level):
        # draw_background
        bg_block = _block_from_index(140, level)

        for x, y in product(range(level.width), range(level.height)):
            bg_block.draw(painter, x * self.block_length, y * self.block_length, self.block_length)

        # draw ceiling
        ceiling_block = _block_from_index(139, level)

        for x in range(level.width):
            ceiling_block.draw(painter, x * self.block_length, 0, self.block_length)

        # draw floor
        upper_floor_blocks = [_block_from_index(20, level), _block_from_index(21, level)]
        lower_floor_blocks = [_block_from_index(22, level), _block_from_index(23, level)]

        upper_y = (GROUND - 2) * self.block_length
        lower_y = (GROUND - 1) * self.block_length

        for block_x in range(level.width):
            pixel_x = block_x * self.block_length

            upper_floor_blocks[block_x % 2].draw(painter, pixel_x, upper_y, self.block_length)
            lower_floor_blocks[block_x % 2].draw(painter, pixel_x, lower_y, self.block_length)

    def _draw_desert_default_graphics(self, painter: QPainter, level: Level):
        floor_level = (GROUND - 1) * self.block_length
        floor_block_index = 86

        floor_block = _block_from_index(floor_block_index, level)

        for x in range(level.width):
            floor_block.draw(painter, x * self.block_length, floor_level, self.block_length)

    def _draw_ice_default_graphics(self, painter: QPainter, level: Level):
        bg_block = _block_from_index(0x80, level)

        for x, y in product(range(level.width), range(level.height)):
            bg_block.draw(painter, x * self.block_length, y * self.block_length, self.block_length)

    def _draw_objects(self, painter: QPainter, level: Level):
        for level_object in level.get_all_objects():
            level_object.render()

            if level_object.name.lower() in SPECIAL_BACKGROUND_OBJECTS:
                width = LEVEL_MAX_LENGTH
                height = GROUND - level_object.y_position

                blocks_to_draw = [level_object.blocks[0]] * width * height

                for index, block_index in enumerate(blocks_to_draw):
                    x = level_object.x_position + index % width
                    y = level_object.y_position + index // width

                    level_object._draw_block(painter, block_index, x, y, self.block_length, False)
            else:
                level_object.draw(painter, self.block_length, self.transparency)

            if level_object.selected:
                painter.save()

                painter.setPen(QPen(QColor(0x00, 0x00, 0x00, 0x80), width=1))
                painter.drawRect(level_object.get_rect(self.block_length))

                painter.restore()

    def _draw_overlays(self, painter: QPainter, level: Level):
        painter.save()

        for level_object in level.get_all_objects():
            name = level_object.name.lower()

            # only handle this specific enemy item for now
            if isinstance(level_object, EnemyObject) and "invisible door" not in name:
                continue

            pos = level_object.get_rect(self.block_length).topLeft()
            rect = level_object.get_rect(self.block_length)

            # invisible coins, for example, expand and need to have multiple overlays drawn onto them
            # set true by default, since for most overlays it doesn't matter
            fill_object = True

            # pipe entries
            if "pipe" in name and "can go" in name:
                if not self.draw_jumps_on_objects:
                    continue

                fill_object = False

                # center() is one pixel off for some reason
                pos = rect.topLeft() + QPoint(*(rect.size() / 2).toTuple())

                trigger_position = level_object.get_position()

                if "left" in name:
                    image = LEFT_ARROW

                    pos.setX(rect.right())
                    pos.setY(pos.y() - self.block_length / 2)

                    # leftward pipes trigger on the column to the left of the opening
                    x, y = level_object.get_rect().bottomRight().toTuple()
                    trigger_position = (x - 1, y)

                elif "right" in name:
                    image = RIGHT_ARROW
                    pos.setX(rect.left() - self.block_length)
                    pos.setY(pos.y() - self.block_length / 2)

                elif "down" in name:
                    image = DOWN_ARROW

                    pos.setX(pos.x() - self.block_length / 2)
                    pos.setY(rect.top() - self.block_length)
                else:
                    # upwards pipe
                    image = UP_ARROW

                    pos.setX(pos.x() - self.block_length / 2)
                    pos.setY(rect.bottom())

                    # upwards pipes trigger on the second to last row
                    x, y = level_object.get_rect().bottomLeft().toTuple()
                    trigger_position = (x, y - 1)

                if not self._object_in_jump_area(level, trigger_position):
                    image = NO_JUMP

            elif "door" == name or "door (can go" in name or "invisible door" in name or "red invisible note" in name:
                fill_object = False

                if "note" in name:
                    image = UP_ARROW
                else:
                    # door
                    image = DOWN_ARROW

                pos.setY(rect.top() - self.block_length)

                x, y = level_object.get_position()

                # jumps seemingly trigger on the bottom block
                if not self._object_in_jump_area(level, (x, y + 1)):
                    image = NO_JUMP

            # "?" - blocks, note blocks, wooden blocks and bricks
            elif "'?' with" in name or "brick with" in name or "bricks with" in name or "block with" in name:
                if not self.draw_items_in_blocks:
                    continue

                pos.setY(pos.y() - self.block_length)

                if "flower" in name:
                    image = FIRE_FLOWER
                elif "leaf" in name:
                    image = LEAF
                elif "continuous star" in name:
                    image = CONTINUOUS_STAR
                elif "star" in name:
                    image = NORMAL_STAR
                elif "multi-coin" in name:
                    image = MULTI_COIN
                elif "coin" in name:
                    image = COIN
                elif "1-up" in name:
                    image = ONE_UP
                elif "vine" in name:
                    image = VINE
                elif "p-switch" in name:
                    image = P_SWITCH
                else:
                    image = EMPTY_IMAGE

                # draw little arrow for the offset item overlay
                arrow_pos = QPoint(pos)
                arrow_pos.setY(arrow_pos.y() + self.block_length / 4)
                painter.drawImage(arrow_pos, ITEM_ARROW.scaled(self.block_length, self.block_length))

            elif "invisible" in name:
                if not self.draw_invisible_items:
                    continue

                if "coin" in name:
                    image = INVISIBLE_COIN
                elif "1-up" in name:
                    image = INVISIBLE_1_UP
                else:
                    image = EMPTY_IMAGE

            elif "silver coins" in name:
                if not self.draw_invisible_items:
                    continue

                image = SILVER_COIN
            else:
                continue

            if fill_object:
                for x in range(level_object.rendered_width):
                    adapted_pos = QPoint(pos)
                    adapted_pos.setX(pos.x() + x * self.block_length)

                    image = image.scaled(self.block_length, self.block_length)
                    painter.drawImage(adapted_pos, image)

                    if level_object.selected:
                        painter.drawImage(adapted_pos, _make_image_selected(image))

            else:
                image = image.scaled(self.block_length, self.block_length)
                painter.drawImage(pos, image)

        painter.restore()

    @staticmethod
    def _object_in_jump_area(level: Level, pos: Tuple[int, int]):
        for jump in level.jumps:
            jump_rect = jump.get_rect(1, level.is_vertical)

            if jump_rect.contains(QPoint(*pos)):
                return True
        else:
            return False

    def _draw_expansions(self, painter: QPainter, level: Level):
        for level_object in level.get_all_objects():
            if level_object.selected:
                painter.drawRect(level_object.get_rect(self.block_length))

            if self.draw_expansions:
                painter.save()

                painter.setPen(Qt.NoPen)

                if level_object.expands() == EXPANDS_BOTH:
                    painter.setBrush(QColor(0xFF, 0, 0xFF, 0x80))
                elif level_object.expands() == EXPANDS_HORIZ:
                    painter.setBrush(QColor(0xFF, 0, 0, 0x80))
                elif level_object.expands() == EXPANDS_VERT:
                    painter.setBrush(QColor(0, 0, 0xFF, 0x80))

                painter.drawRect(level_object.get_rect(self.block_length))

                painter.restore()

    def _draw_mario(self, painter: QPainter, level: Level):
        mario_actions = QImage(str(data_dir / "mario.png"))

        mario_actions.convertTo(QImage.Format_RGBA8888)

        mario_position = QPoint(*level.header.mario_position()) * self.block_length

        x_offset = 32 * level.start_action

        mario_cutout = mario_actions.copy(QRect(x_offset, 0, 32, 32)).scaled(
            2 * self.block_length, 2 * self.block_length
        )

        painter.drawImage(mario_position, mario_cutout)

    def _draw_jumps(self, painter: QPainter, level: Level):
        for jump in level.jumps:
            painter.setBrush(QBrush(QColor(0xFF, 0x00, 0x00), Qt.FDiagPattern))

            painter.drawRect(jump.get_rect(self.block_length, level.is_vertical))

    def _draw_grid(self, painter: QPainter, level: Level):
        panel_width, panel_height = level.get_rect(self.block_length).size().toTuple()

        painter.setPen(self.grid_pen)

        for x in range(0, panel_width, self.block_length):
            painter.drawLine(x, 0, x, panel_height)
        for y in range(0, panel_height, self.block_length):
            painter.drawLine(0, y, panel_width, y)

        painter.setPen(self.screen_pen)

        if level.is_vertical:
            for y in range(0, panel_height, self.block_length * SCREEN_HEIGHT):
                painter.drawLine(0, self.block_length + y, panel_width, self.block_length + y)
        else:
            for x in range(0, panel_width, self.block_length * SCREEN_WIDTH):
                painter.drawLine(x, 0, x, panel_height)

    def _draw_auto_scroll(self, painter: QPainter, level: Level):
        for item in level.enemies:
            if item.obj_index == OBJ_AUTOSCROLL:
                break
        else:
            return

        drawer = AutoScrollDrawer(item.y_position, level)

        drawer.draw(painter, self.block_length)
