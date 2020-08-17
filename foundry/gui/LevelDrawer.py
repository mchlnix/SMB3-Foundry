from PySide2.QtCore import QPoint, QRect
from PySide2.QtGui import QBrush, QColor, QImage, QPainter, QPen, Qt

from foundry.core.util.add_selection_graphic_to_image import add_selection_graphic_to_image
from foundry.gui.settings import SETTINGS, observe_setting, get_setting
from foundry import data_dir
from foundry.game.File import ROM
from foundry.game.gfx.Palette import load_palette
from foundry.game.gfx.PatternTableHandler import PatternTableHandler
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects.EnemyItem import EnemyObject, MASK_COLOR
from foundry.game.gfx.objects.LevelObjectController import LevelObjectController
from foundry.game.gfx.objects.LevelObject import GROUND, SCREEN_HEIGHT, SCREEN_WIDTH
from foundry.game.gfx.objects.ObjectLike import EXPANDS_BOTH, EXPANDS_HORIZ, EXPANDS_VERT
from foundry.game.level.Level import Level
from foundry.game.Tileset import Tileset

png = QImage(str(data_dir / "gfx.png"))
png.convertTo(QImage.Format_RGB888)


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
]


def _block_from_index(block_index: int, level: Level) -> Block:
    """
    Returns the block at the given index, from the TSA table for the given level.

    :param block_index:
    :param level:
    :return:
    """

    palette_group = load_palette(level.object_set_number, level.header.object_palette_index)
    graphics_set = PatternTableHandler(level.header.graphic_set_index)
    tsa_data = ROM().get_tsa_data(level.object_set_number)

    return Block.from_rom(block_index, palette_group, graphics_set, tsa_data)


class LevelDrawer:
    def __init__(self):
        self.draw_invisible_items = SETTINGS["draw_invisible_items"]
        self.transparency = SETTINGS["block_transparency"]
        self.background_enabled = SETTINGS["background_enabled"]
        self.tsa_data = None

        self.block_length = Block.default_size

        self.grid_pen = QPen(QColor(0x80, 0x80, 0x80, 0x80), width=1)
        self.screen_pen = QPen(QColor(0xFF, 0x00, 0x00, 0xFF), width=1)

        self.block_from_rom = {}
        self.block_quick = []
        self.block_quick_object_set = -1
        self.block_quick_block_length = -1
        self.block_transparency = -1

    def draw(self, painter: QPainter, level: Level, force=False):
        self._draw_objects(painter, level, force)

        self._draw_overlays(painter, level)

        if get_setting("draw_expansion", True):
            self._draw_expansions(painter, level)

        if get_setting("draw_mario", True):
            self._draw_mario(painter, level)

        if get_setting("draw_jumps", True):
            self._draw_jumps(painter, level)

        if get_setting("draw_grid", False):
            self._draw_grid(painter, level)

    def _get_background(self, level: Level):
        background_routine_by_objectset = {
            0: self.default_background,
            1: self.default_background,
            2: self.fortress_background,
            3: self.default_background,
            4: self.sky_background,
            5: self.default_background,
            6: self.default_background,
            7: self.default_background,
            8: self.default_background,
            9: self.desert_background,
            10: self.default_background,
            11: self.default_background,
            12: self.sky_background,
            13: self.default_background,
            14: self.default_background,
            15: self.default_background
        }

        return background_routine_by_objectset[level.object_set_number](level)

    def default_background(self, level: Level):
        object_set = Tileset(level.object_set_number)
        level_rect = level.get_rect()
        return [object_set.background_block for _ in level_rect.position_indexes()]

    def sky_background(self, level: Level):
        blocks = []
        object_set = Tileset(level.object_set_number)
        level_rect = level.get_rect()
        for pos in level_rect.positions():
            if pos.y != 0:
                blocks.append(object_set.background_block)
            else:
                blocks.append(0x86)
        return blocks

    def desert_background(self, level: Level):
        blocks = []
        object_set = Tileset(level.object_set_number)
        level_rect = level.get_rect()
        for pos in level_rect.positions():
            if pos.y != GROUND - 1:
                blocks.append(object_set.background_block)
            else:
                blocks.append(0x56)
        return blocks

    def fortress_background(self, level: Level):
        blocks = []
        fortress_blocks = [0x14, 0x15, 0x16, 0x17]
        object_set = Tileset(level.object_set_number)
        level_rect = level.get_rect()
        for pos in level_rect.positions():
            if pos.y == 0:
                blocks.append(0xE5)
            elif pos.y == 1:
                blocks.append(0x8E)
            elif pos.y == GROUND - 1:
                blocks.append(fortress_blocks[2 + pos.x % 2])
            elif pos.y == GROUND - 2:
                blocks.append(fortress_blocks[pos.x % 2])
            else:
                blocks.append(object_set.background_block)
        return blocks

    def _get_objects(self, level, blocks, level_rect):
        width = level_rect.abs_size.width
        for level_object in level.get_all_objects():

            if not isinstance(level_object, LevelObjectController):
                continue
            for block in level_object.get_blocks_and_positions():
                if block[0] >= 0:
                    try:
                        blocks[block[1].x + block[1].y * width] = block[0]
                    except IndexError:
                        pass
        return blocks


    def get_blocks(self, level, force=False):
        if len(self.block_quick) == 0 or self.block_quick_object_set != level.object_set_number or self.block_length != \
                self.block_quick_block_length or self.block_transparency != self.transparency or force:
            self.block_quick_object_set = level.object_set_number
            palette_group = load_palette(level.object_set_number, level.header.object_palette_index)
            tsa_data = ROM.get_tsa_data(level.object_set_number)
            graphics_set = PatternTableHandler.from_tileset(level.header.graphic_set_index)
            blocks = []
            for i in range(0xFF):
                blocks.append(Block.from_rom(i, palette_group, graphics_set, tsa_data).qpixmap_custom(
                    self.block_length, self.block_length, transparent=self.transparency
                ))
            self.block_quick_block_length = self.block_length
            self.block_quick = blocks
            self.block_transparency = self.transparency

        return self.block_quick

    def render_blocks(self, painter, blocks, pixmaps, level_rect):
        current_block = None
        brushes = [QBrush(pix) for pix in pixmaps]
        x_length = self.block_length * level_rect.abs_size.width
        painter.setPen(Qt.NoPen)
        x, y = -self.block_length, -self.block_length
        for idx, block in enumerate(blocks):
            x += self.block_length
            x %= x_length
            if x == 0:
                y += self.block_length
            if current_block != blocks[idx]:
                current_block = blocks[idx]
                painter.setBrush(brushes[blocks[idx]])
            painter.drawRect(x, y, self.block_length, self.block_length)
        painter.setBrush(Qt.NoBrush)

    def _draw_objects(self, painter: QPainter, level: Level, force=False):
        level_rect = level.get_rect()
        blocks = self._get_objects(level, self._get_background(level), level_rect)
        pixmaps = self.get_blocks(level, force)
        self.render_blocks(painter, blocks, pixmaps, level_rect)

        for level_object in level.get_all_objects():
            if level_object.selected:
                painter.save()

                painter.setPen(QPen(QColor(0x00, 0x00, 0x00, 0x80), width=1))
                painter.drawRect(level_object.get_rect(self.block_length))

                painter.restore()
            if isinstance(level_object, LevelObjectController):
                continue
            level_object.render()
            level_object.draw(painter, self.block_length, self.transparency)

    def _draw_overlays(self, painter: QPainter, level: Level):
        painter.save()

        for level_object in level.get_all_objects():
            name = level_object.description.lower()

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
                if not get_setting("draw_jump_on_objects", True):
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

            elif "door" == name or "door (can go" in name or "invisible door" in name:
                fill_object = False

                image = DOWN_ARROW

                pos.setY(rect.top() - self.block_length)

                x, y = level_object.get_position()

                # jumps seemingly trigger on the bottom block
                if not self._object_in_jump_area(level, (x, y + 1)):
                    image = NO_JUMP

            # "?" - blocks, note blocks, wooden blocks and bricks
            elif "'?' with" in name or "brick with" in name or "bricks with" in name or "block with" in name:
                if not get_setting("draw_items_in_blocks", True):
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
                        painter.drawImage(adapted_pos, add_selection_graphic_to_image(image))

            else:
                image = image.scaled(self.block_length, self.block_length)
                painter.drawImage(pos, image)

        painter.restore()

    @staticmethod
    def _object_in_jump_area(level: Level, level_object: LevelObjectController):
        for jump in level.jumps:
            screen = jump.screen_index

            if level.is_vertical:
                rect = QRect(0, SCREEN_WIDTH * screen, SCREEN_WIDTH, SCREEN_HEIGHT, )
            else:
                rect = QRect(SCREEN_WIDTH * screen, 0, SCREEN_WIDTH, GROUND, )
            try:
                if rect.contains(QPoint(*level_object.get_position())):
                    return True
            except AttributeError:
                return False
        else:
            return False

    def _draw_expansions(self, painter: QPainter, level: Level):
        for level_object in level.get_all_objects():
            if level_object.selected:
                painter.drawRect(level_object.get_rect(self.block_length))

            if get_setting("draw_expansion", True):
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
