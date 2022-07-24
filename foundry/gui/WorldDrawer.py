from PySide6.QtCore import QPoint
from PySide6.QtGui import QColor, QPainter, QPen, Qt

from foundry.game.gfx.drawable.Block import Block
from foundry.game.level.WorldMap import WorldMap
from foundry.gui.settings import Settings
from foundry.gui.util import partition
from smb3parse.constants import AIRSHIP_TRAVEL_SET_COUNT
from smb3parse.levels import FIRST_VALID_ROW, WORLD_MAP_HEIGHT, WORLD_MAP_SCREEN_WIDTH, WORLD_MAP_WARP_WORLD_INDEX


class WorldDrawer:
    def __init__(self):
        self.block_length = Block.WIDTH

        self.grid_pen = QPen(QColor(0x80, 0x80, 0x80, 0x80), 1)
        self.screen_pen = QPen(QColor(0xFF, 0x00, 0x00, 0xFF), 1)

        self.settings = Settings("mchlnix", "world drawer")

    def draw(self, painter: QPainter, world: WorldMap):
        painter.save()

        self._draw_background(painter, world)

        painter.translate(0, -FIRST_VALID_ROW * self.block_length)

        self._draw_tiles(painter, world)

        if self.settings.value("world view/show grid"):
            self._draw_grid(painter, world)

        if self.settings.value("world view/show level pointers"):
            self._draw_level_pointers(painter, world)

        if self.settings.value("world view/show sprites"):
            self._draw_sprites(painter, world)

        if self.settings.value("world view/show start position"):
            self._draw_start_position(painter, world)

        if self.settings.value("world view/show airship paths"):
            self._draw_airship_travel_points(painter, world)

        # self.draw_pipes = True

        if self.settings.value("world view/show locks"):
            self._draw_locks_and_bridges(painter, world)

        painter.restore()

    def _draw_background(self, painter: QPainter, world: WorldMap):
        bg_color = Qt.black

        painter.fillRect(world.get_rect(self.block_length), bg_color)

    def _draw_grid(self, painter: QPainter, world: WorldMap):
        painter.setPen(QPen(Qt.gray, 1))

        # rows
        map_length = WORLD_MAP_SCREEN_WIDTH * self.block_length * world.data.screen_count

        for y in range(WORLD_MAP_HEIGHT):
            y += FIRST_VALID_ROW
            y *= self.block_length

            painter.drawLine(QPoint(0, y), QPoint(map_length, y))

        # columns
        for x in range(WORLD_MAP_SCREEN_WIDTH * world.data.screen_count):
            x *= self.block_length

            painter.drawLine(QPoint(x, 0), QPoint(x, (WORLD_MAP_HEIGHT + FIRST_VALID_ROW) * self.block_length))

    def _draw_tiles(self, painter: QPainter, world: WorldMap):
        not_selected, selected = partition(lambda tile_: tile_.selected, world.get_all_objects())

        for tile in not_selected:
            tile.draw(painter, self.block_length, False)

        for tile in selected:
            tile.draw(painter, self.block_length, False)

            painter.setPen(QPen(QColor(0x00, 0x00, 0x00, 0x80), 1))
            painter.drawRect(tile.get_rect(self.block_length))

    def _draw_level_pointers(self, painter: QPainter, world: WorldMap):
        for index, level_pointer in enumerate(world.level_pointers):
            level_pointer.draw(painter, self.block_length, False, level_pointer.selected)

    def _draw_sprites(self, painter: QPainter, world: WorldMap):
        for sprite in world.sprites:
            sprite.draw(painter, self.block_length, False, sprite.selected)

    def _draw_start_position(self, painter: QPainter, world: WorldMap):
        world.start_pos.draw(painter, self.block_length, False)

    def _draw_airship_travel_points(self, painter: QPainter, world: WorldMap):
        if world.data.index == WORLD_MAP_WARP_WORLD_INDEX:
            return

        for i in range(AIRSHIP_TRAVEL_SET_COUNT):
            if self.settings.value("world view/show airship paths") & 2**i != 2**i:
                continue

            for airship_point in world.airship_travel_sets[i]:
                airship_point.draw(painter, self.block_length, False)

    def _draw_locks_and_bridges(self, painter: QPainter, world: WorldMap):
        if world.data.index == WORLD_MAP_WARP_WORLD_INDEX:
            return

        for lock_object in world.locks_and_bridges:
            lock_object.draw(painter, self.block_length, False)
