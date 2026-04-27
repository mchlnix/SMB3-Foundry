"""Paint SMB3 world-map model data into the editor's world view.

This module owns :class:`WorldDrawer`, the Qt-facing renderer that converts a
loaded :class:`foundry.game.level.WorldMap.WorldMap` into the layered preview
shown by the world editor. It consumes world-map model objects, visibility
flags from :class:`foundry.gui.settings.Settings`, and cached SMB3 graphics,
then emits background, tile, and overlay passes into a supplied
``QPainter``.

The helper methods mirror the world-view paint order so maintainers can trace
how map state becomes editor pixels, from the background clear through
selection overlays and special-case travel objects. For interaction logic and
viewport hosting, read
:mod:`foundry.gui.visualization.world.WorldView` next.

See Also
--------
foundry.gui.visualization.world.WorldView
    Widget that hosts this drawer inside the world editor.
foundry.game.level.WorldMap
    World-map model consumed by the drawer.
"""

from PySide6.QtCore import QPoint, QRect, QSize
from PySide6.QtGui import QColor, QPainter, QPen, Qt

from foundry.game.gfx.block_cache import get_worldmap_tile
from foundry.game.gfx.drawable import load_from_object_sprite_sheet
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects.world_map.map_tile import MapTile
from foundry.game.level.WorldMap import WorldMap
from foundry.gui.settings import Settings
from foundry.gui.util import partition
from smb3parse.constants import AIRSHIP_TRAVEL_SET_COUNT
from smb3parse.levels import (
    FIRST_VALID_ROW,
    NO_MAP_SCROLLING,
    WORLD_MAP_BLANK_TILE_ID,
    WORLD_MAP_BORDER_TOP_TILE_ID,
    WORLD_MAP_HEIGHT,
    WORLD_MAP_SCREEN_WIDTH,
    WORLD_MAP_WARP_WORLD_INDEX,
)

BORDER_CORNER_TL = load_from_object_sprite_sheet(61, 3)
BORDER_CORNER_TR = BORDER_CORNER_TL.mirrored(True, False)
BORDER_CORNER_BR = load_from_object_sprite_sheet(63, 3)
BORDER_CORNER_BL = BORDER_CORNER_BR.mirrored(True, False)

BORDER_SIDE_L = load_from_object_sprite_sheet(62, 3)
BORDER_SIDE_R = BORDER_SIDE_L.mirrored(True, False)


class WorldDrawer:
    """Render SMB3 world-map layers into a Qt painter.

    The drawer paints map tiles first, then optional editor overlays such as
    borders, grid/screen dividers, level pointers, sprites, start positions,
    airship paths, locks, and bridges. Layer visibility is read from settings.

    Attributes
    ----------
    anim_frame : int
        Current animation frame for animated map tiles.
    block_length : int
        Rendered pixel size of one world-map tile.
    grid_pen : QPen
        Pen used for grid lines.
    screen_pen : QPen
        Pen used for screen boundary overlays.
    settings : Settings
        Drawing settings for optional world-map layers.
    should_draw_potential_marios : bool
        Reserved flag for drawing possible start positions.
    """

    def __init__(self):
        """Create the world-map drawer with default pens and settings.

        The drawer keeps all world-view paint configuration in one place so a
        caller only needs to supply a painter and a loaded
        :class:`~foundry.game.level.WorldMap.WorldMap`. The settings instance
        controls which overlay passes are enabled, while the pens and block
        size establish the shared coordinate system used by every helper draw
        stage.
        """
        self.block_length = Block.WIDTH

        self.grid_pen = QPen(QColor(0x80, 0x80, 0x80, 0x80), 1)
        self.screen_pen = QPen(QColor(0xFF, 0x00, 0x00, 0xFF), 1)

        self.settings = Settings("mchlnix", "world drawer")

        self.anim_frame = 0

        self.should_draw_potential_marios = False

    def draw(self, painter: QPainter, world: WorldMap):
        """Draw all enabled world-map layers.

        This is the entry point used by the world view during repaint. It
        stages the render as a stable pipeline: clear the viewport, align the
        painter for optional border rows, paint base tiles, then add any
        editor overlays that are enabled in settings. The method only mutates
        painter state for the duration of the paint call, leaving the world
        model untouched while turning ``WorldMap`` collections and settings
        flags into one ordered screen image.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        world : WorldMap
            World map or world number being processed.
        """
        painter.save()

        self._draw_background(painter, world)

        if not self.settings.value("world_view/show_border"):
            painter.translate(0, -FIRST_VALID_ROW * self.block_length)

        self._draw_tiles(painter, world)

        if self.settings.value("world_view/show_border"):
            self._draw_border(painter, world)

        if self.settings.value("world_view/show_grid"):
            self._draw_grid(painter, world)

        if self.settings.value("world_view/show_level_pointers"):
            self._draw_level_pointers(painter, world)

        if self.settings.value("world_view/show_sprites"):
            self._draw_sprites(painter, world)

        if self.settings.value("world_view/show_start_position"):
            self._draw_start_position(painter, world)

        if self.settings.value("world_view/show_airship_paths"):
            self._draw_airship_travel_points(painter, world)

        # self.draw_pipes = True

        if self.settings.value("world_view/show_locks"):
            self._draw_locks_and_bridges(painter, world)

        painter.restore()

    def _draw_background(self, painter: QPainter, world: WorldMap):
        """Fill the world-map bounds with the background color.

        The background pass establishes a known black backing rectangle before
        any tiles or overlays are drawn. Later passes rely on this fill to
        keep partially transparent grid, border, and selection layers readable
        against empty map space. The fill uses the world model's computed
        bounds so every later helper paints into the same world-space rectangle
        that this pass initializes on the painter, making the background the
        first committed geometry in the world-view paint cycle.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        world : WorldMap
            World map or world number being processed.
        """
        bg_color = Qt.GlobalColor.black

        painter.fillRect(world.get_rect(self.block_length), bg_color)

    def _draw_grid(self, painter: QPainter, world: WorldMap):
        """Draw tile grid lines and screen-scroll dividers.

        This overlay translates world geometry into editor measurement cues.
        It expands or shifts the row range to match whether the decorative
        border rows are visible, then colors screen dividers to reflect whether
        the loaded world allows horizontal scrolling between screens. The
        resulting lines reuse world screen counts and tile size so selection
        and placement tools can read the same visual grid the model uses, with
        border visibility and scroll metadata both folded into the final
        painter coordinates.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        world : WorldMap
            World map or world number being processed.
        """
        painter.setPen(QPen(Qt.GlobalColor.gray, 1))

        map_height = WORLD_MAP_HEIGHT

        if self.settings.value("world_view/show_border"):
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

        # TODO seems like map scroll could deactivate scrolling partly, so this could be more fine grained
        # make screen divider red for no scrolling and green for scrolling
        if world.data.map_scroll in [0x0, NO_MAP_SCROLLING]:
            painter.setPen(QPen(QColor(0xFF, 0x00, 0x00, 0xFF), 3))
        else:
            painter.setPen(QPen(QColor(0x00, 0xFF, 0x00, 0xFF), 3))

        for i in range(1, world.data.screen_count):
            x = i * WORLD_MAP_SCREEN_WIDTH * self.block_length

            painter.drawLine(QPoint(x, 0), QPoint(x, map_height * self.block_length))

    def _draw_tiles(self, painter: QPainter, world: WorldMap):
        """Draw map tiles with selected tiles painted last.

        The tile pass preserves editor feedback by painting unselected tiles
        first and selected tiles last, then outlining those selected entries on
        top of the finished tile image. It also updates the shared tile
        animation frame after the pass so subsequent paint cycles reuse the
        same timing state.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        world : WorldMap
            World map or world number being processed.
        """
        if not world.get_all_objects():
            return

        not_selected, selected = partition(lambda tile_: tile_.selected, world.get_all_objects())

        for tile in not_selected:
            self._draw_tile(painter, world, tile)

        for tile in selected:
            self._draw_tile(painter, world, tile)

            painter.setPen(QPen(QColor(0x00, 0x00, 0x00, 0x80), 1))
            painter.drawRect(QRect(*tile.get_rect(self.block_length)))

        # TODO make anim frame a parameter to draw and Tile()
        tile.block.graphics_set.anim_frame = self.anim_frame

    def _draw_tile(self, painter: QPainter, world: WorldMap, tile: MapTile):
        # both exceptions are hard coded and don't animate
        """Draw one map tile with world-specific animation exceptions.

        Most tiles use the drawer's active animation frame, but SMB3 has hard
        coded world-specific exceptions that stay static. This helper keeps
        those animation boundaries localized so the outer tile loop can treat
        every map object the same way while still handing each ``MapTile`` the
        exact animation frame that should be committed to the painter.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        world : WorldMap
            World map or world number being processed.
        tile : MapTile
            Map tile to draw.
        """
        if world.data.index == 4 or (world.data.index == 7 and tile.pos.screen == 3):
            tile.draw(painter, self.block_length, anim_frame=0)
        else:
            tile.draw(painter, self.block_length, anim_frame=self.anim_frame)

    def _draw_border(self, painter: QPainter, world: WorldMap):
        # side borders
        """Draw SMB3-style world-map border tiles.

        The border pass reconstructs the decorative frame that SMB3 places
        around visible world-map rows. It paints side rails, top and bottom
        filler rows, and the four corners in separate stages so the editor can
        show or hide the border independently from the logical map data while
        keeping tile coordinates aligned with the main tile pass. Those stages
        mirror the border assets SMB3 stores separately from map tiles: side
        images first, row-filling tiles next, then corner caps that close the
        frame without disturbing the world-space origin used by overlays. That
        staging lets the view toggle the decorative frame on and off without
        changing how later overlay helpers interpret map coordinates.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        world : WorldMap
            World map or world number being processed.
        """
        x_left = 0
        x_right = (world.width - 1) * self.block_length

        border_side_l = BORDER_SIDE_L.scaled(
            QSize(self.block_length, self.block_length),
            Qt.AspectRatioMode.KeepAspectRatio,
        )
        border_side_r = BORDER_SIDE_R.scaled(
            QSize(self.block_length, self.block_length),
            Qt.AspectRatioMode.KeepAspectRatio,
        )

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
        border_ul = BORDER_CORNER_TL.scaled(
            QSize(self.block_length, self.block_length),
            Qt.AspectRatioMode.KeepAspectRatio,
        )
        border_ur = BORDER_CORNER_TR.scaled(
            QSize(self.block_length, self.block_length),
            Qt.AspectRatioMode.KeepAspectRatio,
        )
        border_bl = BORDER_CORNER_BL.scaled(
            QSize(self.block_length, self.block_length),
            Qt.AspectRatioMode.KeepAspectRatio,
        )
        border_br = BORDER_CORNER_BR.scaled(
            QSize(self.block_length, self.block_length),
            Qt.AspectRatioMode.KeepAspectRatio,
        )

        painter.drawImage(x_left, y_second_row, border_ul)
        painter.drawImage(x_right, y_second_row, border_ur)
        painter.drawImage(x_left, y_last_row, border_bl)
        painter.drawImage(x_right, y_last_row, border_br)

    def _draw_level_pointers(self, painter: QPainter, world: WorldMap):
        """Draw enterable level pointer objects.

        Level pointers are painted after the base tiles so their interactive
        markers remain visible above the map art. Selection state is forwarded
        unchanged to preserve the same highlight semantics used elsewhere in
        the world editor.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        world : WorldMap
            World map or world number being processed.
        """
        for level_pointer in world.level_pointers:
            level_pointer.draw(painter, self.block_length, False, level_pointer.selected)

    def _draw_sprites(self, painter: QPainter, world: WorldMap):
        """Draw world-map sprite objects.

        This overlay paints roaming or event-driven world sprites after tiles
        and before other helper overlays so the editor reflects the sprite set
        embedded in the loaded world model without changing sprite ordering in
        the data itself. Each sprite is forwarded directly from
        ``world.sprites`` into the painter, preserving the model's current
        selection state and draw order for the frame.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        world : WorldMap
            World map or world number being processed.
        """
        for sprite in world.sprites:
            sprite.draw(painter, self.block_length, False, sprite.selected)

    def _draw_start_position(self, painter: QPainter, world: WorldMap):
        """Draw the Mario start position marker.

        The start marker is rendered as its own pass so settings can toggle it
        independently from other overlays while still using the same world-map
        coordinate system established by the base tile render.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        world : WorldMap
            World map or world number being processed.
        """
        world.start_pos.draw(painter, self.block_length, False)

    def _draw_airship_travel_points(self, painter: QPainter, world: WorldMap):
        """Draw enabled airship travel paths for non-warp worlds.

        Airship travel points are grouped into bitflag-controlled travel sets.
        This pass skips the warp world entirely, then filters each set through
        the user's visibility flags before drawing the corresponding path nodes
        on top of the base map. That keeps the overlay synchronized with both
        the loaded world data and the editor's per-travel-set visibility mask,
        so the painter only receives nodes from enabled travel sets in worlds
        that actually support airship routing, and it commits those nodes only
        after tile rendering has established the map surface beneath them.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        world : WorldMap
            World map or world number being processed.
        """
        if world.data.index == WORLD_MAP_WARP_WORLD_INDEX:
            return

        for i in range(AIRSHIP_TRAVEL_SET_COUNT):
            if self.settings.value("world_view/show_airship_paths") & 2**i != 2**i:
                continue

            for airship_point in world.airship_travel_sets[i]:
                airship_point.draw(painter, self.block_length, False)

    def _draw_locks_and_bridges(self, painter: QPainter, world: WorldMap):
        """Draw lock and bridge map objects for non-warp worlds.

        Locks and bridge events are editor overlays rather than base tiles, so
        they are painted late in the pipeline after the map surface is already
        established. Warp world data is skipped because that map does not use
        the same lock and bridge object workflow.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        world : WorldMap
            World map or world number being processed.
        """
        if world.data.index == WORLD_MAP_WARP_WORLD_INDEX:
            return

        for lock_object in world.locks_and_bridges:
            lock_object.draw(painter, self.block_length, False, lock_object.selected)
