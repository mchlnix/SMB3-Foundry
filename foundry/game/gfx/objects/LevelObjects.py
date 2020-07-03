from typing import List, Tuple, Union, Optional
from abc import abstractmethod
import logging

from foundry.game.File import ROM
from foundry.game.gfx.objects.LevelObject import LevelObject, SKY, GROUND, BLANK
from foundry.game.gfx.objects.ObjectLike import EXPANDS_BOTH, EXPANDS_HORIZ, EXPANDS_NOT, EXPANDS_VERT

from foundry.game.Size import Size
from foundry.game.Position import Position, LevelPosition
from foundry.game.Range import Range
from foundry.game.Rect import Rect
from foundry import data_dir

logging.basicConfig(filename=data_dir.joinpath("logs/lvl_objs.log"), level=logging.CRITICAL)


class LevelObjectToSky(LevelObject):
    def icon(self) -> None:
        self.size = Size(1, 2)
        self._render(False)

    def _render(self, regular: bool = True) -> None:
        """
        Draws an blocks to the sky from a given y position
        Note: This class is a very unique case and needs to be updated if desired to be used by bigger applications
        """
        if regular:
            pos, size = Position(self.pos.x, SKY), Size(self.bmp.size.width, self.pos.y - SKY + 1)
            blocks_to_draw = []

            for _ in range(self.pos.y - SKY):
                blocks_to_draw.append(self.blocks[0])
            blocks_to_draw.append(self.blocks[1])
        else:
            pos, size = Position.from_pos(self.pos), Size.from_size(self.size)
            blocks_to_draw = self.blocks
        self._confirm_render(size, pos, blocks_to_draw)


class LevelObjectDesertPipeBox(LevelObject):
    LINES_PER_ROW = 4

    def _render(self) -> None:
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

    @property
    @abstractmethod
    def slope(self) -> int:
        """The slope from self.blocks"""

    @property
    @abstractmethod
    def body(self) -> int:
        """The body from self.blocks"""

    @abstractmethod
    def _render(self) -> None:
        """The render routine for the level object"""

    @abstractmethod
    def get_block_from_position(self, pos: Position) -> int:
        """Returns the corresponding block for a given position"""

    def expands(self) -> int:
        return EXPANDS_HORIZ

    def primary_expansion(self) -> int:
        return EXPANDS_HORIZ

    @abstractmethod
    def render_slope(self) -> Tuple[Size, Position, List[int]]:
        """Returns the size, pos, and blocks_to_draw of the rendered slope"""


class LevelObjectDiagnal45(LevelObjectDiagnal):
    @property
    @abstractmethod
    def slope(self) -> int:
        """The slope from self.blocks"""

    @property
    @abstractmethod
    def body(self) -> int:
        """The body from self.blocks"""

    @abstractmethod
    def _render(self) -> None:
        """The render routine for the level object"""

    def render_slope(self) -> Tuple[Size, Position, List[int]]:
        pos = Position.from_pos(self.pos + Position(self.HORIZONTAL_OFFSET, self.VERTICAL_OFFSET))
        size = Size(self.size.width + 1, self.size.width + 1)
        blocks_to_draw = [self.get_block_from_position(pos) for pos in size.positions()]
        return size, pos, blocks_to_draw

    def get_block_from_position(self, pos: Position) -> int:
        if pos.x == pos.y:
            return self.slope
        elif pos.x < pos.y:
            return self.body
        else:
            return BLANK


class LevelObjectDiagnal30(LevelObjectDiagnal):
    @property
    @abstractmethod
    def slope(self) -> List[int]:
        """The slope from self.blocks"""

    @property
    @abstractmethod
    def body(self) -> int:
        """The body from self.blocks"""

    @abstractmethod
    def _render(self) -> None:
        """The render routine for the level object"""

    def render_slope(self) -> Tuple[Size, Position, List[int]]:
        pos, size = Position.from_pos(self.pos), Size((self.size.width + 1) * 2, self.size.width + 1)
        blocks_to_draw = [self.get_block_from_position(pos) for pos in size.positions()]
        return size, pos, blocks_to_draw

    def get_block_from_position(self, pos: Position) -> int:
        if pos.x // 2 == pos.y:
            return self.slope[pos.x % 2]
        elif pos.x // 2 < pos.y:
            return self.body
        else:
            return BLANK


class LevelObjectDiagnal60(LevelObjectDiagnal):
    @property
    @abstractmethod
    def slope(self) -> List[int]:
        """The slope from self.blocks"""
        return []

    @property
    @abstractmethod
    def body(self) -> Optional[int]:
        """The body from self.blocks"""
        return None

    @abstractmethod
    def _render(self) -> None:
        """The render routine for the level object"""

    def render_slope(self) -> Tuple[Size, Position, List[int]]:
        pos, size = Position.from_pos(self.pos), Size(self.size.width + 1, (self.size.width + 1) * 2)
        blocks_to_draw = [self.get_block_from_position(pos) for pos in size.positions()]
        return size, pos, blocks_to_draw

    def get_block_from_position(self, pos: Position) -> int:
        if pos.y // 2 == pos.x:
            return self.slope[(pos.y % 2)]
        elif pos.y // 2 < pos.x:
            return self.body
        else:
            return BLANK


class DownRightDiagnal(LevelObjectDiagnal):
    def _render(self) -> None:
        self._confirm_render(*self.render_slope())


class DownLeftDiagnal(LevelObjectDiagnal):
    HORZ_OFFSET = 0

    def _render(self) -> None:
        size, pos, blocks_to_draw = self.render_slope()
        blocks_to_draw = size.flip_rows(blocks_to_draw)
        pos = pos - Position(size.width - self.HORZ_OFFSET, 0)
        self._confirm_render(size, pos, blocks_to_draw)


class LevelObjectDiagnalDownLeft45(DownLeftDiagnal, LevelObjectDiagnal45):
    HORZ_OFFSET = 1

    @property
    def slope(self) -> int:
        return self.blocks[0]

    @property
    def body(self) -> int:
        return self.blocks[1] if len(self.blocks) == 2 else BLANK


class LevelObjectDiagnalDownLeft30(DownLeftDiagnal, LevelObjectDiagnal30):
    HORZ_OFFSET = 2

    @property
    def slope(self) -> List[int]:
        return [self.blocks[1], self.blocks[0]]

    @property
    def body(self) -> int:
        return self.blocks[2] if len(self.blocks) == 3 else BLANK


class LevelObjectDiagnalDownRight60(DownRightDiagnal, LevelObjectDiagnal60):
    @property
    def slope(self) -> List[int]:
        return [self.blocks[0], self.blocks[1]]

    @property
    def body(self) -> int:
        return self.blocks[2] if len(self.blocks) == 3 else BLANK


class LevelObjectDiagnalDownLeft60(DownLeftDiagnal, LevelObjectDiagnal60):
    HORZ_OFFSET = -1
    VERTICAL_OFFSET = 4

    @property
    def slope(self) -> List[int]:
        return [self.blocks[0], self.blocks[1]]

    @property
    def body(self) -> List[int]:
        return self.blocks[2] if len(self.blocks) == 3 else BLANK

    def _render(self) -> None:
        size, pos, blocks_to_draw = self.render_slope()
        blocks_to_draw = size.flip_rows(blocks_to_draw)
        pos = pos - Position(-self.HORZ_OFFSET, size.height - self.VERTICAL_OFFSET)
        self._confirm_render(size, pos, blocks_to_draw)


class LevelObjectDiagnalDownRight30(DownRightDiagnal, LevelObjectDiagnal30):
    @property
    def slope(self) -> List[int]:
        return self.blocks[1:]

    @property
    def body(self) -> int:
        return self.blocks[0]


class LevelObjectDiagnalUpRight30(LevelObjectDiagnal30):
    @property
    def slope(self) -> List[int]:
        return [self.blocks[1], self.blocks[2]]

    @property
    def body(self) -> int:
        return self.blocks[0]

    def _render(self) -> None:
        size, pos, blocks_to_draw = self.render_slope()
        blocks_to_draw = size.flip_rows(blocks_to_draw)
        blocks_to_draw.reverse()
        self._confirm_render(size, pos, blocks_to_draw)


class LevelObjectDiagnalUpLeft30(LevelObjectDiagnal30):
    @property
    def slope(self) -> List[int]:
        return [self.blocks[1], self.blocks[0]]

    @property
    def body(self) -> int:
        return self.blocks[2]

    def _render(self) -> None:
        size, pos, blocks_to_draw = self.render_slope()
        blocks_to_draw.reverse()
        self._confirm_render(size, pos, blocks_to_draw)


class LevelObjectDiagnalDownRight45(DownRightDiagnal, LevelObjectDiagnal45):
    @property
    def slope(self) -> int:
        return self.blocks[1] if len(self.blocks) == 2 else self.blocks[0]

    @property
    def body(self) -> int:
        return self.blocks[0] if len(self.blocks) == 2 else BLANK


class LevelObjectDiagnalUpRight45(LevelObjectDiagnal45):
    @property
    def slope(self) -> int:
        if len(self.blocks) == 2:
            return self.blocks[1]
        else:
            return self.blocks[0]

    @property
    def body(self) -> int:
        if len(self.blocks) == 2:
            return self.blocks[0]
        else:
            return BLANK

    def _render(self) -> None:
        size, pos, blocks_to_draw = self.render_slope()
        if len(self.blocks) == 1:
            pos.y -= size.height - 1
        blocks_to_draw = size.flip_rows(blocks_to_draw)
        blocks_to_draw.reverse()

        self._confirm_render(size, pos, blocks_to_draw)


class LevelObjectDiagnalUpLeft45(LevelObjectDiagnal45):
    @property
    def slope(self) -> int:
        if len(self.blocks) == 2:
            return self.blocks[0]
        else:
            return self.blocks[1]

    @property
    def body(self) -> int:
        if len(self.blocks) == 2:
            return self.blocks[1]
        else:
            return BLANK

    def _render(self) -> None:
        size, pos, blocks_to_draw = self.render_slope()
        blocks_to_draw.reverse()

        self._confirm_render(size, pos, blocks_to_draw)


class LevelObjectDiagnalWeird45(LevelObjectDiagnal45):
    @property
    def slope(self) -> int:
        if len(self.blocks) == 2:
            return self.blocks[1]
        else:
            return self.blocks[0]

    @property
    def body(self) -> int:
        try:
            return self.blocks[0]
        except IndexError:
            return 0

    def expands(self) -> int:
        return EXPANDS_HORIZ | EXPANDS_VERT

    def _render(self) -> None:
        size, pos, blocks_to_draw = self.render_slope()

        self._confirm_render(size, pos, blocks_to_draw)


class LevelObjectPyramidToGround(LevelObject):
    """Makes a pyramid that grows horizontally in both directions that extends to the ground"""
    def expands(self) -> int:
        return EXPANDS_NOT

    def _render(self) -> None:
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

    def expands(self) -> int:
        return EXPANDS_HORIZ

    @property
    def fade_tile(self) -> int:
        return self.blocks[0]

    @property
    def background(self) -> int:
        return self.blocks[1]

    @property
    def page_limit(self) -> int:
        return LevelPosition.SCREEN_WIDTH - (self.x_pos % LevelPosition.SCREEN_WIDTH)

    @property
    def rom_offset(self) -> int:
        return self.object_set.get_ending_offset()

    def _render(self) -> None:
        """Draws the end of level background"""
        posi, size = LevelPosition.from_pos(self.pos), Size.from_size(self.bmp.size)

        rect = Rect.from_size_and_position(Size(LevelPosition.SCREEN_WIDTH + posi.rel_x_inverse, self.GROUND),
                                           Position(0, 0))

        blocks_to_draw = [self.fade_tile if pos.x == 0 else self.background for pos in rect.positions()]

        rom = ROM()
        bg_rect = Rect.from_size_and_position(
            Size(LevelPosition.SCREEN_WIDTH, self.ENDING_GRAPHIC_HEIGHT),
            Position(self.page_limit + 1, self.GROUND - self.ENDING_GRAPHIC_HEIGHT)
        )

        for i, pos in enumerate(bg_rect.positions()):
            block = rom.get_byte(self.rom_offset + i - 1)
            try:
                idx = rect.index_position(pos)
                if blocks_to_draw[idx] != self.fade_tile:
                    blocks_to_draw[idx] = block
            except IndexError:
                pass

        self._confirm_render(rect.abs_size, Position(posi.x, 0), blocks_to_draw)


class EndOnAllSides(LevelObject):
    def icon(self) -> None:
        self.size = Size(2, 2)
        self.render()

    def get_block_position(self, pos: Position, size: Size, offset_idx: Optional[int] = None):
        if offset_idx is None:
            offset_idx = self.bmp.size.width * self.bmp.size.height
        idx = self.bmp.size.index_position(pos % self.bmp.size) + \
            size.get_relational_position(pos // self.bmp.size) * offset_idx
        try:
            return self.blocks[idx]
        except IndexError:
            return self.blocks[0]


class LevelObjectBlockGetter(LevelObject):
    @abstractmethod
    def offset(self, pos: Position, size: Size) -> int:
        """Finds the correct offset for a tile"""

    def get_block_position(self, pos: Position, size: Size, offset_idx: Optional[int] = None) -> int:
        """Gets a block at a specific position"""
        if offset_idx is None:
            offset_idx = self.bmp.size.width * self.bmp.size.height
        idx = self.bmp.size.index_position(pos % self.bmp.size) + self.offset(pos, size) * offset_idx
        try:
            return self.blocks[idx]
        except IndexError:
            return self.blocks[0]

    def get_blocks(self, size: Size) -> List[int]:
        """Returns every block for a given size"""
        offset_idx = self.bmp.size.width * self.bmp.size.height
        return [self.get_block_position(pos, size, offset_idx) for pos in size.positions()]


class EndOnTopAndBottom(LevelObjectBlockGetter):
    def icon(self) -> None:
        self.size = Size(2, 0)
        self.render()

    def offset(self, pos: Position, size: Size) -> int:
        if pos.y // self.bmp.size.height == 0:
            return 0
        elif pos.y // self.bmp.size.height == size.height - 1:
            return 2
        else:
            return 1


class EndOnBottom(LevelObjectBlockGetter):
    def icon(self) -> None:
        self.size = Size(1, 1)
        self.render()

    @property
    def bottom(self) -> int:
        return 1

    @property
    def body(self) -> int:
        return 0

    def offset(self, pos: Position, size: Size) -> int:
        if pos.y // self.bmp.size.height == size.height - 1:
            return self.bottom
        else:
            return self.body


class EndOnTop(LevelObjectBlockGetter):
    def icon(self) -> None:
        self.size = Size(1, 1)
        self.render()

    @property
    def top(self) -> int:
        return 0

    @property
    def body(self) -> int:
        return 1

    def offset(self, pos: Position, _) -> int:
        if pos.y // self.bmp.size.height == 0:
            return self.top
        else:
            return self.body


class EndOnDoubleTop(LevelObjectBlockGetter):
    def icon(self) -> None:
        self.size = Size(2, 0)
        self.render()

    @property
    def top(self) -> int:
        return 0

    @property
    def second_top(self) -> int:
        return 1

    @property
    def body(self) -> int:
        return 2

    def offset(self, pos, _):
        if pos.y // self.bmp.size.height == 0:
            return self.top
        elif pos.y // self.bmp.size.height == 1:
            return self.second_top
        else:
            return self.body


class EndOnSides(LevelObjectBlockGetter):
    def icon(self) -> None:
        self.size = Size(2, 0)
        self.render()

    @property
    def left_offset(self) -> int:
        return 0

    @property
    def right_offset(self) -> int:
        return 2

    @property
    def body_offset(self) -> int:
        return 1

    def offset(self, pos: Position, size: Size) -> int:
        if pos.x // self.bmp.size.width == 0:
            return self.left_offset
        elif pos.x // self.bmp.size.width == size.width - 1:
            return self.right_offset
        else:
            return self.body_offset


class VerticalLevelObject:
    def expands(self) -> int:
        return EXPANDS_VERT

    def primary_expansion(self) -> int:
        if self.is_4byte:
            return EXPANDS_HORIZ | EXPANDS_VERT
        else:
            return EXPANDS_VERT


class LevelObjectVertical(LevelObjectBlockGetter, VerticalLevelObject):
    def icon(self) -> None:
        self.size = Size(0, 0)
        self.render()

    def offset(self, *_) -> int:
        return 0

    def _render(self) -> None:
        """Draws blocks vertically"""
        pos, size = Position.from_pos(self.pos), self.bmp.size * (self.size.invert() + Size(1, 1))
        blocks_to_draw = self.get_blocks(size)
        self._confirm_render(size, pos, blocks_to_draw)


class LevelObjectVerticalWithTop(EndOnTop, LevelObjectVertical):
    """Vertical generator with a custom top"""


class LevelObjectVerticalWithDoubleTop(EndOnDoubleTop, LevelObjectVertical):
    """Vertical generator with two custom tops"""


class LevelObjectVerticalWithAllSides(EndOnAllSides, LevelObjectVertical):
    """Vertical generator with custom sides and edges"""


class LevelObjectVerticalWithTopAndBottom(EndOnTopAndBottom, LevelObjectVertical):
    """Vertical generator with a custom bottom and top"""


class LevelObjectVerticalWithBottom(EndOnBottom, LevelObjectVertical):
    """Vertical generator with a custom bottom"""


class HorizontalLevelObject:
    def expands(self) -> int:
        return EXPANDS_HORIZ

    def primary_expansion(self) -> int:
        return EXPANDS_HORIZ | EXPANDS_VERT if self.is_4byte else EXPANDS_HORIZ


class LevelObjectHorizontal(LevelObjectBlockGetter, HorizontalLevelObject):
    def icon(self) -> None:
        self.size = Size(0, 0)
        self.render()

    def offset(self, *_) -> int:
        return 0

    def _render(self) -> None:
        """Draws an blocks to the sky from a given y position"""
        pos, size = Position.from_pos(self.pos), self.bmp.size * (self.size + Size(1, 1))
        blocks_to_draw = self.get_blocks(size)
        self._confirm_render(size, pos, blocks_to_draw)


class LevelObjectHorizontal5Byte(LevelObjectHorizontal):
    """An object that has an additional byte to determine the block displayed"""
    def get_block_position(self, pos: Position, *_) -> int:
        idx = self.bmp.size.index_position(pos % self.bmp.size)
        try:
            return self.overflow[idx]
        except IndexError:
            return 0


class LevelObjectHorizontalWithTop(EndOnTop, LevelObjectHorizontal):
    """Horizontal generator with a custom top"""


class LevelObjectHorizontalWithBottom(EndOnBottom, LevelObjectHorizontal):
    """Horizontal generator with a custom bottom"""


class LevelObjectHorizontalWithAllSides(EndOnAllSides, LevelObjectHorizontal):
    """Horizontal generator with custom sides and edges"""


class LevelObjectHorizontalWithSides(EndOnSides, LevelObjectHorizontal):
    pass


class LevelObjectHorizontalWithSidesAndTop(LevelObjectHorizontal):
    @property
    def left(self) -> int:
        return self.blocks[0]

    @property
    def right(self) -> int:
        return self.blocks[2] if len(self.blocks) == 3 else self.blocks[0]

    @property
    def body(self) -> int:
        return self.blocks[1] if len(self.blocks) == 3 else self.blocks[0]

    def get_block_position(self, pos: Position, size: Size, *_) -> int:
        if pos.x == 0:
            return self.left
        elif pos.x == size.width - 1:
            return self.right
        else:
            return self.body


class LevelObjectHorizontalToGround(LevelObjectHorizontalWithAllSides):
    def icon(self) -> None:
        self.size = Size(3, 3)
        self._render(False)

    def _icon_render(self) -> None:
        """Draws an blocks to the sky from a given y position"""
        pos = Position.from_pos(self.pos)
        size = self.size
        blocks_to_draw = self.get_blocks(size)
        self._confirm_render(size, pos, blocks_to_draw)

    def _render(self, regular: bool = True) -> None:
        """Draws an blocks to the sky from a given y position"""
        if regular:
            pos = Position.from_pos(self.pos)
            size = self.size if self.is_single_block else self.size + Size(1, 0)
            for _ in range(pos.y, self.ground_level):
                size.height += 1
                bottom_rect = Rect.from_size_and_position(size, pos)
                if self._if_intersects(bottom_rect):
                    size.height -= 1
                    break
            else:
                size.height = self.ground_level - pos.y
            blocks_to_draw = self.get_blocks(size)
        else:
            pos = Position.from_pos(self.pos)
            size = Size.from_size(self.size)
            blocks_to_draw = self.get_blocks(size)
        self._confirm_render(size, pos, blocks_to_draw)


class LevelObjectPlainsPlatformFloating(LevelObject):
    def icon(self) -> None:
        self.size = Size(2, 2)
        self.render()

    @property
    def main_blocks(self) -> List[int]:
        try:
            return self.blocks[:9]
        except IndexError:
            return self.blocks

    @property
    def shadow_block(self) -> List[int]:
        return [
            0xC1, -1, 0xC0, -1, -1, 0xC4, 0xC2, 0xC5, 0xC3
        ]

    def get_block_position(self, pos: Position, size: Size) -> int:
        reg_size = size - 1
        if pos.x >= reg_size.width or pos.y >= reg_size.height:  # get shadow
            return self.shadow_block[size.get_relational_position(pos)]
        else:
            offset_idx = self.bmp.size.width * self.bmp.size.height
            idx = self.bmp.size.index_position(pos % self.bmp.size) + \
                reg_size.get_relational_position(pos // self.bmp.size) * offset_idx
            try:
                return self.main_blocks[idx]
            except IndexError:
                return self.blocks[0]

    def _render(self) -> None:
        """Draws an blocks to the sky from a given y position"""
        pos = Position.from_pos(self.pos)
        size = Size(self.size.width + 1, 3)
        blocks_to_draw = []
        for po in size.positions():
            blocks_to_draw.append(self.get_block_position(po, size))
        self._confirm_render(size, pos, blocks_to_draw)


class LevelObjectInteractable(LevelObject):
    """Re-renders the object if something is moved"""
    def backtrace_update(self) -> None:
        self.render()


class LevelObjectPlainsPlatformToGround(LevelObjectInteractable):
    def icon(self) -> None:
        self.size = Size(3, 3)
        self._render(False)

    @property
    def main_blocks(self) -> List[int]:
        try:
            return self.blocks[:9]
        except IndexError:
            return self.blocks

    @property
    def shadow_stopped(self) -> List[int]:
        return [
            0x07, 0x09, 0x0A, 0x0D, 0x47, 0x49, 0x4A, 0x4D, 0x87, 0x89, 0x8A, 0x8D, 0xC7, 0xC9, 0xCA, 0xCD,
            0x90, 0x94, 0x91, 0x95, 0x92, 0x96, 0x93, 0x97, 0x98
        ]

    @property
    def shadow_block(self) -> List[int]:
        return [
            0x0C, 0x0C, 0x0F, 0x0F, 0x4C, 0x4C, 0x4F, 0x4F, 0x8C, 0x8C, 0x8F, 0x8F, 0xCC, 0xCC, 0xCF, 0xCF,
            0x99, 0x9E, 0x9A, 0x9F, 0x9B, 0x9E, 0x9C, 0x9E, 0x9E
        ]

    def get_correct_shadow(self, block: int, y: int) -> int:
        if y == 0:
            if block == 0x80:
                return 0xC0
            elif block == 0x90 or block == 0x9F:
                return 0x9D
            else:
                return block & 0xC0 | 0x0B
        else:
            if block == 0x53 or block == 0x57:
                return -1
            else:
                for idx, stopped in enumerate(self.shadow_stopped):
                    if block == stopped:
                        return self.shadow_block[idx]
                return 0xC4

    def get_icon_position(self, pos: Position, size: Size) -> int:
        offset_idx = self.bmp.size.width * self.bmp.size.height
        idx = self.bmp.size.index_position(pos % self.bmp.size) + \
            size.get_relational_position(pos // self.bmp.size) * offset_idx
        try:
            return self.main_blocks[idx]
        except IndexError:
            return self.blocks[0]

    def get_block_position(self, pos: Position, base_pos: Position, size: Size, level_blocks: List[int]):
        reg_size = size - Size(1, 0)
        if pos.x >= reg_size.width:  # get shadow
            block = self._get_block_at_position(level_blocks, pos + base_pos)
            if pos.y == 0:
                if block == 0x80:
                    return 0xC0
                elif block == 0x90 or block == 0x9F:
                    return 0x9D
                else:
                    return block & 0xC0 | 0x0B
            else:
                if block == 0x53 or block == 0x57:
                    return -1
                else:
                    for idx, stopped in enumerate(self.shadow_stopped):
                        if block == stopped:
                            return self.shadow_block[idx]
                    return 0xC4
        else:
            offset_idx = self.bmp.size.width * self.bmp.size.height
            idx = self.bmp.size.index_position(pos % self.bmp.size) + \
                reg_size.get_relational_position(pos // self.bmp.size) * offset_idx
            try:
                return self.main_blocks[idx]
            except IndexError:
                return self.blocks[0]

    def _find_size(self, level_blocks: List[int], pos: Position) -> Size:
        """Finds how big tall the platform will be"""
        size = Size(0, 1)
        pos = pos + Position(0, 1)
        for _ in range(30):  # we cap the amount of loops, but the game does not
            pos.y += 1
            size.height += 1
            block = self._get_block_at_position(level_blocks, pos)
            if block == 0x51 or block == 0x53:
                break
        return size

    def _render(self, regular: bool = True) -> None:
        """Draws an blocks to the sky from a given y position"""
        if regular:
            level_blocks = self._get_blocks(self.objects_ref[:self._get_obj_index()])
            pos = Position.from_pos(self.pos)
            size = Size(self.size.width, 0) + self._find_size(level_blocks, pos) + Size(2, 0)
            blocks_to_draw = []
            for po in size.positions():
                blocks_to_draw.append(self.get_block_position(po, pos, size, level_blocks))
        else:
            pos = Position.from_pos(self.pos)
            size = Size.from_size(self.size)
            blocks_to_draw = []
            for po in size.positions():
                blocks_to_draw.append(self.get_icon_position(po, size))
        self._confirm_render(size, pos, blocks_to_draw)


class LevelObjectBushPrefab(LevelObjectInteractable):
    def get_block_position(self, pos: Position, idx: int, level_blocks: List[int]) -> int:
        try:
            block = self.blocks[idx]
        except IndexError:
            return BLANK
        if block == BLANK or block == 0x80:
            return BLANK
        if block == 0x93 or block == 0x94:
            return block
        cur_block = self._get_block_at_position(level_blocks, pos)
        if block == cur_block or not 0x90 <= cur_block <= 0x9F:
            return block
        if block == 0x90 or block == 0x91:
            return block + 2
        else:
            return 0x98

    def _render(self) -> None:
        """Draws a bush blocks with the correct blocks"""
        level_blocks = self._get_blocks(self.objects_ref[:self._get_obj_index()])
        pos, size = Position.from_pos(self.pos), Size.from_size(self.bmp.size)
        blocks_to_draw = [self.get_block_position(po + pos, idx, level_blocks) for idx, po in enumerate(size.positions())]
        self._confirm_render(size, pos, blocks_to_draw)


class LevelObjectFortressPillars(LevelObjectInteractable):
    @property
    def top_pillar(self) -> int:
        try:
            return self.blocks[0]
        except IndexError:
            return 0

    @property
    def middle_pillar(self) -> int:
        try:
            return self.blocks[1]
        except IndexError:
            return 0

    @property
    def bottom_pillar(self) -> int:
        try:
            return self.blocks[2]
        except IndexError:
            return 0

    @property
    def top_shadow(self) -> int:
        try:
            return self.blocks[3]
        except IndexError:
            return 0

    @property
    def middle_shadow(self) -> int:
        try:
            return self.blocks[4]
        except IndexError:
            return 0

    @property
    def continue_block(self) -> int:
        try:
            return self.blocks[5]
        except IndexError:
            return 0

    def get_pillar(
            self, x: int, base_pos: Position, size: Size, level_blocks: List[int]
    ) -> Tuple[List[int], int]:
        pos = Position(x, -1)
        length = self.bmp.size.width
        pillar = []
        top_pillar = [self.top_pillar, self.top_shadow]
        top_pillar.extend(-1 for _ in range(length - 2))
        middle_pillar = [self.middle_pillar, self.middle_shadow]
        middle_pillar.extend(-1 for _ in range(length - 2))
        bottom_pillar = [self.bottom_pillar, self.middle_shadow]
        bottom_pillar.extend(-1 for _ in range(length - 2))
        empty = [-1 for _ in range(length)]

        making_pillar = True
        pillar_height = 0
        for y in range(size.height):
            pos.y += 1
            block = self._get_block_at_position(level_blocks, pos + base_pos)
            if making_pillar:
                if pos.y == 0:
                    pillar.append(top_pillar)
                elif block == self.continue_block:
                    pillar.append(middle_pillar)                        
                else:
                    pillar_height = y
                    making_pillar = False
                    pillar = pillar[:-1]
                    pillar.append(bottom_pillar)
                    pillar.append(empty)
            else:
                pillar.append(empty)
        return pillar, pillar_height

    def _render(self) -> None:
        """Draws an blocks to the sky from a given y position"""
        level_blocks = self._get_blocks(self.objects_ref[:self._get_obj_index()])
        pos = Position.from_pos(self.pos)
        size = Size(self.bmp.size.width * (self.size.width + 1), GROUND)
        blocks_to_draw = []
        pillars = []
        pillar_height = 1
        for x in range(self.size.width + 1):
            pillar, height = self.get_pillar(x, pos, size, level_blocks)
            pillar_height = max(height, pillar_height)
            pillars.append(pillar)
        size.height = pillar_height
        for y in range(size.height):
            for pillar in pillars:
                blocks_to_draw.extend(pillar[y])
        self._confirm_render(size, pos, blocks_to_draw)


class LevelObjectHorizontalAlt(LevelObjectHorizontal):
    def _render_two_ends(
            self, pos: Position, size: Size, blocks_to_draw: List[int]
    ) -> Tuple[Position, Size, List[int]]:
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
    def icon(self) -> None:
        self.render()

    def _render(self) -> None:
        """Draws a singular block"""
        self._confirm_render(self.bmp.size, self.pos, self.blocks)


class LevelObjectFillBackgroundHorizontalLevel(LevelObject):
    def icon(self) -> None:
        self.size = Size(1, 1)
        self._render(False)

    def _render(self, regular: int = True) -> None:
        if regular:
            self.pos = Position(0, 0)
            self.size = Size(16 * 15, 26)
            blocks = [self.blocks[0] for _ in range(16 * 15 * 26)]
        else:
            blocks = [self.blocks[0] for _ in range(self.size.width * self.size.height)]
        self._confirm_render(self.size, self.pos, blocks)


class LevelObjectPipe(LevelObject):
    def expands(self) -> int:
        return EXPANDS_HORIZ

    def primary_expansion(self) -> int:
        return EXPANDS_HORIZ

    @property
    def pipe_entrance(self) -> List[int]:
        try:
            return [self.blocks[0], self.blocks[1]]
        except IndexError:
            return [0, 0]

    @property
    def pipe_body(self) -> List[int]:
        try:
            return [self.blocks[2], self.blocks[3]]
        except IndexError:
            return [0, 0]


class LevelObjectDownwardPipe(LevelObjectPipe):
    def _render(self) -> None:
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
    def _render(self) -> None:
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
    def pipe_entrance(self) -> List[int]:
        try:
            return [self.blocks[1], self.blocks[3]]
        except IndexError:
            return [0, 0]

    @property
    def pipe_body(self) -> List[int]:
        try:
            return [self.blocks[0], self.blocks[2]]
        except IndexError:
            return [0, 0]

    def _render(self) -> None:
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
    def pipe_entrance(self) -> List[int]:
        try:
            return [self.blocks[0], self.blocks[2]]
        except IndexError:
            return [0, 0]

    @property
    def pipe_body(self) -> List[int]:
        try:
            return [self.blocks[1], self.blocks[3]]
        except IndexError:
            return [0, 0]

    def _render(self) -> None:
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