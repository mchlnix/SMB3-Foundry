from PySide2.QtCore import QPoint, QRect
from PySide2.QtGui import QBrush, QColor, QImage, QPainter, QPen, Qt

from foundry import data_dir
from foundry.game.File import ROM
from foundry.game.gfx.Palette import bg_color_for_object_set, load_palette
from foundry.game.gfx.PatternTable import PatternTable
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects.EnemyItem import MASK_COLOR
from foundry.game.gfx.objects.LevelObject import GROUND, LevelObject, SCREEN_HEIGHT, SCREEN_WIDTH
from foundry.game.gfx.objects.ObjectLike import EXPANDS_BOTH, EXPANDS_HORIZ, EXPANDS_VERT
from foundry.game.level.Level import Level


png = QImage(str(data_dir / "gfx.png"))
png.convertTo(QImage.Format_RGB888)


def _load_from_png(x: int, y: int):
    image = png.copy(QRect(x * 16, y * 16, 16, 16))
    mask = image.createMaskFromColor(QColor(*MASK_COLOR).rgb(), Qt.MaskOutColor)
    image.setAlphaChannel(mask)

    return image


NO_JUMP = _load_from_png(32, 53)
UP_ARROW = _load_from_png(33, 53)
DOWN_ARROW = _load_from_png(34, 53)
LEFT_ARROW = _load_from_png(35, 53)
RIGHT_ARROW = _load_from_png(36, 53)


class LevelDrawer:
    def __init__(self):
        self.draw_jumps = False
        self.draw_grid = False
        self.draw_expansions = False
        self.draw_mario = False
        self.draw_overlays = True
        self.transparency = False

        self.block_length = Block.WIDTH

        self.grid_pen = QPen(QColor(0x80, 0x80, 0x80, 0x80), width=1)
        self.screen_pen = QPen(QColor(0xFF, 0x00, 0x00, 0xFF), width=1)

    def draw(self, painter: QPainter, level: Level):
        self._draw_background(painter, level)

        if level.object_set_number == 9:  # desert
            self._draw_floor(painter, level)

        # painter.setPen(QPen(QColor(0x00, 0x00, 0x00, 0x80), width=1))
        # painter.setBrush(Qt.NoBrush)

        self._draw_objects(painter, level)

        if self.draw_overlays:
            self._draw_overlays(painter, level)

        if self.draw_expansions:
            self._draw_expansions(painter, level)

        if self.draw_mario:
            self._draw_mario(painter, level)

        if self.draw_grid:
            self._draw_grid(painter, level)

        if self.draw_jumps:
            self._draw_jumps(painter, level)

        if self.draw_grid:
            self._draw_grid(painter, level)

    def _draw_background(self, painter: QPainter, level: Level):
        painter.save()

        bg_color = bg_color_for_object_set(level.object_set_number, level.header.object_palette_index)

        painter.fillRect(level.get_rect(self.block_length), bg_color)

        painter.restore()

    def _draw_floor(self, painter: QPainter, level: Level):
        floor_level = (GROUND - 1) * self.block_length
        floor_block_index = 86

        palette_group = load_palette(level.object_set_number, level.header.object_palette_index)
        pattern_table = PatternTable(level.header.graphic_set_index)
        tsa_data = ROM().get_tsa_data(level.object_set_number)

        floor_block = Block(floor_block_index, palette_group, pattern_table, tsa_data)

        for x in range(level.width):
            floor_block.draw(painter, x * self.block_length, floor_level, self.block_length)

    def _draw_objects(self, painter: QPainter, level: Level):
        for level_object in level.get_all_objects():
            level_object.render()
            level_object.draw(painter, self.block_length, self.transparency)

    def _draw_overlays(self, painter: QPainter, level: Level):
        for level_object in level.get_all_objects():
            # pipe entries
            if "CAN go" in level_object.description:
                rect = level_object.get_rect(self.block_length)

                # center() is one pixel off for some reason
                pos = rect.topLeft() + QPoint(*(rect.size() / 2).toTuple())

                if "Left" in level_object.description:
                    image = LEFT_ARROW

                    pos.setX(rect.right())
                    pos.setY(pos.y() - self.block_length / 2)

                elif "Right" in level_object.description:
                    image = RIGHT_ARROW
                    pos.setX(rect.left() - self.block_length)
                    pos.setY(pos.y() - self.block_length / 2)

                elif "Down" in level_object.description:
                    image = DOWN_ARROW

                    pos.setX(pos.x() - self.block_length / 2)
                    pos.setY(rect.top() - self.block_length)
                else:
                    image = UP_ARROW

                    pos.setX(pos.x() - self.block_length / 2)
                    pos.setY(rect.bottom())

                if not self._object_in_jump_area(level, level_object):
                    image = NO_JUMP

                image = image.scaled(self.block_length, self.block_length)

                painter.drawImage(pos, image)

    @staticmethod
    def _object_in_jump_area(level: Level, level_object: LevelObject):
        for jump in level.jumps:
            screen = jump.screen_index

            if level.is_vertical:
                rect = QRect(0, SCREEN_WIDTH * screen, SCREEN_WIDTH, SCREEN_HEIGHT,)
            else:
                rect = QRect(SCREEN_WIDTH * screen, 0, SCREEN_WIDTH, GROUND,)

            if rect.contains(QPoint(*level_object.get_position())):
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

            screen = jump.screen_index

            if level.is_vertical:
                painter.drawRect(
                    0,
                    self.block_length * SCREEN_WIDTH * screen,
                    self.block_length * SCREEN_WIDTH,
                    self.block_length * SCREEN_HEIGHT,
                )
            else:
                painter.drawRect(
                    self.block_length * SCREEN_WIDTH * screen,
                    0,
                    self.block_length * SCREEN_WIDTH,
                    self.block_length * GROUND,
                )

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
                painter.drawLine(0, y, panel_width, y)
        else:
            for x in range(0, panel_width, self.block_length * SCREEN_WIDTH):
                painter.drawLine(x, 0, x, panel_height)
