from itertools import product

from PySide6.QtCore import QPoint, QRect
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, Qt

from foundry.game import EXPANDS_BOTH, EXPANDS_HORIZ, EXPANDS_VERT, GROUND
from foundry.game.File import ROM
from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx.Palette import (
    NESPalette,
    bg_color_for_object_set,
    load_palette_group,
)
from foundry.game.gfx.drawable import load_from_png, make_image_selected, mario_actions
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects import (
    EnemyItem,
    LevelObject,
)
from foundry.game.gfx.objects.world_map.sprite import EMPTY_IMAGE
from foundry.game.level.Level import Level
from foundry.gui.AutoScrollDrawer import AutoScrollDrawer
from foundry.gui.settings import Settings
from smb3parse.constants import (
    OBJ_AUTOSCROLL,
    OBJ_CHEST_EXIT,
    OBJ_CHEST_ITEM_SETTER,
    OBJ_PIPE_EXITS,
)
from smb3parse.levels import (
    LEVEL_MAX_LENGTH,
    LEVEL_SCREEN_HEIGHT,
    LEVEL_SCREEN_WIDTH,
)
from smb3parse.objects.object_set import (
    CLOUDY_OBJECT_SET,
    DESERT_OBJECT_SET,
    DUNGEON_OBJECT_SET,
    ICE_OBJECT_SET,
)

FIRE_FLOWER = load_from_png(16, 53)
LEAF = load_from_png(17, 53)
NORMAL_STAR = load_from_png(18, 53)
CONTINUOUS_STAR = load_from_png(19, 53)
MULTI_COIN = load_from_png(20, 53)
ONE_UP = load_from_png(21, 53)
COIN = load_from_png(22, 53)
VINE = load_from_png(23, 53)
P_SWITCH = load_from_png(24, 53)
SILVER_COIN = load_from_png(25, 53)
INVISIBLE_COIN = load_from_png(26, 53)
INVISIBLE_1_UP = load_from_png(27, 53)

NO_JUMP = load_from_png(32, 53)
UP_ARROW = load_from_png(33, 53)
DOWN_ARROW = load_from_png(34, 53)
LEFT_ARROW = load_from_png(35, 53)
RIGHT_ARROW = load_from_png(36, 53)

ITEM_ARROW = load_from_png(53, 53)


SPECIAL_BACKGROUND_OBJECTS = [
    "blue background",
    "starry background",
    "underground background under this",
    "sets background to actual background color",
]


OMITTED_ITEMS = [OBJ_PIPE_EXITS, OBJ_CHEST_EXIT, OBJ_CHEST_ITEM_SETTER]
"""
These configure things based on their y-position in the level. This is done in the editor directly now. So no need to
actually render them in the level.
"""


def _block_from_index(block_index: int, level: Level) -> Block:
    """
    Returns the block at the given index, from the TSA table for the given level.

    :param block_index:
    :param level:
    :return:
    """

    palette_group = load_palette_group(level.object_set_number, level.header.object_palette_index)
    graphics_set = GraphicsSet.from_number(level.header.graphic_set_index)
    tsa_data = ROM.get_tsa_data(level.object_set_number)

    return Block(block_index, palette_group, graphics_set, tsa_data)


class LevelDrawer:
    def __init__(self):
        self.block_length = Block.WIDTH

        self.grid_pen = QPen(QColor(0x80, 0x80, 0x80, 0x80), 1)
        self.screen_pen = QPen(QColor(0xFF, 0x00, 0x00, 0xFF), 1)

        self.settings = Settings("mchlnix", "level drawer")
        self.anim_frame = 0

    def draw(self, painter: QPainter, level: Level):
        self._draw_background(painter, level)

        if self.settings.value("level view/special_background"):
            if level.object_set.number == DESERT_OBJECT_SET:
                self._draw_desert_default_graphics(painter, level)

            elif level.object_set.number == DUNGEON_OBJECT_SET:
                self._draw_dungeon_default_graphics(painter, level)

            elif level.object_set.number == ICE_OBJECT_SET:
                self._draw_ice_default_graphics(painter, level)

        self._draw_objects(painter, level)

        self._draw_overlays(painter, level)

        if self.settings.value("level view/draw_expansion"):
            self._draw_expansions(painter, level)

        if self.settings.value("level view/draw_mario"):
            self._draw_mario(painter, level)

        if self.settings.value("level view/draw_jumps"):
            self._draw_jumps(painter, level)

        if self.settings.value("level view/draw_grid"):
            self._draw_grid(painter, level)

        if self.settings.value("level view/draw_autoscroll"):
            self._draw_auto_scroll(painter, level)

    def _draw_background(self, painter: QPainter, level: Level):
        painter.save()

        if level.object_set.number == CLOUDY_OBJECT_SET:
            bg_color = NESPalette[load_palette_group(level.object_set_number, level.header.object_palette_index)[3][2]]
        else:
            bg_color = bg_color_for_object_set(level.object_set_number, level.header.object_palette_index)

        painter.fillRect(level.get_rect(self.block_length), bg_color)

        painter.restore()

    def _draw_dungeon_default_graphics(self, painter: QPainter, level: Level):
        # draw_background
        bg_block = _block_from_index(140, level)

        for x, y in product(range(level.width), range(level.height)):
            bg_block.graphics_set.anim_frame = self.anim_frame
            bg_block.draw(painter, x * self.block_length, y * self.block_length, self.block_length)

        # draw ceiling
        ceiling_block = _block_from_index(139, level)

        for x in range(level.width):
            ceiling_block.graphics_set.anim_frame = self.anim_frame
            ceiling_block.draw(painter, x * self.block_length, 0, self.block_length)

        # draw floor
        upper_floor_blocks = [
            _block_from_index(20, level),
            _block_from_index(21, level),
        ]
        lower_floor_blocks = [
            _block_from_index(22, level),
            _block_from_index(23, level),
        ]

        upper_y = (GROUND - 2) * self.block_length
        lower_y = (GROUND - 1) * self.block_length

        for block_x in range(level.width):
            pixel_x = block_x * self.block_length

            upper_floor_blocks[block_x % 2].draw(painter, pixel_x, upper_y, self.block_length)
            upper_floor_blocks[block_x % 2].graphics_set.anim_frame = self.anim_frame
            lower_floor_blocks[block_x % 2].draw(painter, pixel_x, lower_y, self.block_length)
            lower_floor_blocks[block_x % 2].graphics_set.anim_frame = self.anim_frame

    def _draw_desert_default_graphics(self, painter: QPainter, level: Level):
        floor_level = (GROUND - 1) * self.block_length
        floor_block_index = 86

        floor_block = _block_from_index(floor_block_index, level)

        for x in range(level.width):
            floor_block.graphics_set.anim_frame = self.anim_frame
            floor_block.draw(painter, x * self.block_length, floor_level, self.block_length)

    def _draw_ice_default_graphics(self, painter: QPainter, level: Level):
        bg_block = _block_from_index(0x80, level)

        for x, y in product(range(level.width), range(level.height)):
            bg_block.graphics_set.anim_frame = self.anim_frame
            bg_block.draw(painter, x * self.block_length, y * self.block_length, self.block_length)

    def _draw_objects(self, painter: QPainter, level: Level):
        for level_object in level.get_all_objects():
            if isinstance(level_object, EnemyItem) and level_object.type in OMITTED_ITEMS:
                continue

            level_object.render()

            if level_object.name.lower() in SPECIAL_BACKGROUND_OBJECTS:
                assert isinstance(level_object, LevelObject)

                width = LEVEL_MAX_LENGTH
                height = GROUND - level_object.y_position

                blocks_to_draw = [level_object.blocks[0]] * width * height

                for index, block_index in enumerate(blocks_to_draw):
                    x = level_object.x_position + index % width
                    y = level_object.y_position + index // width

                    level_object._draw_block(painter, block_index, x, y, self.block_length, False)
            else:
                level_object.anim_frame = self.anim_frame
                level_object.draw(
                    painter,
                    self.block_length,
                    self.settings.value("level view/block_transparency"),
                )

            if level_object.selected:
                painter.save()

                painter.setPen(QPen(QColor(0x00, 0x00, 0x00, 0x80), 1))
                painter.drawRect(level_object.get_rect(self.block_length))

                painter.restore()

    def _draw_overlays(self, painter: QPainter, level: Level):
        painter.save()

        for level_object in level.get_all_objects():
            name = level_object.name.lower()

            # only handle this specific enemy item for now
            if isinstance(level_object, EnemyItem) and "invisible door" not in name:
                continue

            pos = level_object.get_rect(self.block_length).topLeft()
            rect = level_object.get_rect(self.block_length)

            # invisible coins, for example, expand and need to have multiple overlays drawn onto them
            # set true by default, since for most overlays it doesn't matter
            fill_object = True

            # pipe entries
            if "pipe" in name and "can go" in name:
                if not self.settings.value("level view/draw_jump_on_objects"):
                    continue

                fill_object = False

                # center() is one pixel off for some reason
                pos = rect.topLeft() + QPoint(rect.width() // 2, rect.height() // 2)

                trigger_position = level_object.get_position()

                if "left" in name:
                    image = LEFT_ARROW

                    pos.setX(rect.right())
                    pos.setY(pos.y() - self.block_length / 2)

                    # leftward pipes trigger on the column to the left of the opening
                    x = level_object.get_rect().bottomRight().x()
                    y = level_object.get_rect().bottomRight().y()
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
                    x = level_object.get_rect().bottomLeft().x()
                    y = level_object.get_rect().bottomLeft().y()
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
                if not self.settings.value("level view/draw_items_in_blocks"):
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
                if not self.settings.value("level view/draw_invisible_items"):
                    continue

                if "coin" in name:
                    image = INVISIBLE_COIN
                elif "1-up" in name:
                    image = INVISIBLE_1_UP
                else:
                    image = EMPTY_IMAGE

            elif "silver coins" in name:
                if not self.settings.value("level view/draw_invisible_items"):
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
                        painter.drawImage(adapted_pos, make_image_selected(image))

            else:
                image = image.scaled(self.block_length, self.block_length)
                painter.drawImage(pos, image)

        painter.restore()

    @staticmethod
    def _object_in_jump_area(level: Level, pos: tuple[int, int]):
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

            if self.settings.value("level view/draw_expansion"):
                painter.save()

                painter.setPen(Qt.PenStyle.NoPen)

                if level_object.expands() == EXPANDS_BOTH:
                    painter.setBrush(QColor(0xFF, 0, 0xFF, 0x80))
                elif level_object.expands() == EXPANDS_HORIZ:
                    painter.setBrush(QColor(0xFF, 0, 0, 0x80))
                elif level_object.expands() == EXPANDS_VERT:
                    painter.setBrush(QColor(0, 0, 0xFF, 0x80))

                painter.drawRect(level_object.get_rect(self.block_length))

                painter.restore()

    def _draw_mario(self, painter: QPainter, level: Level):
        mario_position = QPoint(*level.header.mario_position()) * self.block_length

        x_offset = 32 * level.start_action

        mario_cutout = mario_actions.copy(QRect(x_offset, 0, 32, 32)).scaled(
            2 * self.block_length, 2 * self.block_length
        )

        painter.drawImage(mario_position, mario_cutout)

    def _draw_jumps(self, painter: QPainter, level: Level):
        for jump in level.jumps:
            painter.setBrush(QBrush(QColor(0xFF, 0x00, 0x00), Qt.BrushStyle.FDiagPattern))

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
            for y in range(0, panel_height, self.block_length * LEVEL_SCREEN_HEIGHT):
                painter.drawLine(0, self.block_length + y, panel_width, self.block_length + y)
        else:
            for x in range(0, panel_width, self.block_length * LEVEL_SCREEN_WIDTH):
                painter.drawLine(x, 0, x, panel_height)

    def _draw_auto_scroll(self, painter: QPainter, level: Level):
        for item in level.enemies:
            if item.obj_index == OBJ_AUTOSCROLL:
                break
        else:
            return

        drawer = AutoScrollDrawer(item.auto_scroll_type, level)

        drawer.draw(painter, self.block_length)
