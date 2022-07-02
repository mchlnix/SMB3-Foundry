from PySide6.QtCore import QPoint, QRect, QSize
from PySide6.QtGui import QColor, QPainter, QPen, Qt

from foundry.game.gfx.drawable import load_from_png
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects.LevelObject import SCREEN_HEIGHT, SCREEN_WIDTH
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
from smb3parse.levels import FIRST_VALID_ROW

EMPTY_IMAGE = load_from_png(0, 53)

MAP_OBJ_SPRITES = {
    MAPOBJ_EMPTY: EMPTY_IMAGE,
    MAPOBJ_HELP: load_from_png(43, 2),
    MAPOBJ_AIRSHIP: load_from_png(44, 2),
    MAPOBJ_HAMMERBRO: load_from_png(45, 2),
    MAPOBJ_BOOMERANGBRO: load_from_png(46, 2),
    MAPOBJ_HEAVYBRO: load_from_png(47, 2),
    MAPOBJ_FIREBRO: load_from_png(48, 2),
    MAPOBJ_W7PLANT: load_from_png(49, 2),
    MAPOBJ_UNK08: load_from_png(50, 2),
    MAPOBJ_NSPADE: load_from_png(51, 2),
    MAPOBJ_WHITETOADHOUSE: load_from_png(52, 2),
    MAPOBJ_COINSHIP: load_from_png(53, 2),
    MAPOBJ_UNK0C: load_from_png(54, 2),
    MAPOBJ_BATTLESHIP: load_from_png(55, 2),
    MAPOBJ_TANK: load_from_png(56, 2),
    MAPOBJ_W8AIRSHIP: load_from_png(57, 2),
    MAPOBJ_CANOE: load_from_png(58, 2),
}


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

        self._draw_grid(painter, world)

        self._draw_tiles(painter, world)

        if self.draw_level_pointers:
            # TODO: Fix and understand rules on where pointers can be
            self._draw_level_pointers(painter, world)

        if self.draw_sprites:
            self._draw_sprites(painter, world)

        if self.draw_start:
            self._draw_start_position(painter, world)

        self.draw_airship_points = True
        self.draw_pipes = True
        self.draw_locks = True

    def _draw_background(self, painter: QPainter, world: WorldMap):
        painter.save()

        bg_color = Qt.black

        painter.fillRect(world.get_rect(self.block_length), bg_color)

        painter.restore()

    def _draw_grid(self, painter: QPainter, world: WorldMap):
        painter.save()

        painter.setPen(QPen(Qt.gray, 1))

        # rows
        map_length = SCREEN_WIDTH * self.block_length * world.internal_world_map.screen_count

        for y in range(SCREEN_HEIGHT):
            y *= self.block_length

            painter.drawLine(QPoint(0, y), QPoint(map_length, y))

        # columns
        for x in range(SCREEN_WIDTH * world.internal_world_map.screen_count):
            x *= self.block_length

            painter.drawLine(QPoint(x, 0), QPoint(x, SCREEN_HEIGHT * self.block_length))

        painter.restore()

    def _draw_tiles(self, painter: QPainter, world: WorldMap):
        for tile in world.get_all_objects():
            tile.render()

            tile.draw(painter, self.block_length, False)

            if tile.selected:
                painter.save()

                painter.setPen(QPen(QColor(0x00, 0x00, 0x00, 0x80), 1))
                painter.drawRect(tile.get_rect(self.block_length))

                painter.restore()

    def _draw_level_pointers(self, painter: QPainter, world: WorldMap):
        painter.save()

        level_pointer_index = 0

        for lp in world.internal_world_map.gen_level_pointers():
            x = (lp.screen * SCREEN_WIDTH + lp.column) * self.block_length
            y = (lp.row - FIRST_VALID_ROW) * self.block_length

            if level_pointer_index in world.selected_level_pointers:
                painter.fillRect(QRect(x, y, self.block_length, self.block_length), QColor(0x00, 0xFF, 0x00, 0x80))

            painter.setPen(QPen(QColor(0xFF, 0x00, 0x00, 0x80), 4))

            painter.drawRect(x, y, self.block_length, self.block_length)

            level_pointer_index += 1

        painter.restore()

    def _draw_sprites(self, painter: QPainter, world: WorldMap):
        painter.save()

        for sprite in world.internal_world_map.gen_sprites():
            x = (sprite.screen * SCREEN_WIDTH + sprite.x) * self.block_length
            y = (sprite.y - FIRST_VALID_ROW) * self.block_length

            painter.setPen(QPen(QColor(0x00, 0x00, 0xFF, 0x80), 4))
            painter.drawImage(QPoint(x, y), MAP_OBJ_SPRITES[sprite.type].scaled(self.block_length, self.block_length))

            if sprite.index in world.selected_sprites:
                painter.fillRect(QRect(x, y, self.block_length, self.block_length), QColor(0x00, 0xFF, 0x00, 0x80))

        painter.restore()

    def _draw_start_position(self, painter: QPainter, world: WorldMap):
        painter.save()

        start_pos = world.internal_world_map.start_pos

        if start_pos is None:
            return

        world, screen, y, x = start_pos.tuple()

        x *= self.block_length
        y *= self.block_length

        painter.fillRect(
            QRect(QPoint(x, y), QSize(self.block_length, self.block_length)), QColor(0x00, 0x00, 0xFF, 0x80)
        )

        painter.restore()
