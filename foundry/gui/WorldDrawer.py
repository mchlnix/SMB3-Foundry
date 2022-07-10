from PySide6.QtCore import QPoint, QRect, QSize
from PySide6.QtGui import QColor, QPainter, QPen, Qt

from foundry.game.gfx.drawable.Block import Block
from foundry.game.level.WorldMap import WorldMap
from smb3parse.levels import FIRST_VALID_ROW, WORLD_MAP_HEIGHT, WORLD_MAP_SCREEN_WIDTH, WORLD_MAP_WARP_WORLD_INDEX
from smb3parse.levels.data_points import AIRSHIP_TRAVEL_SET_COUNT


class WorldDrawer:
    def __init__(self):
        self.draw_level_pointers = True
        self.draw_sprites = True
        self.draw_start = True
        self.draw_airship_points = 0
        self.draw_pipes = True
        self.draw_locks = True

        self.block_length = Block.WIDTH

        self.grid_pen = QPen(QColor(0x80, 0x80, 0x80, 0x80), 1)
        self.screen_pen = QPen(QColor(0xFF, 0x00, 0x00, 0xFF), 1)

    def draw(self, painter: QPainter, world: WorldMap):
        painter.translate(0, -FIRST_VALID_ROW * self.block_length)

        self._draw_background(painter, world)

        self._draw_grid(painter, world)

        self._draw_tiles(painter, world)

        if self.draw_level_pointers:
            self._draw_level_pointers(painter, world)

        if self.draw_sprites:
            self._draw_sprites(painter, world)

        if self.draw_start:
            self._draw_start_position(painter, world)

        if self.draw_airship_points:
            self._draw_airship_travel_points(painter, world)

        self.draw_pipes = True
        self.draw_locks = True

    def _draw_background(self, painter: QPainter, world: WorldMap):
        bg_color = Qt.black

        painter.fillRect(world.get_rect(self.block_length), bg_color)

    def _draw_grid(self, painter: QPainter, world: WorldMap):
        painter.setPen(QPen(Qt.gray, 1))

        # rows
        map_length = WORLD_MAP_SCREEN_WIDTH * self.block_length * world.internal_world_map.screen_count

        for y in range(WORLD_MAP_HEIGHT):
            y *= self.block_length

            painter.drawLine(QPoint(0, y), QPoint(map_length, y))

        # columns
        for x in range(WORLD_MAP_SCREEN_WIDTH * world.internal_world_map.screen_count):
            x *= self.block_length

            painter.drawLine(QPoint(x, 0), QPoint(x, WORLD_MAP_SCREEN_WIDTH * self.block_length))

    def _draw_tiles(self, painter: QPainter, world: WorldMap):
        for tile in world.get_all_objects():
            tile.render()

            tile.draw(painter, self.block_length, False)

            if tile.selected:
                painter.setPen(QPen(QColor(0x00, 0x00, 0x00, 0x80), 1))
                painter.drawRect(tile.get_rect(self.block_length))

    def _draw_level_pointers(self, painter: QPainter, world: WorldMap):
        for index, level_pointer in enumerate(world.level_pointers):
            selected = index in world.selected_level_pointers

            level_pointer.draw(painter, self.block_length, False, selected)

    def _draw_sprites(self, painter: QPainter, world: WorldMap):
        for sprite in world.sprites:
            selected = sprite.data.index in world.selected_sprites

            sprite.draw(painter, self.block_length, False, selected)

    def _draw_start_position(self, painter: QPainter, world: WorldMap):
        start_pos = world.internal_world_map.start_pos

        if start_pos is None:
            return

        world, screen, y, x = start_pos.tuple()

        x *= self.block_length
        y *= self.block_length

        painter.fillRect(
            QRect(QPoint(x, y), QSize(self.block_length, self.block_length)), QColor(0x00, 0x00, 0xFF, 0x80)
        )

    def _draw_airship_travel_points(self, painter: QPainter, world: WorldMap):
        world_data = world.internal_world_map.data

        if world_data.index == WORLD_MAP_WARP_WORLD_INDEX:
            return

        for i in range(AIRSHIP_TRAVEL_SET_COUNT):
            if self.draw_airship_points & 2**i != 2**i:
                continue

            for airship_point in world.airship_travel_sets[i]:
                airship_point.draw(painter, self.block_length, False)
