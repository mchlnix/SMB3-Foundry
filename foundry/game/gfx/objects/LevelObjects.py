from abc import ABC, abstractmethod
import logging

from foundry.game.File import ROM
from foundry.game.gfx.objects.LevelObject import LevelObject, SKY, GROUND, BLANK
from foundry.game.gfx.objects.ObjectLike import EXPANDS_BOTH, EXPANDS_HORIZ, EXPANDS_NOT, EXPANDS_VERT, ObjectLike

from foundry.game.Size import Size
from foundry.game.Position import Position, LevelPosition
from foundry.game.Range import Range
from foundry.game.Rect import Rect
from foundry import data_dir

logging.basicConfig(filename=data_dir.joinpath("logs/lvl_objs.log"), level=logging.CRITICAL)


class LevelObjectToSky(LevelObject):
    def _render(self):
        """
        Draws an blocks to the sky from a given y position
        Note: This class is a very unique case and needs to be updated if desired to be used by bigger applications
        """
        pos, size = Position(self.pos.x, SKY), Size(self.bmp.size.width, self.pos.y - SKY + 1)
        blocks_to_draw = []

        for _ in range(self.pos.y - SKY):
            blocks_to_draw.append(self.blocks[0])
        blocks_to_draw.append(self.blocks[1])

        self._confirm_render(size, pos, blocks_to_draw)


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
        base_size = Size(segments * segment_width, self.LINES_PER_ROW * rows_per_box + 1)

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
    VERTICAL_OFFSET = 0
    HORIZONTAL_OFFSET = 0

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
        pos = Position.from_pos(self.pos + Position(self.HORIZONTAL_OFFSET, self.VERTICAL_OFFSET))
        size = Size(self.size.width + 1, self.size.width + 1)
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
    def slope(self) -> list:
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


class LevelObjectDiagnal60(LevelObjectDiagnal):
    def slope(self) -> list:
        """The slope from self.blocks"""
        raise NotImplemented

    def body(self):
        """The body from self.blocks"""
        raise NotImplemented

    @abstractmethod
    def _render(self):
        """The render routine for the level object"""

    def render_slope(self):
        pos, size = Position.from_pos(self.pos), Size(self.size.width + 1, (self.size.width + 1) * 2)
        blocks_to_draw = [self.get_block_from_position(pos) for pos in size.positions()]
        return size, pos, blocks_to_draw

    def get_block_from_position(self, pos):
        if pos.y // 2 == pos.x:
            return self.slope[pos.y % 2]
        elif pos.y // 2 < pos.x:
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


class LevelObjectDiagnalDownRight60(DownRightDiagnal, LevelObjectDiagnal60):
    @property
    def slope(self):
        return [self.blocks[0], self.blocks[1]]

    @property
    def body(self):
        return self.blocks[2] if len(self.blocks) == 3 else BLANK


class LevelObjectDiagnalDownLeft60(DownLeftDiagnal, LevelObjectDiagnal60):
    HORZ_OFFSET = -1
    VERTICAL_OFFSET = 4

    @property
    def slope(self):
        return [self.blocks[0], self.blocks[1]]

    @property
    def body(self):
        return self.blocks[2] if len(self.blocks) == 3 else BLANK

    def _render(self):
        size, pos, blocks_to_draw = self.render_slope()
        blocks_to_draw = size.flip_rows(blocks_to_draw)
        pos = pos - Position(-self.HORZ_OFFSET, size.height - self.VERTICAL_OFFSET)
        self._confirm_render(size, pos, blocks_to_draw)


class LevelObjectDiagnalDownRight30(DownRightDiagnal, LevelObjectDiagnal30):
    @property
    def slope(self):
        return self.blocks[1:]

    @property
    def body(self):
        return self.blocks[0]


class LevelObjectDiagnalUpRight30(LevelObjectDiagnal30):
    @property
    def slope(self):
        return [self.blocks[1], self.blocks[2]]

    @property
    def body(self):
        return self.blocks[0]

    def _render(self):
        size, pos, blocks_to_draw = self.render_slope()
        blocks_to_draw = size.flip_rows(blocks_to_draw)
        blocks_to_draw.reverse()
        self._confirm_render(size, pos, blocks_to_draw)


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
        if len(self.blocks) == 2:
            return self.blocks[0]
        else:
            return BLANK

    def _render(self):
        size, pos, blocks_to_draw = self.render_slope()
        if len(self.blocks) == 1:
            pos.y -= size.height - 1
        blocks_to_draw = size.flip_rows(blocks_to_draw)
        blocks_to_draw.reverse()

        self._confirm_render(size, pos, blocks_to_draw)


class LevelObjectDiagnalUpLeft45(LevelObjectDiagnal45):
    @property
    def slope(self):
        if len(self.blocks) == 2:
            return self.blocks[0]
        else:
            return self.blocks[1]

    @property
    def body(self):
        if len(self.blocks) == 2:
            return self.blocks[1]
        else:
            return BLANK

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
        return EXPANDS_NOT

    def _render(self):
        """Draws a pyramid that expands every block"""
        pos = Position.from_pos(self.pos)
        size = Size(0, 0)
        for y in range(pos.y, (self.ground_level - 1)):
            size += Size(2, 1)
            bottom_rect = Rect.from_size_and_position(size, pos)
            if self._if_intersects(bottom_rect):
                size.height -= 1
                break
        else:
            size.height = (self.ground_level - 1) - pos.y
        pos += Position(-size.width // 2 + 1, 0)
        blocks_to_draw = []
        blank, left_slope, left_fill, right_fill, right_slope = self.blocks[0:5]

        for y in range(size.height):
            blank_blocks = (size.width - (2 * (y + 1))) // 2
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


class EndOnAllSides(LevelObject):
    def get_block_position(self, pos, size):
        offset_idx = self.bmp.size.width * self.bmp.size.height
        idx = self.bmp.size.index_position(pos % self.bmp.size) + \
              size.get_relational_position(pos // self.bmp.size) * offset_idx
        try:
            return self.blocks[idx]
        except IndexError:
            return self.blocks[0]


class EndOnTopAndBottom(LevelObject):
    def offset(self, pos, size):
        if pos.y // self.bmp.size.height == 0:
            return 0
        elif pos.y // self.bmp.size.height == size.height - 1:
            return 2
        else:
            return 1

    def get_block_position(self, pos, size):
        offset_idx = self.bmp.size.width * self.bmp.size.height
        idx = self.bmp.size.index_position(pos % self.bmp.size) + self.offset(pos, size) * offset_idx
        try:
            return self.blocks[idx]
        except IndexError:
            return self.blocks[0]


class EndOnBottom(LevelObject):
    @property
    def bottom(self):
        return 1

    @property
    def body(self):
        return 0

    def offset(self, pos, size):
        if pos.y // self.bmp.size.height == size.height - 1:
            return self.bottom
        else:
            return self.body

    def get_block_position(self, pos, size):
        offset_idx = self.bmp.size.width * self.bmp.size.height
        idx = self.bmp.size.index_position(pos % self.bmp.size) + self.offset(pos, size) * offset_idx
        try:
            return self.blocks[idx]
        except IndexError:
            return self.blocks[0]


class EndOnTop(LevelObject):
    @property
    def top(self):
        return 0

    @property
    def body(self):
        return 1

    def offset(self, pos, size):
        if pos.y // self.bmp.size.height == 0:
            return self.top
        else:
            return self.body

    def get_block_position(self, pos, size):
        offset_idx = self.bmp.size.width * self.bmp.size.height
        idx = self.bmp.size.index_position(pos % self.bmp.size) + self.offset(pos, size) * offset_idx
        try:
            return self.blocks[idx]
        except IndexError:
            return self.blocks[0]


class EndOnDoubleTop(LevelObject):
    @property
    def top(self):
        return 0

    @property
    def second_top(self):
        return 1

    @property
    def body(self):
        return 2

    def offset(self, pos, size):
        if pos.y // self.bmp.size.height == 0:
            return self.top
        elif pos.y // self.bmp.size.height == 1:
            return self.second_top
        else:
            return self.body

    def get_block_position(self, pos, size):
        offset_idx = self.bmp.size.width * self.bmp.size.height
        idx = self.bmp.size.index_position(pos % self.bmp.size) + self.offset(pos, size) * offset_idx
        try:
            return self.blocks[idx]
        except IndexError:
            return self.blocks[0]


class LevelObjectVertical(LevelObject):
    def expands(self):
        return EXPANDS_VERT

    def primary_expansion(self):
        if self.is_4byte:
            return EXPANDS_HORIZ | EXPANDS_VERT
        else:
            return EXPANDS_VERT

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

    def get_block_position(self, pos, size):
        idx = self.bmp.size.index_position(pos % self.bmp.size)
        try:
            return self.blocks[idx]
        except IndexError:
            return self.blocks[0]

    def get_blocks(self, size):
        return [self.get_block_position(po, size) for po in size.positions()]

    def _render(self):
        """Draws an blocks to the sky from a given y position"""
        pos, size = Position.from_pos(self.pos), self.bmp.size * (self.size.invert() + Size(1, 1))
        blocks_to_draw = self.get_blocks(size)
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


class LevelObjectVerticalWithTop(EndOnTop, LevelObjectVertical):
    pass


class LevelObjectVerticalWithDoubleTop(EndOnDoubleTop, LevelObjectVertical):
    pass


class LevelObjectVerticalWithAllSides(EndOnAllSides, LevelObjectVertical):
    pass


class LevelObjectVerticalWithTopAndBottom(EndOnTopAndBottom, LevelObjectVertical):
    pass


class LevelObjectVerticalWithBottom(EndOnBottom, LevelObjectVertical):
    pass


class LevelObjectHorizontal(LevelObject):
    def expands(self):
        return EXPANDS_HORIZ

    def primary_expansion(self):
        return EXPANDS_HORIZ | EXPANDS_VERT if self.is_4byte else EXPANDS_HORIZ

    def get_block_position(self, pos, size):
        idx = self.bmp.size.index_position(pos % self.bmp.size)
        try:
            return self.blocks[idx]
        except IndexError:
            try:
                return self.blocks[0]
            except IndexError:
                print(self, "does not have any blocks")

    def get_blocks(self, size):
        return [self.get_block_position(po, size) for po in size.positions()]

    def _render(self):
        """Draws an blocks to the sky from a given y position"""
        pos, size = Position.from_pos(self.pos), self.bmp.size * (self.size + Size(1, 1))
        blocks_to_draw = self.get_blocks(size)
        self._confirm_render(size, pos, blocks_to_draw)


class LevelObjectHorizontal5Byte(LevelObjectHorizontal):
    def get_block_position(self, pos, size):
        idx = self.bmp.size.index_position(pos % self.bmp.size)
        try:
            return self.overflow[idx]
        except IndexError:
            try:
                return 0
            except IndexError:
                print(self, "does not have any blocks")


class LevelObjectHorizontalWithTop(EndOnTop, LevelObjectHorizontal):
    pass


class LevelObjectHorizontalWithBottom(EndOnBottom, LevelObjectHorizontal):
    pass


class LevelObjectHorizontalWithAllSides(EndOnAllSides, LevelObjectHorizontal):
    pass


class EndOnSides(LevelObject):
    @property
    def left_offset(self):
        return 0

    @property
    def right_offset(self):
        return 2

    @property
    def body_offset(self):
        return 1

    def offset(self, pos, size):
        if pos.x // self.bmp.size.width == 0:
            return self.left_offset
        elif pos.x // self.bmp.size.width == size.width - 1:
            return self.right_offset
        else:
            return self.body_offset

    def get_block_position(self, pos, size):
        offset_idx = self.bmp.size.width * self.bmp.size.height
        idx = self.bmp.size.index_position(pos % self.bmp.size) + self.offset(pos, size) * offset_idx
        try:
            return self.blocks[idx]
        except IndexError:
            return self.blocks[0]


class LevelObjectHorizontalWithSides(EndOnSides, LevelObjectHorizontal):
    pass


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


class LevelObjectHorizontalToGround(LevelObjectHorizontalWithAllSides):
    def _render(self):
        """Draws an blocks to the sky from a given y position"""
        pos = Position.from_pos(self.pos)
        size = self.size if self.is_single_block else self.size + Size(1, 0)
        for y in range(pos.y, self.ground_level):
            size.height += 1
            bottom_rect = Rect.from_size_and_position(size, pos)
            if self._if_intersects(bottom_rect):
                size.height -= 1
                break
        else:
            size.height = self.ground_level - pos.y
        blocks_to_draw = self.get_blocks(size)
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


class LevelObjectFillBackgroundHorizontalLevel(LevelObject):
    def _render(self):
        self.pos = Position(0, 0)
        self.size = Size(16 * 15, 26)
        blocks = [self.blocks[0] for _ in range(16 * 15 * 26)]
        self._confirm_render(self.size, self.pos, blocks)


class LevelObjectPipe(LevelObject):
    def expands(self):
        return EXPANDS_HORIZ

    def primary_expansion(self):
        return EXPANDS_HORIZ

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
                blocks_to_draw.extend(self.pipe_body)
            else:
                blocks_to_draw.extend(self.pipe_entrance)

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