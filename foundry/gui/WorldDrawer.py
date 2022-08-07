from PySide6.QtCore import QPoint, QSize
from PySide6.QtGui import QColor, QPainter, QPen, Qt

from foundry.game.gfx.drawable import load_from_png
from foundry.game.gfx.drawable.Block import Block, get_worldmap_tile
from foundry.game.gfx.objects import MapTile
from foundry.game.level.WorldMap import WorldMap
from foundry.gui.settings import Settings
from foundry.gui.util import partition
from smb3parse.constants import AIRSHIP_TRAVEL_SET_COUNT
from smb3parse.levels import (
    FIRST_VALID_ROW,
    WORLD_MAP_BLANK_TILE_ID,
    WORLD_MAP_BORDER_TOP_TILE_ID,
    WORLD_MAP_HEIGHT,
    WORLD_MAP_SCREEN_WIDTH,
    WORLD_MAP_WARP_WORLD_INDEX,
)


BORDER_UL = load_from_png(61, 3)
BORDER_UR = BORDER_UL.mirrored(True, False)
BORDER_BR = load_from_png(63, 3)
BORDER_BL = BORDER_BR.mirrored(True, False)

BORDER_SIDE_L = load_from_png(62, 3)
BORDER_SIDE_R = BORDER_SIDE_L.mirrored(True, False)


class WorldDrawer:
    def __init__(self):
        self.block_length = Block.WIDTH

        self.grid_pen = QPen(QColor(0x80, 0x80, 0x80, 0x80), 1)
        self.screen_pen = QPen(QColor(0xFF, 0x00, 0x00, 0xFF), 1)

        self.settings = Settings("mchlnix", "world drawer")

        self.anim_frame = 0

    def draw(self, painter: QPainter, world: WorldMap):
        painter.save()

        self._draw_background(painter, world)

        if not self.settings.value("world view/show border"):
            painter.translate(0, -FIRST_VALID_ROW * self.block_length)

        self._draw_tiles(painter, world)

        if self.settings.value("world view/show border"):
            self._draw_border(painter, world)

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

        map_height = WORLD_MAP_HEIGHT

        if self.settings.value("world view/show border"):
            y_offset = 0
            map_height += 3
        else:
            y_offset = FIRST_VALID_ROW
            map_height += y_offset

        # rows
        map_length = WORLD_MAP_SCREEN_WIDTH * self.block_length * world.data.screen_count

        for y in range(map_height):
            y += y_offset
            y *= self.block_length

            painter.drawLine(QPoint(0, y), QPoint(map_length, y))

        # columns
        for x in range(WORLD_MAP_SCREEN_WIDTH * world.data.screen_count):
            x *= self.block_length

            painter.drawLine(QPoint(x, y_offset), QPoint(x, map_height * self.block_length))

        painter.setPen(QPen(QColor(0xFF, 0x00, 0x00, 0xFF), 3))

        for i in range(1, world.data.screen_count):
            x = i * WORLD_MAP_SCREEN_WIDTH * self.block_length

            painter.drawLine(QPoint(x, 0), QPoint(x, map_height * self.block_length))

    def _draw_tiles(self, painter: QPainter, world: WorldMap):
        not_selected, selected = partition(lambda tile_: tile_.selected, world.get_all_objects())

        for tile in not_selected:
            self._draw_tile(painter, world, tile)

        for tile in selected:
            self._draw_tile(painter, world, tile)

            painter.setPen(QPen(QColor(0x00, 0x00, 0x00, 0x80), 1))
            painter.drawRect(tile.get_rect(self.block_length))

        # TODO make anim frame a parameter to draw and Tile()
        tile.block.graphics_set.anim_frame = self.anim_frame

    def _draw_tile(self, painter: QPainter, world: WorldMap, tile: MapTile):
        # both exceptions are hard coded and don't animate
        if world.data.index == 4 or (world.data.index == 7 and tile.pos.screen == 3):
            tile.draw(painter, self.block_length, anim_frame=0)
        else:
            tile.draw(painter, self.block_length, anim_frame=self.anim_frame)

    def _draw_border(self, painter: QPainter, world: WorldMap):
        # side borders
        x_left = 0
        x_right = (world.width - 1) * self.block_length

        border_side_l = BORDER_SIDE_L.scaled(QSize(self.block_length, self.block_length), Qt.KeepAspectRatio)
        border_side_r = BORDER_SIDE_R.scaled(QSize(self.block_length, self.block_length), Qt.KeepAspectRatio)

        for y in range(WORLD_MAP_HEIGHT + 3):
            painter.drawImage(x_left, y * self.block_length, border_side_l)
            painter.drawImage(x_right, y * self.block_length, border_side_r)

        # top border
        y_first_row = 0
        y_second_row = self.block_length

        blank_tile = get_worldmap_tile(WORLD_MAP_BLANK_TILE_ID, world.data.palette_index)
        border_top = get_worldmap_tile(WORLD_MAP_BORDER_TOP_TILE_ID, world.data.palette_index)

        for x in range(world.width):
            blank_tile.draw(painter, x * self.block_length, y_first_row, self.block_length)
            border_top.draw(painter, x * self.block_length, y_second_row, self.block_length)

        # bottom border
        y_last_row = (WORLD_MAP_HEIGHT + 3 - 1) * self.block_length

        bottom_border = get_worldmap_tile(world.data.bottom_border_tile, world.data.palette_index)

        for x in range(world.width):
            bottom_border.draw(painter, x * self.block_length, y_last_row, self.block_length)

        # border corners
        border_ul = BORDER_UL.scaled(QSize(self.block_length, self.block_length), Qt.KeepAspectRatio)
        border_ur = BORDER_UR.scaled(QSize(self.block_length, self.block_length), Qt.KeepAspectRatio)
        border_bl = BORDER_BL.scaled(QSize(self.block_length, self.block_length), Qt.KeepAspectRatio)
        border_br = BORDER_BR.scaled(QSize(self.block_length, self.block_length), Qt.KeepAspectRatio)

        painter.drawImage(x_left, y_second_row, border_ul)
        painter.drawImage(x_right, y_second_row, border_ur)
        painter.drawImage(x_left, y_last_row, border_bl)
        painter.drawImage(x_right, y_last_row, border_br)

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
            lock_object.draw(painter, self.block_length, False, lock_object.selected)
