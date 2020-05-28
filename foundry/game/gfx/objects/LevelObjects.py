from abc import ABC, abstractmethod
import logging

from foundry.game.File import ROM
from foundry.game.gfx.objects.LevelObject import LevelObject, SKY, GROUND, BLANK
from foundry.game.gfx.objects.ObjectLike import EXPANDS_BOTH, EXPANDS_HORIZ, EXPANDS_NOT, EXPANDS_VERT, ObjectLike
from foundry.game.ObjectDefinitions import (
    DESERT_PIPE_BOX,
    DIAG_DOWN_LEFT,
    DIAG_DOWN_RIGHT,
    DIAG_UP_RIGHT,
    DIAG_WEIRD,
    ENDING,
    END_ON_BOTTOM_OR_RIGHT,
    END_ON_TOP_OR_LEFT,
    HORIZONTAL,
    HORIZONTAL_2,
    HORIZ_TO_GROUND,
    PYRAMID_2,
    PYRAMID_TO_GROUND,
    SINGLE_BLOCK_OBJECT,
    TO_THE_SKY,
    TWO_ENDS,
    UNIFORM,
    VERTICAL,
)

from foundry.game.Size import Size
from foundry.game.Position import Position, LevelPosition
from foundry.game.Range import Range
from foundry.game.Rect import Rect
from foundry import data_dir

logging.basicConfig(filename=data_dir.joinpath("logs/lvl_objs.log"), level=logging.CRITICAL)


class LevelObjectToSky(LevelObject):
    def _render(self):
        """Draws an blocks to the sky from a given y position"""
        pos, size = Position.from_pos(self.pos), Size.from_size(self.bmp.size)
        blocks_to_draw = []

        base_pos = Position(self.pos.x, SKY)

        for _ in range(self.pos.y):
            blocks_to_draw.extend(self.blocks[0: self.bmp.size.width])
        blocks_to_draw.extend(self.blocks[-self.bmp.size.width:])

        self._confirm_render(size, base_pos, blocks_to_draw)


class LevelObjectDesertPipeBox(LevelObject):
    LINES_PER_ROW = 4

    def _render(self):
        """
        Segments are the horizontal sections, which are 8 blocks long
        two of those are drawn per length bit
        rows are the 4 block high rows Mario can walk in
        """
        pos, size = Position.from_pos(self.pos), Size.from_size(self.bmp.size)
        blocks_to_draw = []
        is_pipe_box_type_b = self.obj_index // 0x10 == 4  # Todo: Move this to a new class

        rows_per_box = self.bmp.size.height
        segment_width = size.width
        segments = (self.size.width + 1) * 2
        base_size = Size(segments * segment_width, self.LINES_PER_ROW * rows_per_box)

        for row_number in range(rows_per_box):
            for line in range(self.LINES_PER_ROW):
                # pipe box type b does not repeat the horizontal beams
                line += 1 if is_pipe_box_type_b and row_number > 0 and line == 0 else 0

                rng = Range.from_offset(line * segment_width, segment_width)
                for _ in range(segments):
                    blocks_to_draw.extend(self.blocks[rng.start:rng.end])

        # draw another open row or draw the first row again to close the box
        start = segment_width if is_pipe_box_type_b else 0
        rng = Range.from_offset(start, segment_width)
        for _ in range(segments):
            blocks_to_draw.extend(self.blocks[rng.start:rng.end])

        self._confirm_render(base_size, pos, blocks_to_draw)


class LevelObjectDiagnal(LevelObject):
    def expands(self):
        return EXPANDS_HORIZ

    def slope(self):
        """The slope from self.blocks"""
        raise NotImplemented

    def body(self):
        """The body from self.blocks"""
        raise NotImplemented

    @abstractmethod
    def _render(self):
        """The render routine for the level object"""

    @abstractmethod
    def get_block_from_position(self, pos):
        """Returns the corresponding block for a given position"""

    def expands(self):
        return EXPANDS_HORIZ

    def primary_expansion(self):
        return EXPANDS_HORIZ

    @abstractmethod
    def render_slope(self):
        """Returns the size, pos, and blocks_to_draw of the rendered slope"""


class LevelObjectDiagnal45(LevelObjectDiagnal):
    def slope(self):
        """The slope from self.blocks"""
        raise NotImplemented

    def body(self):
        """The body from self.blocks"""
        raise NotImplemented

    @abstractmethod
    def _render(self):
        """The render routine for the level object"""

    def render_slope(self):
        pos, size = Position.from_pos(self.pos), Size(self.size.width + 1, self.size.width + 1)
        blocks_to_draw = [self.get_block_from_position(pos) for pos in size.positions()]
        return size, pos, blocks_to_draw

    def get_block_from_position(self, pos):
        if pos.x == pos.y:
            return self.slope
        elif pos.x < pos.y:
            return self.body
        else:
            return BLANK


class LevelObjectDiagnal30(LevelObjectDiagnal):
    def slope(self):
        """The slope from self.blocks"""
        raise NotImplemented

    def body(self):
        """The body from self.blocks"""
        raise NotImplemented

    @abstractmethod
    def _render(self):
        """The render routine for the level object"""

    def render_slope(self):
        pos, size = Position.from_pos(self.pos), Size((self.size.width + 1) * 2, self.size.width + 1)
        blocks_to_draw = [self.get_block_from_position(pos) for pos in size.positions()]
        return size, pos, blocks_to_draw

    def get_block_from_position(self, pos):
        if pos.x // 2 == pos.y:
            return self.slope[pos.x % 2]
        elif pos.x // 2 < pos.y:
            return self.body
        else:
            return BLANK


class DownRightDiagnal(LevelObjectDiagnal):
    def _render(self):
        self._confirm_render(*self.render_slope())


class DownLeftDiagnal(LevelObjectDiagnal):
    HORZ_OFFSET = 0

    def _render(self):
        size, pos, blocks_to_draw = self.render_slope()
        blocks_to_draw = size.flip_rows(blocks_to_draw)
        pos = pos - Position(size.width - self.HORZ_OFFSET, 0)
        self._confirm_render(size, pos, blocks_to_draw)


class LevelObjectDiagnalDownLeft45(DownLeftDiagnal, LevelObjectDiagnal45):
    HORZ_OFFSET = 1

    @property
    def slope(self):
        return self.blocks[0]

    @property
    def body(self):
        return self.blocks[1] if len(self.blocks) == 2 else BLANK


class LevelObjectDiagnalDownLeft30(DownLeftDiagnal, LevelObjectDiagnal30):
    HORZ_OFFSET = 2

    @property
    def slope(self):
        return [self.blocks[1], self.blocks[0]]

    @property
    def body(self):
        return self.blocks[2] if len(self.blocks) == 3 else BLANK


class LevelObjectDiagnalDownRight30(DownRightDiagnal, LevelObjectDiagnal30):
    @property
    def slope(self):
        return self.blocks[1:]

    @property
    def body(self):
        return self.blocks[0]


class LevelObjectDiagnalDownRight45(DownRightDiagnal, LevelObjectDiagnal45):
    @property
    def slope(self):
        return self.blocks[1] if len(self.blocks) == 2 else self.blocks[0]

    @property
    def body(self):
        return self.blocks[0] if len(self.blocks) == 2 else BLANK


class LevelObjectDiagnalUpRight45(LevelObjectDiagnal45):
    @property
    def slope(self):
        if len(self.blocks) == 2:
            return self.blocks[1]
        else:
            return self.blocks[0]

    @property
    def body(self):
        try:
            return self.blocks[0]
        except IndexError:
            return 0

    def _render(self):
        size, pos, blocks_to_draw = self.render_slope()
        blocks_to_draw.reverse()

        self._confirm_render(size, pos, blocks_to_draw)


class LevelObjectDiagnalWeird45(LevelObjectDiagnal45):
    @property
    def slope(self):
        if len(self.blocks) == 2:
            return self.blocks[1]
        else:
            return self.blocks[0]

    @property
    def body(self):
        try:
            return self.blocks[0]
        except IndexError:
            return 0

    def expands(self):
        return EXPANDS_HORIZ | EXPANDS_VERT

    def _render(self):
        size, pos, blocks_to_draw = self.render_slope()

        self._confirm_render(size, pos, blocks_to_draw)


class LevelObjectPyramidToGround(LevelObject):
    """Makes a pyramid that grows horizontally in both directions that extends to the ground"""
    def expands(self):
        return EXPANDS_HORIZ

    def _render(self):
        """Draws a pyramid that expands every block"""
        pos, size = self.pos, Size.from_size(self.bmp.size)
        blocks_to_draw = []

        pos.x += 1  # set the new base_x to the tip of the pyramid

        for y in range(pos.y, self.ground_level):
            size = Size(2 * size.height, y - pos.y)
            bottom_rect = Rect.from_size_and_position(Size(size.width, 1), Position(pos.x, y))
            if self._if_intersects(bottom_rect):
                break

        pos.x = pos.x - (size.width // 2)
        blank, left_slope, left_fill, right_fill, right_slope = self.blocks[0:5]

        for y in range(size.height):
            blank_blocks = (size.width // 2) - (y + 1)
            middle_blocks = y  # times two

            blocks_to_draw.extend(blank_blocks * [blank])
            blocks_to_draw.append(left_slope)
            blocks_to_draw.extend(middle_blocks * [left_fill] + middle_blocks * [right_fill])
            blocks_to_draw.append(right_slope)
            blocks_to_draw.extend(blank_blocks * [blank])

        self._confirm_render(size, pos, blocks_to_draw)


class LevelObjectEndingBackground(LevelObject):
    GROUND = 26
    ENDING_GRAPHIC_HEIGHT = 6
    FLOOR_HEIGHT = 1

    def expands(self):
        return EXPANDS_HORIZ

    @property
    def fade_tile(self):
        return self.blocks[0]

    @property
    def background(self):
        return self.blocks[1]

    @property
    def page_limit(self):
        return LevelPosition.SCREEN_WIDTH - (self.x_pos % LevelPosition.SCREEN_WIDTH)

    @property
    def rom_offset(self):
        return self.object_set.get_ending_offset()

    def _render(self):
        """Draws the end of level background"""
        posi, size = LevelPosition.from_pos(self.pos), Size.from_size(self.bmp.size)

        rect = Rect.from_size_and_position(Size(LevelPosition.SCREEN_WIDTH + posi.rel_x_inverse + 1, self.GROUND),
                                           Position(0, 0))

        blocks_to_draw = [self.fade_tile if pos.x == 0 else self.background for pos in rect.positions()]

        rom = ROM()
        bg_rect = Rect.from_size_and_position(
            Size(LevelPosition.SCREEN_WIDTH, self.ENDING_GRAPHIC_HEIGHT),
            Position(self.page_limit + 1, self.GROUND - self.ENDING_GRAPHIC_HEIGHT)
        )

        for i, pos in enumerate(bg_rect.positions()):
            block = rom.get_byte(self.rom_offset + i - 1)
            blocks_to_draw[rect.index_position(pos)] = block

        self._confirm_render(rect.abs_size, Position(posi.x, 0), blocks_to_draw)


class LevelObjectVertical(LevelObject):
    def expands(self):
        return EXPANDS_VERT

    def primary_expansion(self):
        return EXPANDS_HORIZ | EXPANDS_VERT if self.is_4byte else EXPANDS_VERT

    @property
    def height_leng(self):
        # invert height and length
        return self.size.width

    @height_leng.setter
    def height_leng(self, value):
        # invert height and length
        self.size.width = value

    @property
    def hlength(self):
        # invert height and length
        return self.size.height

    @hlength.setter
    def hlength(self, value):
        # invert height and length
        self.size.height = value

    def get_block_from_position(self, overload=0):
        """
        Provides the correct blocks for the provided amount
        :param List blocks: The blocks provided
        :return: The blocks
        :rtype: List
        """
        if len(self.blocks) == 4:
            lt, rt, lm, rm = self.blocks
            mt, mb, mm = 0, 0, 0
            lb, rb = lm, rm
        elif len(self.blocks) == 3:
            lt, lm, lb = self.blocks
            mt, mm, mb, rt, rm, rb = lt, lm, lb, lt, lm, lb
        else:
            logging.debug(f"{self} did not recieve any blocks from {self.blocks}")
            return [0, 0, 0, 0, 0, 0, 0, 0, 0]

        return [lt, mt, rt, lm, mm, rm, lb, mb, rb]

    def _render(self):
        """Draws an blocks to the sky from a given y position"""
        pos, size = Position.from_pos(self.pos), self.bmp.size.invert() + Size(0, self.height_leng - 1)
        blocks_to_draw = []

        ending_functions = {
            UNIFORM: self._render_uniform,
            END_ON_TOP_OR_LEFT: self._render_end_on_top_or_left,
            END_ON_BOTTOM_OR_RIGHT: self._render_end_on_bottom_or_right,
            TWO_ENDS: self._render_two_ends
        }
        pos, size, blocks_to_draw = ending_functions[self.ending](pos, size, blocks_to_draw)

        self._confirm_render(size, pos, blocks_to_draw)

    def _render_uniform(self, pos, size, blocks_to_draw):
        """Update values for the ending UNIFORM"""
        for po in Rect.from_size_and_position(size, pos).positions():
            for _ in range(self.bmp.size.width):
                try:
                    blocks_to_draw.append(self.blocks[0])
                except IndexError:
                    blocks_to_draw.append(0)
        return pos, size, blocks_to_draw

    def _render_end_on_top_or_left(self, pos, size, blocks_to_draw):
        """Updates values for the ending END_ON_TOP_OR_LEFT"""
        # in case the drawn object is smaller than its actual size
        blocks = self.get_block_from_position()
        for po in size.positions():
            blocks_to_draw.append(blocks[size.get_relational_position(po)])
        return pos, size, blocks_to_draw

    def _render_end_on_bottom_or_right(self, pos, size, blocks_to_draw):
        """Updates values for the ending END_ON_BOTTOM_OR_RIGHT"""
        additional_rows = size.height - self.bmp.size.height

        # assume only the first row needs to repeat
        # todo true for giant blocks?
        if additional_rows > 0:
            last_row = self.blocks[0: self.bmp.size.width]
            for _ in range(additional_rows):
                blocks_to_draw.extend(last_row)

        # in case the drawn object is smaller than its actual size
        for y in range(min(self.bmp.size.height, size.height)):
            offset = y * self.bmp.size.width
            blocks_to_draw.extend(self.blocks[offset: offset + self.bmp.size.width])
        return pos, size, blocks_to_draw

    def _render_two_ends(self, pos, size, blocks_to_draw):
        """Updates values for the ending TWO_ENDS"""
        # object exists on ships
        top_row = self.blocks[0: self.bmp.size.width]
        bottom_row = self.blocks[-self.bmp.size.width:]

        blocks_to_draw.extend(top_row)

        additional_rows = size.height - 2
        # repeat second to last row
        if additional_rows > 0:
            for _ in range(additional_rows):
                blocks_to_draw.extend(self.blocks[-2 * self.bmp.size.width: -self.bmp.size.width])

        if size.height > 1:
            blocks_to_draw.extend(bottom_row)
        return pos, size, blocks_to_draw


class LevelObjectHorizontal(LevelObject):
    def expands(self):
        return EXPANDS_HORIZ

    def primary_expansion(self):
        return EXPANDS_HORIZ | EXPANDS_VERT if self.is_4byte else EXPANDS_HORIZ

    def get_block_position(self, pos, size):
        try:
            return self.blocks[pos.y]
        except IndexError:
            return self.blocks[0]

    def get_blocks(self, pos, size):
        return [self.get_block_position(po, size) for po in size.positions()]

    def _render(self):
        """Draws an blocks to the sky from a given y position"""
        pos, size = Position.from_pos(self.pos), self.bmp.size + Size(self.size.width, self.size.height)
        blocks_to_draw = self.get_blocks(pos, size)
        self._confirm_render(size, pos, blocks_to_draw)


class LevelObjectHorizontalWithTop(LevelObjectHorizontal):
    @property
    def top(self):
        return self.blocks[0]

    @property
    def body(self):
        return self.blocks[1]

    def get_block_position(self, pos, size):
        return self.top if pos.y == 0 else self.body


class LevelObjectHorizontalWithSides(LevelObjectHorizontal):
    @property
    def left(self):
        return self.blocks[0]

    @property
    def right(self):
        return self.blocks[2] if len(self.blocks) == 3 else self.blocks[0]

    @property
    def body(self):
        return self.blocks[1] if len(self.blocks) == 3 else self.blocks[0]

    def get_block_position(self, pos, size):
        if pos.x == 0:
            return self.left
        elif pos.x == size.width - 1:
            return self.right
        else:
            return self.body


class LevelObjectHorizontalWithSidesAndTop(LevelObjectHorizontal):
    @property
    def left(self):
        return self.blocks[0]

    @property
    def right(self):
        return self.blocks[2] if len(self.blocks) == 3 else self.blocks[0]

    @property
    def body(self):
        return self.blocks[1] if len(self.blocks) == 3 else self.blocks[0]

    def get_block_position(self, pos, size):
        if pos.x == 0:
            return self.left
        elif pos.x == size.width - 1:
            return self.right
        else:
            return self.body


class LevelObjectHorizontalToGround(LevelObjectHorizontal):
    def _render(self):
        """Draws a horizontal block to the ground"""
        pos, size = Position.from_pos(self.pos), self.bmp.size + Size(self.size.width - 1, self.size.height)
        blocks_to_draw = []

        for y in range(pos.y, self.ground_level):
            size = Size(size.width, y - pos.y + 1)
            bottom_rect = Rect.from_size_and_position(Size(size.width, 1), pos)
            if self._if_intersects(bottom_rect):
                break
        else:
            print("found no ground")
            # nothing underneath this object, extend to the ground
            size.height = self.ground_level - pos.y

        if self.is_single_block:
            size.width = self.size.width

        super()._render()
        self._confirm_render(size, pos, blocks_to_draw)


class LevelObjectHorizontalAlt(LevelObjectHorizontal):
    def _render_two_ends(self, pos, size, blocks_to_draw):
        """Updates values for the ending TWO_ENDS"""
        size.width -= 1
        start, *middle, end = self.blocks
        for po in size.positions():
            try:
                if po.x == 0:
                    blocks_to_draw.append(start)
                elif po.x == size.width + 1:
                    blocks_to_draw.append(end)
                else:
                    blocks_to_draw.append(middle[(self.blocks[size.index_position(po)] - 1) % len(middle)])
            except IndexError:
                blocks_to_draw.append(self.blocks[0])
        return pos, size, blocks_to_draw


class SingleBlock(LevelObject):
    def _render(self):
        """Draws a singular block"""
        self._confirm_render(self.bmp.size, self.pos, self.blocks)


class LevelObjectPipe(LevelObject):
    def expands(self):
        return EXPANDS_HORIZ

    def primary_expansion(self):
        return EXPANDS_NOT

    @property
    def pipe_entrance(self):
        try:
            return [self.blocks[0], self.blocks[1]]
        except IndexError:
            print(f"{self} does not have a pipe entrance")

    @property
    def pipe_body(self):
        try:
            return [self.blocks[2], self.blocks[3]]
        except IndexError:
            print(f"{self} does not have a pipe body")


class LevelObjectDownwardPipe(LevelObjectPipe):
    def _render(self):
        """Draws an upward pipe"""
        pos, size = Position.from_pos(self.pos), Size(2, self.size.width + 1)
        blocks_to_draw = []
        for po in size.height_positions():
            if po.y == 0:
                blocks_to_draw.extend(self.pipe_entrance)
            else:
                blocks_to_draw.extend(self.pipe_body)

        self._confirm_render(size, pos, blocks_to_draw)


class LevelObjectUpwardPipe(LevelObjectPipe):
    def _render(self):
        """Draws an downward pipe"""
        pos, size = Position.from_pos(self.pos), Size(2, self.size.width + 1)
        blocks_to_draw = []
        for po in size.height_positions():
            if po.y == self.size.width:
                blocks_to_draw.extend(self.pipe_entrance)
            else:
                blocks_to_draw.extend(self.pipe_body)

        self._confirm_render(size, pos, blocks_to_draw)


class LevelObjectLeftwardPipe(LevelObjectPipe):
    @property
    def pipe_entrance(self):
        try:
            return [self.blocks[1], self.blocks[3]]
        except IndexError:
            print(f"{self} does not have a pipe entrance")

    @property
    def pipe_body(self):
        try:
            return [self.blocks[0], self.blocks[2]]
        except IndexError:
            print(f"{self} does not have a pipe body")

    def _render(self):
        """Draws an downward pipe"""
        pos, size = Position.from_pos(self.pos), Size(self.size.width + 1, 2)
        blocks_to_draw = []
        for height in size.height_positions():
            for width in size.width_positions():
                if width.x == self.size.width:
                    blocks_to_draw.append(self.pipe_entrance[height.y])
                else:
                    blocks_to_draw.append(self.pipe_body[height.y])

        self._confirm_render(size, pos, blocks_to_draw)


class LevelObjectRightwardPipe(LevelObjectPipe):
    @property
    def pipe_entrance(self):
        try:
            return [self.blocks[0], self.blocks[2]]
        except IndexError:
            print(f"{self} does not have a pipe entrance")

    @property
    def pipe_body(self):
        try:
            return [self.blocks[1], self.blocks[3]]
        except IndexError:
            print(f"{self} does not have a pipe body")

    def _render(self):
        """Draws an downward pipe"""
        pos, size = Position.from_pos(self.pos), Size(self.size.width + 1, 2)
        blocks_to_draw = []
        for height in size.height_positions():
            for width in size.width_positions():
                if width.x == 0:
                    blocks_to_draw.append(self.pipe_entrance[height.y])
                else:
                    blocks_to_draw.append(self.pipe_body[height.y])

        self._confirm_render(size, pos, blocks_to_draw)