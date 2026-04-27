"""Expand SMB3 terrain-object generators into rendered block layouts.

This module contains the execution logic that turns decoded ``LevelObject``
state into the block arrays, rendered bounds, and warning paths used by
Foundry's level views. It is the render-phase bridge between symbolic object
definitions and the rectangular block footprints that drawing, hit testing,
and selection overlays consume.

See Also
--------
foundry.game.gfx.objects.in_level.level_object
    Supplies the decoded object state that the renderer expands.
foundry.gui.visualization.level.LevelDrawer
    Consumes the rendered block footprints produced here while painting levels.
"""

from typing import TYPE_CHECKING
from warnings import warn

from foundry.game import GROUND, SKY
from foundry.game.File import ROM
from foundry.game.ObjectDefinitions import EndType, GeneratorType
from smb3parse.constants import (
    LVL_OBJ_PLAINS_DOWNWARD_VINE,
    LVL_OBJ_SKY_WOODEN_POLE,
    PLAINS_OBJECT_SET,
)
from smb3parse.levels import LEVEL_MAX_LENGTH, LEVEL_SCREEN_HEIGHT, LEVEL_SCREEN_WIDTH
from smb3parse.util.rect import Rect

# not all objects provide a block index for a blank block
BLANK = -1

if TYPE_CHECKING:
    from foundry.game.gfx.objects.in_level.level_object import LevelObject


class LevelObjectRenderWarning(UserWarning):
    """Warn when object expansion produces inconsistent preview geometry.

    ``ObjectRenderer`` emits this warning at the boundary where compact SMB3
    object bytes are expanded into concrete block layouts. A warning here means
    Foundry could still decode enough information to keep the object editable,
    but the rendered width, height, or block count no longer agree with one
    another. That soft-failure path matters because object definitions evolve
    over time and some legacy or partially understood generators are still more
    useful when shown imperfectly than when they abort level rendering.

    Notes
    -----
    This warning is part of Foundry's reverse-engineering safety net: it keeps
    suspicious object-definition behavior visible to maintainers without taking
    down the whole level view.
    """

    pass


class ObjectRenderer:
    """Expand a ``LevelObject`` into rendered block geometry.

    The renderer interprets the object's generator type, ending behavior,
    encoded lengths, and sibling-object context to turn one compact SMB3
    object record into a block list, rendered bounds, and a hit-test
    rectangle. It is the execution step between parsed object metadata and the
    block arrays used by level drawing and inspection tools.

    Parameters
    ----------
    level_object : foundry.game.gfx.objects.in_level.level_object.LevelObject
        Level object being displayed or modified.

    Attributes
    ----------
    _base_x : int
        Leftmost block coordinate after generator-specific offsets.
    _base_y : int
        Topmost block coordinate after generator-specific offsets.
    _new_height : int
        Rendered height accumulated during expansion.
    _new_width : int
        Rendered width accumulated during expansion.
    _object : foundry.game.gfx.objects.in_level.level_object.LevelObject
        Level object whose generator is being expanded.

    Notes
    -----
    This class is effectively the executor for SMB3 object-generator behavior:
    ``ObjectDefinition`` supplies the symbolic generator type and this class
    applies the corresponding expansion rules to produce concrete block layout.

    Examples
    --------
    Stage the minimal object state for a horizontal generator, run one render
    pass, and inspect the footprint that level drawing will later consume::

        from types import SimpleNamespace

        from foundry.game.ObjectDefinitions import EndType, GeneratorType

        obj = SimpleNamespace(
            x_position=10,
            y_position=5,
            rendered_width=1,
            rendered_height=1,
            generator_type=GeneratorType.HORIZONTAL,
            ending=EndType.UNIFORM,
            length=2,
            height=1,
            secondary_length=0,
            width=1,
            blocks=[0x6A],
            is_4byte=False,
            object_info=None,
            name="Example row",
        )
        obj.objects_ref = [obj]

        renderer = ObjectRenderer(obj)
        renderer.render()

        (obj.rendered_base_x, obj.rendered_base_y)
        (10, 5)
        (obj.rendered_width, obj.rendered_height)
        (3, 1)
        obj.rendered_blocks
        [106, 106, 106]
    """

    def __init__(self, level_object: "LevelObject"):
        """Capture the decoded object state needed for one render pass.

        Initialization snapshots the object's current rendered origin and size
        state so one render pass can update width, height, and block layout
        without repeatedly re-reading mutable object properties.

        Parameters
        ----------
        level_object : foundry.game.gfx.objects.in_level.level_object.LevelObject
            Level object being displayed or modified.
        """
        self._object = level_object

        self._base_x: int = self._object.x_position
        """
        The left most point where blocks for this object are drawn from. This is often the same as the x position, but
        in pyramids for example, the x position describes the center, from which they grow outwards in both directions.

        B...O¤.... With B being the base x and base y and the O being the objects x and y in the data of the ROM
        ...¤¤¤¤...
        ..¤¤¤¤¤¤..
        .¤¤¤¤¤¤¤¤.
        ¤¤¤¤¤¤¤¤¤¤
        """
        self._base_y: int = self._object.y_position
        """See _base_x."""

        self._new_width: int = self._object.rendered_width
        """
        After rendering the object might be wider than originally thought. Keep track of it, while rendering here.
        """
        self._new_height: int = self._object.rendered_height
        """
        After rendering the object might be taller than originally thought. Keep track of it, while rendering here.
        """

    def render(self):
        """Expand one SMB3 object record into rendered blocks and bounds.

        The renderer chooses the generator-specific expansion path, builds the
        block buffer, reconciles inferred width and height with the produced
        block count, and stores the finished rectangle back on the level
        object for later drawing and hit testing. This is the main render
        workflow boundary where decoded object metadata becomes block-buffer
        state reused by level drawing, selection, and inspector surfaces.

        Examples
        --------
        Render a simple uniform horizontal object and inspect the fields that
        the rest of the level view consumes afterward::

            from types import SimpleNamespace

            from foundry.game.ObjectDefinitions import EndType, GeneratorType

            obj = SimpleNamespace(
                x_position=10,
                y_position=5,
                rendered_width=1,
                rendered_height=1,
                generator_type=GeneratorType.HORIZONTAL,
                ending=EndType.UNIFORM,
                length=2,
                height=1,
                secondary_length=0,
                width=1,
                blocks=[0x6A],
                is_4byte=False,
                object_info=None,
                name="Example row",
            )
            obj.objects_ref = [obj]

            ObjectRenderer(obj).render()

            (obj.rendered_base_x, obj.rendered_base_y)
            (10, 5)
            (obj.rendered_width, obj.rendered_height)
            (3, 1)
            obj.rendered_blocks
            [106, 106, 106]
        """
        if self._object in self._object.objects_ref:
            self._object.index_in_level = self._object.objects_ref.index(self._object)

        blocks_to_draw: list[int] = []

        self._render_by_generator_type(blocks_to_draw)

        # for not yet implemented objects and single block objects
        if blocks_to_draw:
            self._object.rendered_blocks = blocks_to_draw
        else:
            self._object.rendered_blocks = self._object.blocks

        if self._new_width == 0:
            warn(
                f"Calculated Width is 0, setting to 1: {self._object.name}. "
                f"Blocks to draw: {len(self._object.rendered_blocks)}. Height calculated: {self._new_height}",
                LevelObjectRenderWarning,
            )

            self._new_width = 1
        else:
            expected_height_from_blocks = len(self._object.rendered_blocks) / self._new_width

            if self._new_height != expected_height_from_blocks:
                warn(
                    f"Not enough Blocks for calculated height: {self._object.name}. "
                    f"Height from Blocks: {expected_height_from_blocks}. Height calculated: {self._new_height}",
                    LevelObjectRenderWarning,
                )

                self._new_height = int(expected_height_from_blocks)

        self._object.rect = Rect(self._base_x, self._base_y, self._new_width, self._new_height)

        self._object.rendered_width = self._new_width
        self._object.rendered_height = self._new_height
        self._object.rendered_base_x = self._base_x
        self._object.rendered_base_y = self._base_y

    def _render_by_generator_type(self, blocks_to_draw: list[int]):
        """Dispatch expansion to the generator-specific render path.

        Generator type is the main branch point in SMB3 object rendering, so
        this dispatcher routes one decoded object state into the correct
        expansion workflow while keeping the surrounding render pass focused on
        block-buffer assembly and bounds updates.

        Parameters
        ----------
        blocks_to_draw : list[int]
            Block buffer populated by the renderer.
        """
        if self._object.generator_type == GeneratorType.TO_THE_SKY:
            self._render_to_sky(blocks_to_draw)

        elif self._object.generator_type == GeneratorType.DESERT_PIPE_BOX:
            self._render_desert_pipe_box(blocks_to_draw)

        elif self._object.generator_type in [
            GeneratorType.DIAG_DOWN_LEFT,
            GeneratorType.DIAG_DOWN_RIGHT,
            GeneratorType.DIAG_UP_RIGHT,
            GeneratorType.DIAG_WEIRD,
        ]:
            self._render_diagonals(blocks_to_draw)

        elif self._object.generator_type == GeneratorType.DIAG_STAGGERED:
            self._render_diagonal_staggered(blocks_to_draw)

        elif self._object.generator_type in [
            GeneratorType.PYRAMID_TO_GROUND,
            GeneratorType.PYRAMID_2,
        ]:
            self._render_pyramids(blocks_to_draw)

        elif self._object.generator_type == GeneratorType.ENDING:
            self._render_ending(blocks_to_draw)

        elif self._object.generator_type == GeneratorType.VERTICAL:
            self._render_vertical(blocks_to_draw)

        elif self._object.generator_type in [
            GeneratorType.HORIZONTAL,
            GeneratorType.HORIZONTAL_2,
            GeneratorType.HORIZ_TO_GROUND,
        ]:
            self._render_horizontal(blocks_to_draw)

        elif self._object.generator_type == GeneratorType.WOODEN_PLATFORM:
            self._render_wooden_platform(blocks_to_draw)

        elif self._object.generator_type == GeneratorType.BRICK_WALL:
            self._render_brick_wall(blocks_to_draw)

        else:
            if not self._object.generator_type == GeneratorType.SINGLE_BLOCK:
                warn(f"Didn't render {self._object.name}", LevelObjectRenderWarning)
                # breakpoint()

            if self._object.name.lower() == "black boss room background":
                self._render_black_boss_room_bg(blocks_to_draw)

    def _render_diagonal_staggered(self, blocks_to_draw: list[int]):
        """Expand staggered diagonal generators into blank-padded rows.

        These SMB3 generators advance one step per row while widening the
        footprint, so the renderer grows width and height together, shifts the
        rendered base x coordinate, and inserts blank padding that preserves
        the intended diagonal data flow into the shared block buffer.

        Parameters
        ----------
        blocks_to_draw : list[int]
            Block buffer populated by the renderer.
        """
        self._new_height = self._object.height + self._object.length
        self._new_width = self._object.width + self._object.length

        self._base_x = self._object.x_position - self._object.length

        top = self._object.blocks[0 : self._object.width]
        bottom = self._object.blocks[self._object.width * (self._object.height - 1) :]

        assert len(top) == len(bottom) == 1

        for row in range(self._new_height):
            front_blanks = self._new_width - 1 - row
            back_blanks = -1 + row

            if front_blanks > 0:
                blocks_to_draw.extend([BLANK] * front_blanks)

            if row < self._new_height - len(top):
                blocks_to_draw.extend(top)

            if row > 0:
                blocks_to_draw.extend(bottom)

            if back_blanks > 0:
                blocks_to_draw.extend([BLANK] * back_blanks)

    def _render_brick_wall(self, blocks_to_draw: list[int]):
        """Render brick wall.

        It keeps SMB3 object bytes aligned with editor geometry, rendering, and serialization. The method updates stored state that later editor operations depend on.

        Parameters
        ----------
        blocks_to_draw : list[int]
            Block buffer populated by the renderer.
        """
        top = self._object.blocks[0 : self._object.width]
        middle = self._object.blocks[self._object.width : 2 * self._object.width]
        bottom = self._object.blocks[self._object.width * (self._object.height - 1) :]

        no_of_rows = self._object.secondary_length + 1
        no_of_columns = self._object.length + 1

        needs_x_offset = no_of_rows > 1
        x_offset = self._object.width // 2

        self._new_height = self._object.height * no_of_rows
        self._new_width = self._object.width * no_of_columns

        self._base_x = self._object.x_position
        if needs_x_offset:
            self._base_x -= x_offset

        if self._object.secondary_length > 0:
            self._new_width += self._object.width // 2

        def _insert_block_row(blocks: list[int]):
            if not blocks:
                return

            if needs_x_offset and row % 2 == 0:
                blocks_to_draw.extend([BLANK] * x_offset)

            for column in range(no_of_columns):
                blocks_to_draw.extend(blocks)

            if needs_x_offset and row % 2 == 1:
                blocks_to_draw.extend([BLANK] * x_offset)

        for row in range(no_of_rows):
            _insert_block_row(top)

            for _ in range(self._object.height - 2):
                _insert_block_row(middle)

            if self._object.height > 1:
                _insert_block_row(bottom)

    def _render_wooden_platform(self, blocks_to_draw: list[int]):
        """Render wooden platform.

        It keeps SMB3 object bytes aligned with editor geometry, rendering, and serialization. The method updates stored state that later editor operations depend on.

        Parameters
        ----------
        blocks_to_draw : list[int]
            Block buffer populated by the renderer.
        """
        if self._object.is_4byte:
            # Seemingly the max for the few objects that do grow vertically
            self._new_height = min(self._object.secondary_length + 1, self._object.height)
        else:
            # The block is almost always rendered as having a height of 1, no matter what the object data says
            # It also expands its width differently and alternates between two fill blocks, needing its own generator
            self._new_height = 1

        # length of 0 fills the screen, length of 1 means 2, 2 means 3 and so on
        if self._object.length == 0:
            # TODO Would need a level reference to know how many screens there are, to properly size this object
            # Now it extends past most levels, unless they are at max size, causing a warning in the editor
            self._new_width = LEVEL_MAX_LENGTH - self._base_x
        else:
            self._new_width = self._object.width + (self._object.length - 1)

        if self._object.ending == EndType.TWO_ENDS:
            for row in range(self._new_height):
                start = (len(self._object.blocks) // self._object.height) * (row % self._object.height)
                end = start + (len(self._object.blocks) // self._object.height)

                left_end, right_end, *middles = self._object.blocks[start:end]
                blocks_to_draw.append(left_end)

                middle_block_count = self._new_width - self._object.width

                # any width larger than 2 is filled by alternating between the two fill blocks
                for middle_index in range(middle_block_count):
                    blocks_to_draw.append(middles[middle_index % len(middles)])

                blocks_to_draw.append(right_end)

        elif self._object.ending == EndType.BOTTOM_OR_RIGHT:
            left_end, right_end, *middles = self._object.blocks
            blocks_to_draw.append(left_end)

            if not middles:
                middles = [left_end]

            middle_block_count = self._new_width - self._object.width

            # any width larger than 2 is filled by alternating between the two fill blocks
            for middle_index in range(middle_block_count):
                blocks_to_draw.append(middles[middle_index % len(middles)])

            blocks_to_draw.append(right_end)

    def _render_black_boss_room_bg(self, blocks_to_draw: list[int]):
        """Render black boss room bg.

        It keeps SMB3 object bytes aligned with editor geometry, rendering, and serialization. The method updates stored state that later editor operations depend on.

        Parameters
        ----------
        blocks_to_draw : list[int]
            Block buffer populated by the renderer.
        """
        self._new_width = LEVEL_SCREEN_WIDTH
        self._new_height = LEVEL_SCREEN_HEIGHT

        self._base_x = self._object.x_position // LEVEL_SCREEN_WIDTH * LEVEL_SCREEN_WIDTH
        self._base_y = 0

        blocks_to_draw.clear()
        blocks_to_draw.extend(LEVEL_SCREEN_WIDTH * LEVEL_SCREEN_HEIGHT * [self._object.blocks[0]])

    def _render_horizontal(self, blocks_to_draw):
        """Render one horizontally expanding object footprint.

        Parameters
        ----------
        blocks_to_draw : list[int]
            Block buffer populated by the renderer.
        """
        self._new_width = self._object.length + 1
        downwards_extending_vine = LVL_OBJ_PLAINS_DOWNWARD_VINE
        wooden_sky_pole = LVL_OBJ_SKY_WOODEN_POLE

        if self._object.object_info in [downwards_extending_vine, wooden_sky_pole]:
            self._new_width -= 1

        if self._object.generator_type == GeneratorType.HORIZ_TO_GROUND:
            self._sub_render_horizontal_to_ground()

        elif self._object.generator_type == GeneratorType.HORIZONTAL_2 and self._object.ending == EndType.TWO_ENDS:
            # floating platforms seem to just be one shorter for some reason
            self._new_width -= 1
        else:
            self._new_height = self._object.height + self._object.secondary_length

        if self._object.ending == EndType.UNIFORM and not self._object.is_4byte:
            self._sub_render_horizontal_uniform_3byte(blocks_to_draw)

        elif self._object.ending == EndType.UNIFORM and self._object.is_4byte:
            self._sub_render_4byte_uniform(blocks_to_draw)

        elif self._object.ending == EndType.TOP_OR_LEFT:
            for y in range(self._new_height):
                offset = y * self._object.width

                blocks_to_draw.append(self._object.blocks[offset])

                for x in range(1, self._new_width):
                    blocks_to_draw.append(self._object.blocks[offset + 1])

        elif self._object.ending == EndType.BOTTOM_OR_RIGHT:
            for y in range(self._new_height):
                offset = y * self._object.width

                for x in range(self._new_width - 1):
                    blocks_to_draw.append(self._object.blocks[offset])

                blocks_to_draw.append(self._object.blocks[offset + self._object.width - 1])

        elif self._object.ending == EndType.TWO_ENDS:
            self._sub_render_horizontal_two_ends(blocks_to_draw)

    def _sub_render_horizontal_two_ends(self, blocks_to_draw):
        """Fill a horizontal generator using left cap, middle, and right cap.

        SMB3 stores these objects as compact rows whose first and last blocks
        differ from the repeatable middle section. The helper expands that row
        data into the rectangular block buffer and then stretches the interior
        rows to the final rendered height.

        Parameters
        ----------
        blocks_to_draw : list[int]
            Block buffer populated by the renderer.

        Raises
        ------
        ValueError
            If the input data or current state is invalid.
        """
        if self._object.generator_type == GeneratorType.HORIZONTAL and self._object.is_4byte:
            # flat ground objects have an artificial limit of 2 lines
            if (
                self._object.object_set.number == PLAINS_OBJECT_SET
                and self._object.domain == 0
                and self._object.obj_index in range(0xC0, 0xE0)
            ):
                self._object.height = self._new_height = min(2, self._object.secondary_length + 1)

            else:
                self._new_height = self._object.secondary_length + 1

        if self._object.width > len(self._object.blocks):
            raise ValueError(f"{self} does not provide enough blocks to fill a row.")

        else:
            start = 0
            end = self._object.width

        for y in range(self._object.height):
            new_start = y * self._object.width
            new_end = (y + 1) * self._object.width

            if new_end > len(self._object.blocks):
                # repeat the last line of blocks to fill the object
                pass

            else:
                start = new_start
                end = new_end

            left_, *middle_, right_ = self._object.blocks[start:end]

            blocks_to_draw.append(left_)
            blocks_to_draw.extend(middle_ * (self._new_width - 2))
            blocks_to_draw.append(right_)

        if not len(blocks_to_draw) % self._object.height == 0:
            warn(
                f"Blocks to draw are not divisible by height. {self}",
                LevelObjectRenderWarning,
            )

        self._new_width = int(len(blocks_to_draw) / self._object.height)
        top_row = blocks_to_draw[0 : self._new_width]
        middle_blocks_ = blocks_to_draw[self._new_width : self._new_width * 2]
        bottom_row = blocks_to_draw[-self._new_width :]

        blocks_to_draw.clear()
        blocks_to_draw.extend(top_row)

        for y in range(1, self._new_height - 1):
            blocks_to_draw.extend(middle_blocks_)

        if self._new_height > 1:
            blocks_to_draw.extend(bottom_row)

    def _sub_render_4byte_uniform(self, blocks_to_draw):
        # 4 byte objects
        """Render a uniform four-byte horizontal object.

        Parameters
        ----------
        blocks_to_draw : list[int]
            Block buffer populated by the renderer.
        """
        top = self._object.blocks[0:1]
        bottom = self._object.blocks[-1:]
        self._new_height = self._object.height + self._object.secondary_length

        # ceilings are one shorter than normal
        if self._object.height > self._object.width:
            self._new_height -= 1

        if self._object.generator_type == GeneratorType.HORIZONTAL_2:
            for _ in range(0, self._new_height - 1):
                blocks_to_draw.extend(self._new_width * top)

            blocks_to_draw.extend(self._new_width * bottom)

        else:
            blocks_to_draw.extend(self._new_width * top)

            for _ in range(1, self._new_height):
                blocks_to_draw.extend(self._new_width * bottom)

    def _sub_render_horizontal_uniform_3byte(self, blocks_to_draw):
        """Render a uniform three-byte horizontal object.

        Parameters
        ----------
        blocks_to_draw : list[int]
            Block buffer populated by the renderer.
        """
        for y in range(self._new_height):
            offset = (y % self._object.height) * self._object.width

            for _ in range(0, self._new_width):
                blocks_to_draw.extend(self._object.blocks[offset : offset + self._object.width])

        # in case of giant blocks
        self._new_width *= self._object.width

    def _sub_render_horizontal_to_ground(self):
        # to the ground only until it hits something
        """Render render horizontal to ground.

        It keeps SMB3 object bytes aligned with editor geometry, rendering, and serialization. The method updates stored state that later editor operations depend on.
        """
        for y in range(self._base_y, self._object.ground_level):
            bottom_row = Rect(self._base_x, y, self._new_width, 1)

            if any(
                [
                    bottom_row.intersects(obj.get_rect()) and y == obj.get_rect().top()
                    for obj in self._object.objects_ref[0 : self._object.index_in_level]
                ]
            ):
                self._new_height = y - self._base_y
                break

        else:
            # nothing underneath this object, extend to the ground
            self._new_height = self._object.ground_level - self._base_y

        if self._object.is_fixed:
            self._new_width = self._object.length

        min_height = min(self._object.height, 2)
        self._new_height = max(min_height, self._new_height)

    def _render_vertical(self, blocks_to_draw):
        """Render one vertically expanding object footprint.

        Parameters
        ----------
        blocks_to_draw : list[int]
            Block buffer populated by the renderer.
        """
        self._new_height = self._object.length + 1
        self._new_width = self._object.width

        if self._object.ending == EndType.UNIFORM:
            if self._object.is_4byte:
                # there is one VERTICAL 4-byte object: Vertically oriented X-blocks
                # the width is the primary expansion
                self._new_width = (self._object.obj_index & 0x0F) + 1

            for _ in range(self._new_height):
                for y in range(self._object.height):
                    for x in range(self._new_width):
                        blocks_to_draw.append(self._object.blocks[y * self._object.height + x % self._object.width])

            # adjust height for giant blocks, so that the rect is correct
            self._new_height *= self._object.height

        elif self._object.ending == EndType.TOP_OR_LEFT:
            # in case the drawn object is smaller than its actual size
            for y in range(min(self._object.height, self._new_height)):
                offset = y * self._object.width
                blocks_to_draw.extend(self._object.blocks[offset : offset + self._object.width])

            additional_rows = self._new_height - self._object.height

            # assume only the last row needs to repeat
            # todo true for giant blocks?
            if additional_rows > 0:
                last_row = self._object.blocks[-self._object.width :]

                for _ in range(additional_rows):
                    blocks_to_draw.extend(last_row)

        elif self._object.ending == EndType.BOTTOM_OR_RIGHT:
            additional_rows = self._new_height - self._object.height

            # assume only the first row needs to repeat
            # todo true for giant blocks?
            if additional_rows > 0:
                last_row = self._object.blocks[0 : self._object.width]

                for _ in range(additional_rows):
                    blocks_to_draw.extend(last_row)

            # in case the drawn object is smaller than its actual size
            for y in range(min(self._object.height, self._new_height)):
                offset = y * self._object.width
                blocks_to_draw.extend(self._object.blocks[offset : offset + self._object.width])

        elif self._object.ending == EndType.TWO_ENDS:
            # object exists on ships
            top_row = self._object.blocks[0 : self._object.width]
            bottom_row = self._object.blocks[-self._object.width :]

            blocks_to_draw.extend(top_row)

            additional_rows = self._new_height - 2

            # repeat second to last row
            if additional_rows > 0:
                for _ in range(additional_rows):
                    blocks_to_draw.extend(self._object.blocks[-2 * self._object.width : -self._object.width])

            if self._new_height > 1:
                blocks_to_draw.extend(bottom_row)

    def _render_ending(self, blocks_to_draw):
        """Expand the SMB3 ending strip and embedded goal graphics.

        The ending object starts as a repeated backdrop fill, then patches in
        the goal-card artwork read from ROM. That turns one compact ending
        object into the full screen-edge footprint shown by Foundry's level
        renderer. It is also the render boundary where object-definition
        metadata has to pull additional ROM block data into the same block
        buffer as the repeated background fill.

        Parameters
        ----------
        blocks_to_draw : list[int]
            Block buffer populated by the renderer.
        """
        page_width = 16
        page_limit = page_width - self._object.x_position % page_width

        self._new_width = page_width + page_limit + 1
        self._new_height = (GROUND - 1) - SKY

        for y in range(SKY, GROUND - 1):
            blocks_to_draw.append(self._object.blocks[0])
            blocks_to_draw.extend([self._object.blocks[1]] * (self._new_width - 1))

        rom_offset = self._object.object_set.get_ending_offset()
        rom = ROM()

        ending_graphic_height = 6
        floor_height = 1
        y_offset = GROUND - floor_height - ending_graphic_height

        for y in range(ending_graphic_height):
            for x in range(page_width):
                block_index = rom.int(rom_offset + y * page_width + x - 1)

                block_position = (y_offset + y) * self._new_width + x + page_limit + 1
                blocks_to_draw[block_position] = block_index

        # the ending object is seemingly always 1 block too wide (going into the next screen)
        for end_of_line in range(len(blocks_to_draw) - 1, 0, -self._new_width):
            blocks_to_draw.pop(end_of_line)

        self._new_width -= 1
        # Mushroom/Fire flower/Star is categorized as an enemy

    def _render_pyramids(self, blocks_to_draw):
        # since pyramids grow horizontally in both directions when expanding, we need to check for new ground every time
        # it grows
        """Expand a pyramid generator around its centered SMB3 origin.

        Pyramid objects grow outward while also searching for the ground or an
        intersecting object below them. The renderer therefore updates width,
        height, and base x together before writing the triangular block data
        into the shared buffer, keeping collision-aware growth and final block
        layout in one render workflow.

        Parameters
        ----------
        blocks_to_draw : list[int]
            Block buffer populated by the renderer.
        """
        objects_before = self._object.objects_ref[0 : self._object.index_in_level]

        for y in range(self._base_y, self._object.ground_level):
            self._new_height = y - self._base_y
            self._new_width = 2 * self._new_height

            bottom_row = Rect(self._base_x, y, self._new_width, 1)

            if any((bottom_row.intersects(obj.get_rect()) and y == obj.get_rect().top() for obj in objects_before)):
                break

        # the tip of a pyramid is 2 blocks, the x position is the left block, so subtract half the width minus 1
        self._base_x = self._object.x_position - (self._new_width // 2 - 1)

        blank = self._object.blocks[0]
        left_slope = self._object.blocks[1]
        left_fill = self._object.blocks[2]
        right_fill = self._object.blocks[3]
        right_slope = self._object.blocks[4]

        for y in range(self._new_height):
            blank_blocks = (self._new_width // 2) - (y + 1)
            middle_blocks = y  # times two

            blocks_to_draw.extend(blank_blocks * [blank])

            blocks_to_draw.append(left_slope)
            blocks_to_draw.extend(middle_blocks * [left_fill] + middle_blocks * [right_fill])
            blocks_to_draw.append(right_slope)

            blocks_to_draw.extend(blank_blocks * [blank])

    def _render_diagonals(self, blocks_to_draw):
        """Expand SMB3 diagonal slope generators into rectangular buffers.

        Diagonal generators describe visible slope blocks plus the blank space
        needed to place them at the proper step. This method converts that
        compact slope definition into full rows so later rendering and hit
        testing can treat the object like any other rectangular footprint,
        while still preserving generator-specific reversals and base-coordinate
        shifts inside one data-flow step.

        Parameters
        ----------
        blocks_to_draw : list[int]
            Block buffer populated by the renderer.
        """
        if self._object.ending == EndType.UNIFORM:
            self._new_height = (self._object.length + 1) * self._object.height
            self._new_width = (self._object.length + 1) * self._object.width

            left = [BLANK]
            right = [BLANK]
            slopes = self._object.blocks

        elif self._object.ending == EndType.TOP_OR_LEFT:
            self._new_height = (self._object.length + 1) * self._object.height
            self._new_width = (self._object.length + 1) * (self._object.width - 1)  # without fill block

            if self._object.generator_type in [
                GeneratorType.DIAG_DOWN_RIGHT,
                GeneratorType.DIAG_UP_RIGHT,
            ]:
                fill_block = self._object.blocks[0:1]
                slopes = self._object.blocks[1:]

                left = fill_block
                right = [BLANK]

            elif self._object.generator_type == GeneratorType.DIAG_DOWN_LEFT:
                fill_block = self._object.blocks[-1:]
                slopes = self._object.blocks[0:-1]

                right = fill_block
                left = [BLANK]

            else:
                fill_block = self._object.blocks[0:1]
                slopes = self._object.blocks[1:]

                right = [BLANK]
                left = fill_block

        elif self._object.ending == EndType.BOTTOM_OR_RIGHT:
            self._new_height = (self._object.length + 1) * self._object.height
            self._new_width = (self._object.length + 1) * (self._object.width - 1)  # without fill block

            fill_block = self._object.blocks[-1:]
            slopes = self._object.blocks[0:-1]

            left = [BLANK]
            right = fill_block

        else:
            # todo other two ends not used with diagonals?
            self._object.rendered_blocks = []
            raise LevelObjectRenderWarning(f"{self._object.name} was not rendered.")

        rows = []
        if self._object.height > self._object.width:
            slope_width = self._object.width
        else:
            slope_width = len(slopes)

        for y in range(self._new_height):
            amount_right = (y // self._object.height) * slope_width
            amount_left = self._new_width - slope_width - amount_right

            offset = y % self._object.height

            rows.append(amount_left * left + slopes[offset : offset + slope_width] + amount_right * right)

        if self._object.generator_type == GeneratorType.DIAG_UP_RIGHT:
            for row in rows:
                row.reverse()

        if self._object.generator_type in [
            GeneratorType.DIAG_DOWN_RIGHT,
            GeneratorType.DIAG_UP_RIGHT,
        ]:
            if not self._object.height > self._object.width:
                rows.reverse()

        if self._object.generator_type == GeneratorType.DIAG_DOWN_RIGHT and self._object.height > self._object.width:
            # special case for 60 degree platform wire down right
            for row in rows:
                row.reverse()

        if self._object.generator_type == GeneratorType.DIAG_UP_RIGHT:
            self._base_y -= self._new_height - 1

        if self._object.generator_type == GeneratorType.DIAG_DOWN_LEFT:
            self._base_x -= self._new_width - slope_width

        for row in rows:
            blocks_to_draw.extend(row)

    def _render_desert_pipe_box(self, blocks_to_draw: list[int]):
        # segments are the horizontal sections, which are 8 blocks long
        # two of those are drawn per length bit
        # rows are the 4 block high rows Mario can walk in
        """Expand the desert pipe-box generator into a boxed walkable region.

        Pipe-box objects repeat 8-block segments across several four-line
        rows, then close the structure with one final line. The renderer
        converts that compact length and height encoding into the full boxed
        footprint stored in the shared block buffer, so the editor can treat
        the result like normal rectangular render state even though the SMB3
        generator logic grows in segment-sized steps.

        Parameters
        ----------
        blocks_to_draw : list[int]
            Block buffer populated by the renderer.
        """
        is_pipe_box_type_b = self._object.obj_index // 0x10 == 4
        rows_per_box = self._object.height
        lines_per_row = 4
        segment_width = self._object.width
        segments = (self._object.length + 1) * 2

        box_height = lines_per_row * rows_per_box
        self._new_width = segments * segment_width
        self._new_height = box_height

        for row_number in range(rows_per_box):
            for line in range(lines_per_row):
                if is_pipe_box_type_b and row_number > 0 and line == 0:
                    # in pipebox type b we do not repeat the horizontal beams
                    line += 1

                start = line * segment_width
                stop = start + segment_width

                for segment_number in range(segments):
                    blocks_to_draw.extend(self._object.blocks[start:stop])

        # draw another last row
        self._new_height += 1
        if is_pipe_box_type_b:
            # draw another open row
            start = segment_width

        else:
            # draw the first row again to close the box
            start = 0

        stop = start + segment_width
        for segment_number in range(segments):
            blocks_to_draw.extend(self._object.blocks[start:stop])

        # every line repeats the last block again for some reason
        for end_of_line in range(len(blocks_to_draw), 0, -self._new_width):
            blocks_to_draw.insert(end_of_line, blocks_to_draw[end_of_line - 1])

        self._new_width += 1

    def _render_to_sky(self, blocks_to_draw: list[int]):
        """Extend a vertical generator upward until it reaches the sky row.

        SMB3 uses this generator for objects that repeat from the object's y
        position up to the fixed sky boundary. The renderer moves the rendered
        base to ``SKY`` and emits the repeated column so later drawing sees the
        same vertical footprint.

        Parameters
        ----------
        blocks_to_draw : list[int]
            Block buffer populated by the renderer.
        """
        self._base_x = self._object.x_position
        self._base_y = SKY

        for _ in range(self._object.y_position):
            blocks_to_draw.extend(self._object.blocks[0 : self._object.width])

        blocks_to_draw.extend(self._object.blocks[-self._object.width :])
        self._new_height = self._object.y_position + (self._object.height - 1)
