"""Level rendering pipeline for Foundry's in-level editor surface.

This module turns decoded level state into the layered pixels shown by the
editor: background and default graphics, level objects, overlays, jump hints,
grid lines, and Mario-position previews. It is the rendering counterpart to
``LevelView`` and the main place where SMB3 drawing rules become editor-facing
visual output.

Notes
-----
This file sits close to low-level SMB3 drawing behavior. When documenting
non-obvious rendering logic, prefer implementation-backed explanations and use
NESdev or SMB3 disassembly context only where the code clearly depends on it.

See Also
--------
foundry.gui.visualization.level.LevelView
    Interactive level canvas that uses this drawer for paint output.
foundry.game.level.Level
    Model whose decoded state is rendered here.
foundry.game.gfx.objects.in_level.object_renderer
    Expands SMB3 object definitions into renderable geometry.
"""

from itertools import product

from PySide6.QtCore import QPoint, QRect
from PySide6.QtGui import QBrush, QColor, QImage, QPainter, QPen, Qt

from foundry.game import EXPANDS_BOTH, EXPANDS_HORIZ, EXPANDS_VERT, GROUND
from foundry.game.gfx import BlockCache
from foundry.game.gfx.block_cache import draw_block, draw_enemy_item, draw_level_object
from foundry.game.gfx.drawable import (
    MARIO_SPRITE_SHEET_BY_POWERUP,
    load_from_object_sprite_sheet,
    make_image_selected,
)
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects.in_level.enemy_item import EnemyItem
from foundry.game.gfx.objects.in_level.level_object import LevelObject
from foundry.game.gfx.objects.world_map.sprite import EMPTY_IMAGE
from foundry.game.gfx.Palette import (
    NESPalette,
    bg_color_for_object_set,
    load_palette_group,
)
from foundry.game.level.Level import Level
from foundry.gui.dialogs.SettingsDialog import POWERUPS
from foundry.gui.settings import Settings
from foundry.gui.visualization.level.AutoScrollDrawer import AutoScrollDrawer
from smb3parse.constants import (
    CLOUDY_OBJECT_SET,
    DESERT_OBJECT_SET,
    DUNGEON_OBJECT_SET,
    ICE_OBJECT_SET,
    OBJ_AUTOSCROLL,
    OBJ_CHEST_EXIT,
    OBJ_CHEST_ITEM_SETTER,
    OBJ_PIPE_EXITS,
    OBJ_WHITE_MUSHROOM_HOUSE,
)
from smb3parse.levels import LEVEL_MAX_LENGTH, LEVEL_SCREEN_HEIGHT, LEVEL_SCREEN_WIDTH
from smb3parse.util import apply
from smb3parse.util.rect import Point

FIRE_FLOWER = load_from_object_sprite_sheet(16, 53)
LEAF = load_from_object_sprite_sheet(17, 53)
NORMAL_STAR = load_from_object_sprite_sheet(18, 53)
CONTINUOUS_STAR = load_from_object_sprite_sheet(19, 53)
MULTI_COIN = load_from_object_sprite_sheet(20, 53)
ONE_UP = load_from_object_sprite_sheet(21, 53)
COIN = load_from_object_sprite_sheet(22, 53)
VINE = load_from_object_sprite_sheet(23, 53)
P_SWITCH = load_from_object_sprite_sheet(24, 53)
SILVER_COIN = load_from_object_sprite_sheet(25, 53)
INVISIBLE_COIN = load_from_object_sprite_sheet(26, 53)
INVISIBLE_1_UP = load_from_object_sprite_sheet(27, 53)

NO_JUMP = load_from_object_sprite_sheet(32, 53)
UP_ARROW = load_from_object_sprite_sheet(33, 53)
DOWN_ARROW = load_from_object_sprite_sheet(34, 53)
LEFT_ARROW = load_from_object_sprite_sheet(35, 53)
RIGHT_ARROW = load_from_object_sprite_sheet(36, 53)

ITEM_ARROW = load_from_object_sprite_sheet(53, 53)


MARIO_BLOCK_WIDTH = 2
MARIO_BLOCK_HEIGHT = 2

MARIO_SPRITE_OVER_HEIGHT = 4  # pixels

MARIO_SPRITE_WIDTH = MARIO_BLOCK_WIDTH * Block.WIDTH
MARIO_SPRITE_HEIGHT = MARIO_BLOCK_HEIGHT * Block.HEIGHT + MARIO_SPRITE_OVER_HEIGHT

MARIO_WIDTH_SCALE_FACTOR = MARIO_SPRITE_WIDTH / (Block.WIDTH * 2)
MARIO_HEIGHT_SCALE_FACTOR = MARIO_SPRITE_HEIGHT / (Block.HEIGHT * 2)

MARIO_SPRITE_X_OFFSET = 0
MARIO_SPRITE_Y_OFFSET = -MARIO_SPRITE_OVER_HEIGHT / Block.HEIGHT


SPECIAL_BACKGROUND_OBJECTS = [
    "blue background",
    "starry background",
    "underground background under this",
    "sets background to actual background color",
]


OMITTED_ITEMS = [OBJ_PIPE_EXITS, OBJ_CHEST_EXIT, OBJ_CHEST_ITEM_SETTER, OBJ_WHITE_MUSHROOM_HOUSE]
"""
These configure things based on their y-position in the level. This is done in the editor directly now. So no need to
actually render them in the level.
"""


ENEMY_ITEMS_WITH_OVERLAYS = apply(
    str.lower, ("Invisible door (appears when you hit a P-switch)", "Red Koopa Paratroopa")
)


def _block_from_index(block_index: int, level: Level, animated: bool) -> Block:
    """Return a block from the level TSA table.

    This helper keeps block-cache access consistent for level drawing paths that need object-set,
    palette, graphics-set, and animation context.

    Parameters
    ----------
    block_index : int
        Index of the block.
    level : foundry.game.level.Level.Level
        Level that supplies object set, palette, graphics set, and TSA data.
    animated : bool
        Whether animated block frames should be used.

    Returns
    -------
    Block
        Block image for the requested block index.
    """

    return BlockCache.block(
        block_index,
        level.object_set_number,
        level.header.object_palette_index,
        level.header.graphic_set_index,
        animated,
    )


class LevelDrawer:
    """Render SMB3 level layers and editor overlays.

    The drawer paints the level in the same broad order the editor expects:
    background color, optional object-set default graphics, level objects and
    enemies/items, semantic overlays, expansion markers, Mario start markers,
    jump zones, grid coordinates, and autoscroll paths.

    Attributes
    ----------
    anim_frame : int
        Current animation frame used for animated blocks and enemies.
    block_length : int
        Rendered pixel size of one SMB3 block.
    coord_pen : QPen
        Pen used for grid coordinate labels.
    grid_pen : QPen
        Pen used for block grid lines.
    screen_pen : QPen
        Pen used for screen boundary lines.
    settings : Settings
        Level-view settings that toggle optional layers.
    should_draw_potential_marios : bool
        Whether all possible Mario start positions should be drawn.
    """

    def __init__(self):
        """Create a level drawer with shared pens, settings, and animation state.

        The drawer keeps long-lived paint resources and feature toggles so
        repeated paint events can render quickly without rebuilding pens,
        settings access, or animation bookkeeping each frame.
        """
        self.block_length = Block.WIDTH

        self.grid_pen = QPen(QColor(0x80, 0x80, 0x80, 0x80), 1)
        self.screen_pen = QPen(QColor(0xFF, 0x00, 0x00, 0xFF), 1)
        self.coord_pen = QPen(QColor(0xFF, 0x00, 0x00, 0xC0), 1)

        self.settings = Settings("mchlnix", "level drawer")
        self.anim_frame = 0
        self.should_draw_potential_marios = False

    def draw(self, painter: QPainter, level: Level):
        """Draw one full editor frame for a level.

        The pass is intentionally layered: background first, then implicit
        object-set scenery, then decoded objects, then semantic overlays and
        optional helper layers such as expansions, Mario previews, jumps, grid
        guides, and autoscroll traces. Each helper paints onto the same
        ``QPainter`` so later layers can annotate or sit above earlier ones.
        ``LevelView`` drives this once per repaint, which makes the ordering
        here the authoritative rendering pipeline for the level canvas and the
        boundary where decoded level data becomes one composed frame.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        level : foundry.game.level.Level.Level
            Level to render.
        """
        self._draw_background(painter, level)

        if self.settings.value("level_view/special_background"):
            self._draw_default_graphics(painter, level)

        self._draw_objects(painter, level)

        self._draw_overlays(painter, level)

        if self.settings.value("level_view/draw_expansion"):
            self._draw_expansions(painter, level)

        if self.should_draw_potential_marios:
            self._draw_potential_marios(painter, level)

        if self.settings.value("level_view/draw_mario"):
            self._draw_mario(painter, level)

        if self.settings.value("level_view/draw_jumps"):
            self._draw_jumps(painter, level)

        if self.settings.value("level_view/draw_grid"):
            self._draw_grid(painter, level)

        if self.settings.value("level_view/draw_grid_coordinates"):
            self._draw_grid_coordinates(painter, level)

        if self.settings.value("level_view/draw_autoscroll"):
            self._draw_auto_scroll(painter, level)

    def _draw_background(self, painter: QPainter, level: Level):
        """Fill the panel with the base background color for this level.

        Most object sets use a palette-derived background color directly, but
        cloudy levels pull the color from a specific palette slot to match the
        way that set is encoded and drawn. During ``draw``, this helper fills
        the full level rectangle before any other pixels are emitted. The level
        model supplies the object-set number and palette indices, this helper
        turns that state into one solid backdrop, and the later
        default-graphics, object, and overlay helpers all paint on top of that
        decoded base rectangle. The whole frame therefore starts from the same
        background color path the remaining layers assume.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        level : foundry.game.level.Level.Level
            Level to render.
        """
        painter.save()

        if level.object_set.number == CLOUDY_OBJECT_SET:
            bg_color = NESPalette[load_palette_group(level.object_set_number, level.header.object_palette_index)[3][2]]
        else:
            bg_color = bg_color_for_object_set(level.object_set_number, level.header.object_palette_index)

        painter.fillRect(QRect(*level.get_rect(self.block_length)), bg_color)

        painter.restore()

    def _draw_default_graphics(self, painter: QPainter, level: Level):
        """Draw object-set default scenery that is implicit in SMB3.

        Some object sets rely on background or floor graphics that are not
        stored as normal level objects. During ``draw``, this helper runs
        immediately after ``_draw_background`` and before ``_draw_objects``.
        The level object-set number selects which implicit scenery rule is
        active, this helper dispatches to one object-set-specific renderer,
        and that renderer mutates the shared painter before any decoded level
        objects are processed. In the frame lifecycle this is the handoff
        between ``_draw_background`` and ``_draw_objects``: the first stage
        contributes only the generic backdrop, this stage injects the
        object-set-derived implicit tiles SMB3 assumes, and the later object,
        overlay, and grid stages all consume that same synthesized base layer.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        level : foundry.game.level.Level.Level
            Level to render.
        """
        painter.save()

        if level.object_set.number == DESERT_OBJECT_SET:
            self._draw_desert_default_graphics(painter, level)

        elif level.object_set.number == DUNGEON_OBJECT_SET:
            self._draw_dungeon_default_graphics(painter, level)

        elif level.object_set.number == ICE_OBJECT_SET:
            self._draw_ice_default_graphics(painter, level)

        painter.restore()

    def _draw_dungeon_default_graphics(self, painter: QPainter, level: Level):
        # TODO Fix magic numbers
        """Draw dungeon background, ceiling, and floor blocks.

        Dungeon levels rely on implicit scenery that is not represented as
        ordinary editor objects. During the default-graphics stage, this helper
        consumes the dungeon object-set state and emits three concrete paint
        passes into the shared frame buffer: repeated wall fill for every block
        position, one ceiling strip across the top, and the alternating two-row
        floor pattern near ground level. When ``_draw_objects`` runs next, it
        paints decoded level geometry on top of that already-synthesized
        dungeon shell.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        level : foundry.game.level.Level.Level
            Level to render.
        """
        animated = self.settings.value("level_view/block_animation")

        # draw_background
        bg_block = _block_from_index(140, level, animated)

        for x, y in product(range(level.width), range(level.height)):
            bg_block.graphics_set.anim_frame = self.anim_frame
            bg_block.draw(painter, x * self.block_length, y * self.block_length, self.block_length)

        # draw ceiling
        ceiling_block = _block_from_index(139, level, animated)

        for x in range(level.width):
            ceiling_block.graphics_set.anim_frame = self.anim_frame
            ceiling_block.draw(painter, x * self.block_length, 0, self.block_length)

        # draw floor
        upper_floor_blocks = [
            _block_from_index(20, level, animated),
            _block_from_index(21, level, animated),
        ]
        lower_floor_blocks = [
            _block_from_index(22, level, animated),
            _block_from_index(23, level, animated),
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
        """Draw the implicit desert floor row.

        Desert object sets assume a stock floor strip near ground level even
        when no explicit terrain object encodes it. During the default-graphics
        stage, this helper expands that implicit rule into one repeated row of
        floor blocks at the ground boundary. Later object and overlay passes
        therefore operate against the same desert baseline SMB3 synthesizes
        from the object set.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        level : foundry.game.level.Level.Level
            Level to render.
        """
        animated = self.settings.value("level_view/block_animation")

        floor_level = (GROUND - 1) * self.block_length
        floor_block_index = 86

        floor_block = _block_from_index(floor_block_index, level, animated)

        for x in range(level.width):
            floor_block.graphics_set.anim_frame = self.anim_frame
            floor_block.draw(painter, x * self.block_length, floor_level, self.block_length)

    def _draw_ice_default_graphics(self, painter: QPainter, level: Level):
        """Draw the implicit ice background block field.

        Ice levels use a repeated background tile across the whole panel.
        During the default-graphics stage, this helper expands the ice
        object-set's backing tile across every decoded block position before
        explicit objects are drawn. That full-panel fill becomes the shared
        base state for the rest of the frame, so later object, overlay, and
        grid passes annotate an already-synthesized ice field instead of
        needing to special-case blank background pixels.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        level : foundry.game.level.Level.Level
            Level to render.
        """
        animated = self.settings.value("level_view/block_animation")

        bg_block = _block_from_index(0x80, level, animated)

        for x, y in product(range(level.width), range(level.height)):
            bg_block.graphics_set.anim_frame = self.anim_frame
            bg_block.draw(painter, x * self.block_length, y * self.block_length, self.block_length)

    def _draw_objects(self, painter: QPainter, level: Level):
        """Draw level objects, enemies/items, and selection outlines.

        Configuration-only enemy items are skipped because their behavior is
        represented by dedicated editor UI. Special background objects are
        expanded across the remaining level space before normal rendering. This
        is the pipeline step where decoded level-model objects become visible
        blocks or sprites, animated frame state is pushed into renderers, and
        selection outlines are anchored to the same geometry that later input
        handling and overlays reference.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        level : foundry.game.level.Level.Level
            Level to render.
        """
        animated = self.settings.value("level_view/block_animation")

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

                    draw_block(
                        painter,
                        block_index,
                        level_object.object_set.number,
                        level_object.palette_group.index,
                        level_object.graphics_set.number,
                        x,
                        y,
                        self.block_length,
                        False,
                        level_object.selected,
                        animated,
                    )
            else:
                if isinstance(level_object, LevelObject):
                    draw_level_object(
                        level_object,
                        painter,
                        self.block_length,
                        self.settings.value("level_view/block_transparency"),
                        self.settings.value("level_view/block_animation"),
                    )
                else:
                    assert isinstance(level_object, EnemyItem)

                    level_object.anim_frame = self.anim_frame

                    draw_enemy_item(level_object, painter, self.block_length)

            if level_object.selected:
                painter.save()

                painter.setPen(QPen(QColor(0x00, 0x00, 0x00, 0x80), 1))
                painter.drawRect(QRect(*level_object.get_rect(self.block_length)))

                painter.restore()

    def _draw_overlays(self, painter: QPainter, level: Level):
        """Draw semantic overlays for hidden items and jump triggers.

        Overlays make ROM-encoded behavior visible: pipe and door jump arrows,
        missing-jump indicators, block contents, invisible items, silver coins,
        and the red Koopa Paratroopa movement marker. During ``draw``, this
        pass reads each decoded object name, position, and render rectangle
        after geometry is already on the painter, translates that state into an
        overlay image or guide line, and adds the metadata-driven cues that
        explain how those rendered objects behave.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        level : foundry.game.level.Level.Level
            Level to inspect for overlay-worthy objects.
        """
        painter.save()

        for level_object in level.get_all_objects():
            name = level_object.name.lower()

            # only handle this specific enemy item for now
            if isinstance(level_object, EnemyItem) and name not in ENEMY_ITEMS_WITH_OVERLAYS:
                continue

            pos = level_object.get_rect(self.block_length).top_left()
            rect = level_object.get_rect(self.block_length)

            # invisible coins, for example, expand and need to have multiple overlays drawn onto them
            # set true by default, since for most overlays it doesn't matter
            fill_object = True

            # pipe entries
            if "pipe" in name and "can go" in name:
                if not self.settings.value("level_view/draw_jump_on_objects"):
                    continue

                fill_object = False

                # center() is one pixel off for some reason
                pos = rect.top_left() + Point(rect.width // 2, rect.height // 2)

                trigger_position = level_object.get_position()

                if "left" in name:
                    image = LEFT_ARROW

                    pos.x = rect.right()
                    pos.y -= self._half_block

                    # leftward pipes trigger on the column to the left of the opening
                    x = level_object.get_rect().bottom_right().x
                    y = level_object.get_rect().bottom_right().y
                    trigger_position = (x - 1, y)

                elif "right" in name:
                    image = RIGHT_ARROW
                    pos.x = rect.left() - self.block_length
                    pos.y -= self._half_block

                elif "down" in name:
                    image = DOWN_ARROW

                    pos.x -= self._half_block
                    pos.y = rect.top() - self.block_length
                else:
                    # upwards pipe
                    image = UP_ARROW

                    pos.x -= self._half_block
                    pos.y = rect.bottom()

                    # upwards pipes trigger on the second-to-last row
                    x = level_object.get_rect().bottom_left().x
                    y = level_object.get_rect().bottom_left().y
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

                pos.y = rect.top() - self.block_length

                x, y = level_object.get_position()

                # jumps seemingly trigger on the bottom block
                if not self._object_in_jump_area(level, (x, y + 1)):
                    image = NO_JUMP

            # "?" - blocks, note blocks, wooden blocks and bricks
            elif "'?' with" in name or "brick with" in name or "bricks with" in name or "block with" in name:
                if not self.settings.value("level_view/draw_items_in_blocks"):
                    continue

                pos.y -= self.block_length

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

                # draw a little arrow for the offset item overlay
                arrow_pos = pos.copy()
                arrow_pos.y += self.block_length // 4
                painter.drawImage(QPoint(*arrow_pos), ITEM_ARROW.scaled(self.block_length, self.block_length))

            elif "invisible" in name:
                if not self.settings.value("level_view/draw_invisible_items"):
                    continue

                if "coin" in name:
                    image = INVISIBLE_COIN
                elif "1-up" in name:
                    image = INVISIBLE_1_UP
                else:
                    image = EMPTY_IMAGE

            elif "silver coins" in name:
                if not self.settings.value("level_view/draw_invisible_items"):
                    continue

                image = SILVER_COIN

            elif "red koopa" in name:
                if not self.settings.value("level_view/draw_invisible_items"):
                    continue

                painter.save()

                koopa_trail_pen = QPen(Qt.GlobalColor.red)
                koopa_trail_pen.setStyle(Qt.PenStyle.DotLine)
                koopa_trail_pen.setWidth(self.block_length // 8)

                start_pos = pos + Point(self._half_block, 2 * self.block_length)
                end_pos = start_pos + Point(0, 7 * self.block_length)

                painter.setPen(koopa_trail_pen)

                painter.drawLine(QPoint(*start_pos), QPoint(*end_pos))

                koopa_trail_pen.setStyle(Qt.PenStyle.SolidLine)
                painter.setPen(koopa_trail_pen)
                painter.drawLine(pos.x, end_pos.y, pos.x + self.block_length, end_pos.y)

                painter.restore()

                continue
            else:
                continue

            if fill_object:
                for x in range(level_object.rendered_width):
                    adapted_pos = pos.copy()
                    adapted_pos.x += x * self.block_length

                    image = image.scaled(self.block_length, self.block_length)
                    painter.drawImage(QPoint(*adapted_pos), image)

                    if level_object.selected:
                        painter.drawImage(QPoint(*adapted_pos), make_image_selected(image))

            else:
                image = image.scaled(self.block_length, self.block_length)
                painter.drawImage(QPoint(*pos), image)

        painter.restore()

    @staticmethod
    def _object_in_jump_area(level: Level, pos: tuple[int, int]):
        """Flag a block position covered by any jump zone.

        Pipe and door overlays call this from ``_draw_overlays`` while
        translating one trigger block into one overlay icon. The level model
        supplies the decoded jump list, this helper tests a single block
        position against those rectangles, and the boolean result flows
        directly back into the overlay branch that chooses either a direction
        arrow or the missing-jump warning marker. That keeps jump validation
        localized to one predicate while the surrounding overlay workflow
        continues mapping rendered objects into maintainer-facing jump cues.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Level containing jump definitions.
        pos : tuple[int, int]
            Block position to test.

        Returns
        -------
        bool
            ``True`` when the position is inside any jump rectangle.
        """
        for jump in level.jumps:
            jump_rect = jump.get_rect(1, level.is_vertical)

            if jump_rect.point_in(*pos):
                return True
        else:
            return False

    def _draw_expansions(self, painter: QPainter, level: Level):
        """Draw color-coded object expansion overlays.

        Magenta marks objects that expand both ways, red marks horizontal
        expansion, and blue marks vertical expansion. During ``draw``, this
        helper walks the already-decoded object list after geometry is visible,
        maps each object's expansion mode to one translucent brush, and paints
        that object's rendered rectangle into the shared frame. The result is a
        resizeability overlay that stays aligned with the same object bounds
        input handling and selection logic already use. The data flow therefore
        stays linear: decoded objects expose expansion metadata, this helper
        converts that metadata into one overlay color per object, and the
        painter receives those translucent rectangles on top of the already
        rendered geometry without introducing a second geometry model just for
        the overlay layer.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        level : foundry.game.level.Level.Level
            Level whose objects should be annotated.
        """
        for level_object in level.get_all_objects():
            if self.settings.value("level_view/draw_expansion"):
                painter.save()

                painter.setPen(Qt.PenStyle.NoPen)

                if level_object.expands() == EXPANDS_BOTH:
                    painter.setBrush(QColor(0xFF, 0, 0xFF, 0x80))
                elif level_object.expands() == EXPANDS_HORIZ:
                    painter.setBrush(QColor(0xFF, 0, 0, 0x80))
                elif level_object.expands() == EXPANDS_VERT:
                    painter.setBrush(QColor(0, 0, 0xFF, 0x80))

                painter.drawRect(QRect(*level_object.get_rect(self.block_length)))

                painter.restore()

    def _draw_potential_marios(self, painter: QPainter, level: Level):
        """Draw every possible Mario start position for the header.

        These translucent sprites help tune the start-action bits by showing
        all candidate positions derived from the level header. ``LevelView``
        enables this helper layer only during Mario-start dragging, so the
        painter can show valid landing positions before the header edit is
        committed through undo commands.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        level : foundry.game.level.Level.Level
            Level whose header provides candidate start positions.
        """
        painter.save()
        painter.setOpacity(0.2)

        mario_sprite = self._mario_sprite_for_action(level.start_action)

        # adjust it outside the list comprehension, otherwise we lose precision when the QPoint rounds down
        adjusted_y_offset = MARIO_SPRITE_Y_OFFSET * self.block_length

        # get all potential mario positions
        potential_positions = [QPoint(x, y) * self.block_length for x, y in level.header.gen_mario_start_positions()]

        for mario_position in potential_positions:
            mario_position.setY(mario_position.y() + adjusted_y_offset)
            painter.drawImage(mario_position, mario_sprite)

        painter.restore()

    def _draw_mario(self, painter: QPainter, level: Level):
        # get the part of Mario from the Mario sprite sheet
        """Draw Mario at the active start position.

        This layer renders the single committed start state, while
        ``_draw_potential_marios`` renders every valid candidate during
        interactive Mario-start dragging.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        level : foundry.game.level.Level.Level
            Level whose header supplies the start position.
        """
        mario_sprite = self._mario_sprite_for_action(level.start_action)

        adjusted_y_offset = MARIO_SPRITE_Y_OFFSET * self.block_length

        mario_position = QPoint(*level.header.mario_position()) * self.block_length
        mario_position.setY(mario_position.y() + adjusted_y_offset)

        painter.drawImage(mario_position, mario_sprite)

    def _mario_sprite_for_action(self, start_action_index: int) -> QImage:
        # loop through positions and draw transparent mario
        """Build the Mario sprite that matches a header start action.

        SMB3 stores several entry behaviors in the header, such as different
        pipe or entry animations. This helper translates that encoded action
        into the matching sprite strip and scales it to the active block size
        so both committed Mario rendering and potential-start previews can draw
        from the same decoded sprite image during the frame.

        Parameters
        ----------
        start_action_index : int
            Index of the start action.

        Returns
        -------
        QImage
            Mario sprite image for that start action.
        """
        x_offset = MARIO_SPRITE_WIDTH * start_action_index

        # TODO: The pipe sprites are off by one. Needs an additional offset to rectify
        powerup_state = self.settings.value("editor/default_powerup")
        mario_sprite_sheet = MARIO_SPRITE_SHEET_BY_POWERUP[POWERUPS[powerup_state].power_up_code]

        mario_sprite = mario_sprite_sheet.copy(QRect(x_offset, 0, MARIO_SPRITE_WIDTH, MARIO_SPRITE_HEIGHT))

        mario_sprite = mario_sprite.scaled(
            MARIO_BLOCK_WIDTH * self.block_length * MARIO_WIDTH_SCALE_FACTOR,
            MARIO_BLOCK_HEIGHT * self.block_length * MARIO_HEIGHT_SCALE_FACTOR,
        )
        return mario_sprite

    def _draw_jumps(self, painter: QPainter, level: Level):
        """Draw jump-zone rectangles from the level jump table.

        These overlays make the otherwise indirect next-area trigger regions
        visible while editing doors, pipes, and other jump-producing objects.
        During ``draw``, this helper reads the decoded jump table, converts
        each jump rectangle into painter coordinates, and draws those bounds
        after objects but before optional grid aids. The same frame therefore
        shows both trigger coverage and the geometry that would activate it.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        level : foundry.game.level.Level.Level
            Level containing jump definitions.
        """
        for jump in level.jumps:
            painter.setBrush(QBrush(QColor(0xFF, 0x00, 0x00), Qt.BrushStyle.FDiagPattern))

            painter.drawRect(QRect(*jump.get_rect(self.block_length, level.is_vertical)))

    def _draw_grid(self, painter: QPainter, level: Level):
        """Draw block grid lines and screen boundary lines.

        The grid combines one-block guides with red screen boundaries so edits
        can be reasoned about in both object-space and SMB3 screen-space.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        level : foundry.game.level.Level.Level
            Level whose dimensions define the grid.
        """
        panel_width, panel_height = level.get_rect(self.block_length).size()

        self._draw_grid_lines(painter, panel_height, panel_width)
        self._draw_screen_lines(painter, panel_height, panel_width, level.is_vertical)

    def _draw_grid_coordinates(self, painter: QPainter, level: Level):
        """Draw screen-start coordinate labels along the level axis.

        Labels are placed on the scrolling axis only, which matches how SMB3
        screen divisions matter for horizontal versus vertical levels.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        level : foundry.game.level.Level.Level
            Level whose orientation determines label placement.
        """
        panel_width, panel_height = level.get_rect(self.block_length).size()

        font = painter.font()
        font.setPointSize(self.block_length)

        painter.setFont(font)

        painter.setPen(self.coord_pen)

        if level.is_vertical:
            for y in range(0, panel_height, self.block_length * LEVEL_SCREEN_HEIGHT):
                painter.drawText(QPoint(0, self.block_length + y), str(y // self.block_length))
        else:
            for x in range(0, panel_width, self.block_length * LEVEL_SCREEN_WIDTH):
                painter.drawText(QPoint(x, self.block_length), str(x // self.block_length))

    def _draw_screen_lines(self, painter: QPainter, panel_height, panel_width, vertical_level):
        """Draw SMB3 screen boundary lines.

        Horizontal levels divide by screen width; vertical levels divide by
        screen height. The editor keeps that distinction visible because many
        game behaviors and save warnings are screen-oriented.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        panel_height : int
            Rendered level height in pixels.
        panel_width : int
            Rendered level width in pixels.
        vertical_level : bool
            Whether the level uses vertical orientation.
        """
        font = painter.font()
        font.setPointSize(self.block_length)

        painter.setFont(font)

        painter.setPen(self.screen_pen)

        if vertical_level:
            for y in range(0, panel_height, self.block_length * LEVEL_SCREEN_HEIGHT):
                painter.drawLine(0, self.block_length + y, panel_width, self.block_length + y)
        else:
            for x in range(0, panel_width, self.block_length * LEVEL_SCREEN_WIDTH):
                painter.drawLine(x, 0, x, panel_height)

    def _draw_grid_lines(self, painter, panel_height, panel_width):
        """Draw one-block grid lines across the level panel.

        These are the fine-grained placement guides underneath the coarser red
        screen boundaries drawn by ``_draw_screen_lines``. During ``_draw_grid``,
        this helper turns the rendered panel dimensions into one-block x and y
        positions, emits the full lattice into the painter, and hands control
        back to ``_draw_screen_lines`` for the larger SMB3 screen cuts. The
        data flow matters because the lattice spacing is derived from the same
        block length the object, overlay, and selection passes already used,
        so the guides land on the exact pixel grid those earlier stages
        established.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        panel_height : int
            Rendered level height in pixels.
        panel_width : int
            Rendered level width in pixels.
        """
        painter.setPen(self.grid_pen)

        # draw vertical grid lines
        for x in range(0, panel_width, self.block_length):
            painter.drawLine(x, 0, x, panel_height)

        # draw horizontal grid lines
        for y in range(0, panel_height, self.block_length):
            painter.drawLine(0, y, panel_width, y)

    def _draw_auto_scroll(self, painter: QPainter, level: Level):
        """Draw the autoscroll path for the first autoscroll item.

        Autoscroll is configured by a dedicated enemy or item entry rather than
        a standalone level field, so this helper scans the decoded enemy stream
        during ``draw`` for the first matching controller. When one is present,
        the helper lifts that item's decoded autoscroll type into an
        ``AutoScrollDrawer`` and asks it to paint the path overlay onto this
        frame using the same block scale as the rest of the level view. If the
        enemy stream contains no autoscroll controller, the overlay phase exits
        without adding any path markers. The data flow therefore stays aligned
        with SMB3's encoding model: enemy bytes define the controller, the
        level model exposes that decoded item, and the overlay layer turns it
        into the path maintainers inspect while editing.

        Parameters
        ----------
        painter : QPainter
            Painter used to render the object or view.
        level : foundry.game.level.Level.Level
            Level containing enemy/item data.
        """
        for item in level.enemies:
            if item.obj_index == OBJ_AUTOSCROLL:
                break
        else:
            return

        drawer = AutoScrollDrawer(item.auto_scroll_type, level)

        drawer.draw(painter, self.block_length)

    @property
    def _half_block(self):
        """Expose half of the rendered block size.

        Overlay alignment uses this helper while placing icons and sprites that
        need to sit on the centerline of a block rather than its origin. The
        overlay and jump-marker helpers read this property while translating
        decoded block positions into centered painter offsets, so one shared
        derivation keeps those alignment calculations consistent wherever the
        render pipeline needs half-block placement. Keeping that derivation in
        one property also means every overlay stage stays synchronized when the
        view changes block scale. The render pipeline therefore reads one
        centered offset from this property, carries that value through overlay
        placement, and avoids letting separate overlay stages drift onto
        slightly different centerlines when block scaling changes.

        Returns
        -------
        int
            Half the active rendered block size in pixels.
        """
        return self.block_length // 2
