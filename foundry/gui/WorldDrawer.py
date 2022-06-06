from PySide6.QtCore import QPoint, QRect, QSize
from PySide6.QtGui import QColor, QImage, QPainter, QPen, Qt

from foundry import data_dir
from foundry.game.File import ROM
from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx.Palette import load_palette_group
from foundry.game.gfx.drawable import apply_selection_overlay
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects.EnemyItem import EnemyObject, MASK_COLOR
from foundry.game.gfx.objects.LevelObject import GROUND, SCREEN_WIDTH
from foundry.game.level.Level import Level
from foundry.game.level.WorldMap import WorldMap
from smb3parse.constants import (
    MAPOBJ_AIRSHIP,
    MAPOBJ_BATTLESHIP,
    MAPOBJ_BOOMERANGBRO,
    MAPOBJ_CANOE,
    MAPOBJ_COINSHIP,
    MAPOBJ_EMPTY,
    MAPOBJ_FIREBRO,
    MAPOBJ_HAMMERBRO,
    MAPOBJ_HEAVYBRO,
    MAPOBJ_HELP,
    MAPOBJ_NSPADE,
    MAPOBJ_TANK,
    MAPOBJ_UNK08,
    MAPOBJ_UNK0C,
    MAPOBJ_W7PLANT,
    MAPOBJ_W8AIRSHIP,
    MAPOBJ_WHITETOADHOUSE,
)
from smb3parse.levels import LEVEL_MAX_LENGTH

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

MAP_OBJ_SPRITES = {
    MAPOBJ_EMPTY: EMPTY_IMAGE,
    MAPOBJ_HELP: _load_from_png(43, 2),
    MAPOBJ_AIRSHIP: _load_from_png(44, 2),
    MAPOBJ_HAMMERBRO: _load_from_png(45, 2),
    MAPOBJ_BOOMERANGBRO: _load_from_png(46, 2),
    MAPOBJ_HEAVYBRO: _load_from_png(47, 2),
    MAPOBJ_FIREBRO: _load_from_png(48, 2),
    MAPOBJ_W7PLANT: _load_from_png(49, 2),
    MAPOBJ_UNK08: _load_from_png(50, 2),
    MAPOBJ_NSPADE: _load_from_png(51, 2),
    MAPOBJ_WHITETOADHOUSE: _load_from_png(52, 2),
    MAPOBJ_COINSHIP: _load_from_png(53, 2),
    MAPOBJ_UNK0C: _load_from_png(54, 2),
    MAPOBJ_BATTLESHIP: _load_from_png(55, 2),
    MAPOBJ_TANK: _load_from_png(56, 2),
    MAPOBJ_W8AIRSHIP: _load_from_png(57, 2),
    MAPOBJ_CANOE: _load_from_png(58, 2),
}

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


class WorldDrawer:
    def __init__(self):
        self.draw_level_pointers = True
        self.draw_sprites = True
        self.draw_start = True
        self.draw_airship_points = True
        self.draw_pipes = True
        self.draw_locks = True

        self.block_length = Block.WIDTH

        self.grid_pen = QPen(QColor(0x80, 0x80, 0x80, 0x80), 1)
        self.screen_pen = QPen(QColor(0xFF, 0x00, 0x00, 0xFF), 1)

    def draw(self, painter: QPainter, world: WorldMap):
        self._draw_background(painter, world)

        self._draw_tiles(painter, world)

        if self.draw_level_pointers:
            # TODO: Fix and understand rules on where pointers can be
            # self._draw_level_pointers(painter, world)
            pass

        if self.draw_sprites:
            self._draw_sprites(painter, world)

        if self.draw_start:
            self._draw_start_position(painter, world)

        self.draw_airship_points = True
        self.draw_pipes = True
        self.draw_locks = True

        self._draw_overlays(painter, world)

    def _draw_background(self, painter: QPainter, world: WorldMap):
        painter.save()

        bg_color = QColor(0xFF, 0, 0xFF, 0xFF)

        painter.fillRect(world.get_rect(self.block_length), bg_color)

        painter.restore()

    def _draw_tiles(self, painter: QPainter, world: WorldMap):
        for tile in world.get_all_objects():
            tile.render()

            if tile.name.lower() in SPECIAL_BACKGROUND_OBJECTS:
                width = LEVEL_MAX_LENGTH
                height = GROUND - tile.y_position

                blocks_to_draw = [tile.blocks[0]] * width * height

                for index, block_index in enumerate(blocks_to_draw):
                    x = tile.x_position + index % width
                    y = tile.y_position + index // width

                    tile._draw_block(painter, block_index, x, y, self.block_length, False)
            else:
                tile.draw(painter, self.block_length, False)

            if tile.selected:
                painter.save()

                painter.setPen(QPen(QColor(0x00, 0x00, 0x00, 0x80), 1))
                painter.drawRect(tile.get_rect(self.block_length))

                painter.restore()

    def _draw_level_pointers(self, painter: QPainter, world: WorldMap):
        painter.save()

        for tile_on_map in world._internal_world_map.gen_positions():
            if not tile_on_map.could_have_a_level():
                continue

            x = ((tile_on_map.screen - 1) * SCREEN_WIDTH + tile_on_map.column) * self.block_length
            y = tile_on_map.row * self.block_length

            painter.setPen(QPen(QColor(0xFF, 0x00, 0x00, 0x80), 2))
            painter.drawRect(x, y, self.block_length, self.block_length)

        painter.restore()

    def _draw_sprites(self, painter: QPainter, world: WorldMap):
        painter.save()

        for tile_on_map in world._internal_world_map.gen_positions():
            if not (sprite_id := tile_on_map.sprite()):
                continue

            x = ((tile_on_map.screen - 1) * SCREEN_WIDTH + tile_on_map.column) * self.block_length
            y = tile_on_map.row * self.block_length

            painter.setPen(QPen(QColor(0x00, 0x00, 0xFF, 0x80), 4))
            painter.drawImage(QPoint(x, y), MAP_OBJ_SPRITES[sprite_id].scaled(self.block_length, self.block_length))

        painter.restore()

    def _draw_start_position(self, painter: QPainter, world: WorldMap):
        painter.save()

        world, screen, y, x = world._internal_world_map.start_pos.tuple()

        x *= self.block_length
        y *= self.block_length

        painter.fillRect(
            QRect(QPoint(x, y), QSize(self.block_length, self.block_length)), QColor(0x00, 0xFF, 0x00, 0x80)
        )

        painter.restore()

    def _draw_overlays(self, painter: QPainter, world: WorldMap):
        painter.save()

        for level_object in world.get_all_objects():
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

                if not self._object_in_jump_area(world, trigger_position):
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
                if not self._object_in_jump_area(world, (x, y + 1)):
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
