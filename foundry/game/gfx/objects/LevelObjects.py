from abc import ABC, abstractmethod
import logging

from foundry.game.File import ROM
from foundry.game.gfx.objects.LevelObject import LevelObject, SKY, GROUND, BLANK
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

    def __repr__(self):
        return f"LevelObjectToSky {self.description} at {self.x_position}, {self.y_position}"

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

    def __repr__(self):
        return f"LevelObjectDesertPipeBox {self.description} at {self.x_position}, {self.y_position}"


class LevelObjectDiagnal(LevelObject):
    def _render(self):
        """Base render function for diagnal blocks, useless unless extended"""
        pos, size = Position.from_pos(self.pos), Size.from_size(self.bmp.size)
        rows = []

        ending_functions = {
            UNIFORM: self._render_uniform,
            END_ON_TOP_OR_LEFT: self._render_end_on_top_or_left,
            END_ON_BOTTOM_OR_RIGHT: self._render_end_on_bottom_or_right,
            TWO_ENDS: self._render_two_ends
        }
        base_size, left, right, slopes = ending_functions[self.ending]()

        slope_width = size.width if size.height > size.width else len(slopes)
        for elevation in range(base_size.height):
            amount_right = (elevation // size.height) * slope_width
            amount_left = base_size.width - slope_width - amount_right
            offset = elevation % size.height
            rows.append(amount_left * left + slopes[offset: offset + slope_width] + amount_right * right)

        return base_size, pos, rows, slope_width

    def _render_uniform(self):
        """Update values for the ending UNIFORM"""
        base_size = Size((self.size.width + 1) * self.bmp.size.width, (self.size.width + 1) * self.bmp.size.height)
        left, right, slopes = [BLANK], [BLANK], self.blocks
        return base_size, left, right, slopes

    @abstractmethod
    def _render_end_on_top_or_left(self):
        """Updates values for the ending END_ON_TOP_OR_LEFT"""

    def _render_end_on_bottom_or_right(self):
        """Updates values for the ending END_ON_BOTTOM_OR_RIGHT"""
        width = (self.size.width + 1)
        base_size = Size(width * (self.bmp.size.width - 1), width * self.bmp.size.height)  # without fill block
        fill_block = self.blocks[-1:]
        left, right, slopes = [BLANK], fill_block, self.blocks[0:-1]
        return base_size, left, right, slopes

    def _render_two_ends(self):
        """Updates values for the ending TWO_ENDS"""
        raise NotImplementedError  # todo add two ends functionality

    def __repr__(self):
        return f"LevelObjectDiagnal {self.description} at {self.x_position}, {self.y_position}"


class LevelObjectDiagnalDownLeft(LevelObjectDiagnal):
    def _render(self):
        blocks_to_draw = []
        base_size, pos, rows, slope_width = super()._render()
        pos.x -= base_size.width - slope_width
        for row in rows:
            blocks_to_draw.extend(row)

        self._confirm_render(base_size, pos, blocks_to_draw)

    def _render_end_on_top_or_left(self):
        """Updates values for the ending END_ON_TOP_OR_LEFT"""
        return self._render_end_on_bottom_or_right()

    def __repr__(self):
        return f"LevelObjectDiagnalDownLeft {self.description} at {self.x_position}, {self.y_position}"


class LevelObjectDiagnalDownRight(LevelObjectDiagnal):
    def _render(self):
        blocks_to_draw = []
        size, pos, rows, slope_width = super()._render()
        if not self.bmp.size.height > self.bmp.size.width:  # special case for 60 degree platform wire down right
            rows.reverse()

        pos.x -= size.height - 1
        for row in rows:
            blocks_to_draw.extend(row)

        self._confirm_render(size, pos, blocks_to_draw)

    def _render_end_on_top_or_left(self):
        """Updates values for the ending END_ON_TOP_OR_LEFT"""
        base_size = Size((self.size.width + 1) * self.bmp.size.width, (self.size.width + 1) * self.bmp.size.height)
        fill_block = self.blocks[0:1]
        left, right, slopes = fill_block, [BLANK], self.blocks[1:]
        return base_size, left, right, slopes

    def __repr__(self):
        return f"LevelObjectDiagnalDownRight {self.description} at {self.x_position}, {self.y_position}"


class LevelObjectDiagnalUpRight(LevelObjectDiagnal):
    def _render(self):
        blocks_to_draw = []
        base_size, pos, rows, slope_width = super()._render()

        for row in rows:
            row.reverse()
        if not self.bmp.size.height > self.bmp.size.width:  # special case for 60 degree platform wire down right
            rows.reverse()
        pos.y -= base_size.height - 1

        for row in rows:
            blocks_to_draw.extend(row)

        self._confirm_render(base_size, pos, blocks_to_draw)

    def _render_end_on_top_or_left(self):
        """Updates values for the ending END_ON_TOP_OR_LEFT"""
        base_size = Size((self.size.width + 1) * self.bmp.size.width, (self.size.width + 1) * self.bmp.size.height)
        fill_block = self.blocks[0:1]
        left, right, slopes = fill_block, [BLANK], self.blocks[1:]
        return base_size, left, right, slopes

    def __repr__(self):
        return f"LevelObjectDiagnalUpRight {self.description} at {self.x_position}, {self.y_position}"


class LevelObjectDiagnalWeird(LevelObjectDiagnal):
    def _render(self):
        blocks_to_draw = []
        base_size, pos, rows, slope_width = super()._render()

        for row in rows:
            blocks_to_draw.extend(row)

        self._confirm_render(base_size, pos, blocks_to_draw)

    def _render_end_on_top_or_left(self):
        """Updates values for the ending END_ON_TOP_OR_LEFT"""
        base_size = Size((self.size.width + 1) * self.bmp.size.width, (self.size.width + 1) * self.bmp.size.height)
        fill_block = self.blocks[0:1]
        left, right, slopes = fill_block, [BLANK], self.blocks[1:]
        return base_size, left, right, slopes

    def __repr__(self):
        return f"LevelObjectDiagnalWeird {self.description} at {self.x_position}, {self.y_position}"


class LevelObjectPyramidToGround(LevelObject):
    """Makes a pyramid that grows horizontally in both directions that extends to the ground"""
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

    def __repr__(self):
        return f"LevelObjectPyramidToGround {self.description} at {self.x_position}, {self.y_position}"


class LevelObjectEndingBackground(LevelObject):
    GROUND = 26
    ENDING_GRAPHIC_HEIGHT = 6
    FLOOR_HEIGHT = 1

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

    def __repr__(self):
        return f"LevelObjectEndingBackground {self.description} at {self.x_position}, {self.y_position}"


class LevelObjectVertical(LevelObject):
    @property
    def height_leng(self):
        # invert height and length
        return self.length

    @height_leng.setter
    def height_leng(self, value):
        # invert height and length
        self.length = value

    @property
    def hlength(self):
        # invert height and length
        return self.height_len

    @hlength.setter
    def hlength(self, value):
        # invert height and length
        self.height_len = value

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
            for _ in range(self.width):
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
        additional_rows = size.height - self.height

        # assume only the first row needs to repeat
        # todo true for giant blocks?
        if additional_rows > 0:
            last_row = self.blocks[0: self.width]
            for _ in range(additional_rows):
                blocks_to_draw.extend(last_row)

        # in case the drawn object is smaller than its actual size
        for y in range(min(self.height, size.height)):
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
                blocks_to_draw.extend(self.blocks[-2 * self.width: -self.width])

        if size.height > 1:
            blocks_to_draw.extend(bottom_row)
        return pos, size, blocks_to_draw

    def __repr__(self):
        return f"LevelObjectVertical {self.description} at {self.x_position}, {self.y_position}"


class LevelObjectHorizontal(LevelObject):
    def _render(self):
        """Draws an blocks to the sky from a given y position"""
        pos, size = Position.from_pos(self.pos), self.bmp.size + Size(self.size.width, self.size.height)
        blocks_to_draw = []

        ending_functions = {
            UNIFORM: self._render_uniform,
            END_ON_TOP_OR_LEFT: self._render_end_on_top_or_left,
            END_ON_BOTTOM_OR_RIGHT: self._render_end_on_bottom_or_right,
            TWO_ENDS: self._render_two_ends
        }
        pos, size, blocks_to_draw = ending_functions[self.ending](pos, size, blocks_to_draw)

        self._confirm_render(size, pos, blocks_to_draw)

    @property
    def top_block(self):
        return self.blocks[0:1]

    @property
    def bottom_block(self):
        return self.blocks[-1:]

    def _render_uniform(self, pos, size, blocks_to_draw):
        """Update values for the ending UNIFORM"""
        if self.is_4byte:
            # ceilings are one shorter than normal
            if self.bmp.size.height > self.bmp.size.width:
                size.height -= 1

            for po in size.positions():
                blocks_to_draw.append(self.top_block if po.y == 0 else self.bottom_block)
        else:
            for po in size.positions():
                try:
                    blocks_to_draw.append(self.blocks[0])
                except IndexError:
                    blocks_to_draw.append(0)

        return pos, size, blocks_to_draw

    def _render_end_on_top_or_left(self, pos, size, blocks_to_draw):
        """Updates values for the ending END_ON_TOP_OR_LEFT"""
        blocks = self.get_block_from_position()
        for po in size.positions():
            blocks_to_draw.append(blocks[size.get_relational_position(po)])
        return pos, size, blocks_to_draw

    def _render_end_on_bottom_or_right(self, pos, size, blocks_to_draw):
        """Updates values for the ending END_ON_BOTTOM_OR_RIGHT"""
        blocks = self.get_block_from_position(overload=1)
        for po in size.positions():
            blocks_to_draw.append(blocks[size.get_relational_position(po)])
        return pos, size, blocks_to_draw

    def get_block_from_position(self, overload=0):
        """
        Provides the correct blocks for the provided amount
        :param List blocks: The blocks provided
        :return: The blocks
        :rtype: List
        """
        if len(self.blocks) == 9:
            lt, mt, rt, lm, mm, rm, lb, mb, rb = self.blocks
        elif len(self.blocks) == 6:
            lt, mt, rt, lb, mb, rb = self.blocks
            lm, mm, rm = lb, mb, rb
        elif len(self.blocks) == 4:
            if overload == 0:
                lt, mt, lb, mb = self.blocks
                rt, rb = mt, mb
            else:
                lt, rt, lb, rb = self.blocks
                mt, mb = rt, rb
            lm, mm, rm = lb, mb, rb
        elif len(self.blocks) == 3:
            lt, mt, rt = self.blocks
            lb, mb, rb, lm, mm, rm = lt, mt, rt, lt, mt, rt
        else:
            lt, mt = self.blocks
            lb, lm = lt, lt
            mb, mm, rb, rm, rt = mt, mt, mt, mt, mt

        return [lt, mt, rt, lm, mm, rm, lb, mb, rb]

    def _render_two_ends(self, pos, size, blocks_to_draw):
        """Updates values for the ending TWO_ENDS"""
        blocks = self.get_block_from_position()
        for po in size.positions():
            blocks_to_draw.append(blocks[size.get_relational_position(po)])
        return pos, size, blocks_to_draw

    def __repr__(self):
        return f"LevelObjectHorizontal {self.description} at {self.x_position}, {self.y_position}"


class LevelObjectHorizontalToGround(LevelObjectHorizontal):
    def _render(self):
        """Draws a horizontal block to the ground"""
        pos, size = Position.from_pos(self.pos), self.bmp.size + Size(self.size.width - 1, self.size.height)
        blocks_to_draw = []

        print(f"{self}")
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
            size.width = self.length

        ending_functions = {
            UNIFORM: self._render_uniform,
            END_ON_TOP_OR_LEFT: self._render_end_on_top_or_left,
            END_ON_BOTTOM_OR_RIGHT: self._render_end_on_bottom_or_right,
            TWO_ENDS: self._render_two_ends
        }
        pos, size, blocks_to_draw = ending_functions[self.ending](pos, size, blocks_to_draw)

        self._confirm_render(size, pos, blocks_to_draw)

    def __repr__(self):
        return f"LevelObjectHorizontalToGround {self.description} at {self.x_position}, {self.y_position}"


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

    def __repr__(self):
        return f"LevelObjectHorizontalAlt {self.description} at {self.x_position}, {self.y_position}"


class SingleBlock(LevelObject):
    def _render(self):
        """Draws a singular block"""
        self._confirm_render(self.bmp.size, self.pos, self.blocks)

    def __repr__(self):
        return f"SingleBlock {self.description} at {self.x_position}, {self.y_position}"
