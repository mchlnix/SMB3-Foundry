from typing import TYPE_CHECKING
from warnings import warn

from PySide6.QtCore import QRect

from foundry.game import GROUND, SKY
from foundry.game.File import ROM
from foundry.game.ObjectDefinitions import EndType, GeneratorType
from smb3parse.levels import LEVEL_SCREEN_HEIGHT, LEVEL_SCREEN_WIDTH
from smb3parse.objects.object_set import PLAINS_OBJECT_SET

ENDING_STR = {
    EndType.UNIFORM: "Uniform",
    EndType.END_ON_TOP_OR_LEFT: "Top or Left",
    EndType.END_ON_BOTTOM_OR_RIGHT: "Bottom or Right",
    EndType.TWO_ENDS: "Top & Bottom/Left & Right",
}

ORIENTATION_TO_STR = {
    GeneratorType.HORIZONTAL: "Horizontal",
    GeneratorType.VERTICAL: "Vertical",
    GeneratorType.DIAG_DOWN_LEFT: "Diagonal ↙",
    GeneratorType.DESERT_PIPE_BOX: "Desert Pipe Box",
    GeneratorType.DIAG_DOWN_RIGHT: "Diagonal ↘",
    GeneratorType.DIAG_UP_RIGHT: "Diagonal ↗",
    GeneratorType.HORIZ_TO_GROUND: "Horizontal to the Ground",
    GeneratorType.HORIZONTAL_2: "Horizontal Alternative",
    GeneratorType.DIAG_WEIRD: "Diagonal Weird",  # up left?
    GeneratorType.SINGLE_BLOCK_OBJECT: "Single Block",
    GeneratorType.CENTERED: "Centered",
    GeneratorType.PYRAMID_TO_GROUND: "Pyramid to Ground",
    GeneratorType.PYRAMID_2: "Pyramid Alternative",
    GeneratorType.TO_THE_SKY: "To the Sky",
    GeneratorType.ENDING: "Ending",
}


# not all objects provide a block index for blank block
BLANK = -1

if TYPE_CHECKING:
    from foundry.game import LevelObject


class LevelObjectRenderWarning(UserWarning):
    pass


class ObjectRenderer:
    def __init__(self, level_object: "LevelObject"):
        self._object = level_object

        self.base_x: int = self._object.x_position
        self.base_y: int = self._object.y_position

        self._new_width: int = self._object.rendered_width
        self._new_height: int = self._object.rendered_height

    def render(self):
        self._object.rendered_base_x = self.base_x
        self._object.rendered_base_y = self.base_y

        self._object.rendered_width = self._new_width
        self._object.rendered_height = self._new_height

        # if the object has not been added yet, stick with the one given in the constructor
        if self in self._object.objects_ref:
            self._object.index_in_level = self._object.objects_ref.index(self._object)

        blocks_to_draw: list[int] = []

        if self._object.orientation == GeneratorType.TO_THE_SKY:
            self._render_to_sky(blocks_to_draw)

        elif self._object.orientation == GeneratorType.DESERT_PIPE_BOX:
            self._render_desert_pipe_box(blocks_to_draw)

        elif self._object.orientation in [
            GeneratorType.DIAG_DOWN_LEFT,
            GeneratorType.DIAG_DOWN_RIGHT,
            GeneratorType.DIAG_UP_RIGHT,
            GeneratorType.DIAG_WEIRD,
        ]:
            self._render_diagonals(blocks_to_draw)

        elif self._object.orientation in [
            GeneratorType.PYRAMID_TO_GROUND,
            GeneratorType.PYRAMID_2,
        ]:
            # since pyramids grow horizontally in both directions when extending
            # we need to check for new ground every time it grows

            self._render_pyramids(blocks_to_draw)

        elif self._object.orientation == GeneratorType.ENDING:
            self._render_ending(blocks_to_draw)

        elif self._object.orientation == GeneratorType.VERTICAL:
            self._render_vertical(blocks_to_draw)

        elif self._object.orientation in [
            GeneratorType.HORIZONTAL,
            GeneratorType.HORIZ_TO_GROUND,
            GeneratorType.HORIZONTAL_2,
        ]:
            self._render_horizontal(blocks_to_draw)

        else:
            if not self._object.orientation == GeneratorType.SINGLE_BLOCK_OBJECT:
                warn(f"Didn't render {self._object.name}", LevelObjectRenderWarning)
                # breakpoint()

            if self._object.name.lower() == "black boss room background":
                self._new_width = LEVEL_SCREEN_WIDTH
                self._new_height = LEVEL_SCREEN_HEIGHT

                self.base_x = self._object.x_position // LEVEL_SCREEN_WIDTH * LEVEL_SCREEN_WIDTH
                self.base_y = 0

                blocks_to_draw.clear()
                blocks_to_draw.extend(LEVEL_SCREEN_WIDTH * LEVEL_SCREEN_HEIGHT * [self._object.blocks[0]])

        # for not yet implemented objects and single block objects
        if blocks_to_draw:
            self._object.rendered_blocks = blocks_to_draw
        else:
            self._object.rendered_blocks = self._object.blocks

        self._object.rendered_width = self._new_width
        self._object.rendered_height = self._new_height
        self._object.rendered_base_x = self.base_x
        self._object.rendered_base_y = self.base_y

        if self._new_width and not self._object.rendered_height == len(self._object.rendered_blocks) / self._new_width:
            warn(
                f"Not enough Blocks for calculated height: {self._object.name}. "
                f"Blocks for height: {len(self._object.rendered_blocks) / self._new_width}. "
                f"Rendered height: {self._object.rendered_height}",
                LevelObjectRenderWarning,
            )

            self._object.rendered_height = len(self._object.rendered_blocks) // self._new_width
        elif self._new_width == 0:
            warn(
                f"Calculated Width is 0, setting to 1: {self._object.name}. "
                f"Blocks to draw: {len(self._object.rendered_blocks)}. Rendered height: {self._object.rendered_height}",
                LevelObjectRenderWarning,
            )

            self._object.rendered_width = 1

        self._object.rect = QRect(
            self._object.rendered_base_x,
            self._object.rendered_base_y,
            self._object.rendered_width,
            self._object.rendered_height,
        )

    def _render_horizontal(self, blocks_to_draw):
        self._new_width = self._object.length + 1
        downwards_extending_vine = 1, 0, 0x06
        wooden_sky_pole = 4, 0, 0x04

        if self._object.object_info in [downwards_extending_vine, wooden_sky_pole]:
            self._new_width -= 1

        if self._object.orientation == GeneratorType.HORIZ_TO_GROUND:
            self._sub_render_horizontal_to_ground()

        elif self._object.orientation == GeneratorType.HORIZONTAL_2 and self._object.ending == EndType.TWO_ENDS:
            # floating platforms seem to just be one shorter for some reason
            self._new_width -= 1
        else:
            self._new_height = self._object.height + self._object.secondary_length

        if self._object.ending == EndType.UNIFORM and not self._object.is_4byte:
            self._sub_render_horizontal_uniform_3byte(blocks_to_draw)

        elif self._object.ending == EndType.UNIFORM and self._object.is_4byte:
            self._sub_render_4byte_uniform(blocks_to_draw)

        elif self._object.ending == EndType.END_ON_TOP_OR_LEFT:
            for y in range(self._new_height):
                offset = y * self._object.width

                blocks_to_draw.append(self._object.blocks[offset])

                for x in range(1, self._new_width):
                    blocks_to_draw.append(self._object.blocks[offset + 1])

        elif self._object.ending == EndType.END_ON_BOTTOM_OR_RIGHT:
            for y in range(self._new_height):
                offset = y * self._object.width

                for x in range(self._new_width - 1):
                    blocks_to_draw.append(self._object.blocks[offset])

                blocks_to_draw.append(self._object.blocks[offset + self._object.width - 1])

        elif self._object.ending == EndType.TWO_ENDS:
            self._sub_render_horizontal_two_ends(blocks_to_draw)

    def _sub_render_horizontal_two_ends(self, blocks_to_draw):
        if self._object.orientation == GeneratorType.HORIZONTAL and self._object.is_4byte:
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
        top = self._object.blocks[0:1]
        bottom = self._object.blocks[-1:]
        self._new_height = self._object.height + self._object.secondary_length

        # ceilings are one shorter than normal
        if self._object.height > self._object.width:
            self._new_height -= 1

        if self._object.orientation == GeneratorType.HORIZONTAL_2:
            for _ in range(0, self._new_height - 1):
                blocks_to_draw.extend(self._new_width * top)

            blocks_to_draw.extend(self._new_width * bottom)

        else:
            blocks_to_draw.extend(self._new_width * top)

            for _ in range(1, self._new_height):
                blocks_to_draw.extend(self._new_width * bottom)

    def _sub_render_horizontal_uniform_3byte(self, blocks_to_draw):
        for y in range(self._new_height):
            offset = (y % self._object.height) * self._object.width

            for _ in range(0, self._new_width):
                blocks_to_draw.extend(self._object.blocks[offset : offset + self._object.width])

        # in case of giant blocks
        self._new_width *= self._object.width

    def _sub_render_horizontal_to_ground(self):
        # to the ground only, until it hits something
        for y in range(self.base_y, self._object.ground_level):
            bottom_row = QRect(self.base_x, y, self._new_width, 1)

            if any(
                [
                    bottom_row.intersects(obj.get_rect()) and y == obj.get_rect().top()
                    for obj in self._object.objects_ref[0 : self._object.index_in_level]
                ]
            ):
                self._new_height = y - self.base_y
                break

        else:
            # nothing underneath this object, extend to the ground
            self._new_height = self._object.ground_level - self.base_y

        if self._object.is_fixed:
            self._new_width = self._object.length

        min_height = min(self._object.height, 2)
        self._new_height = max(min_height, self._new_height)

    def _render_vertical(self, blocks_to_draw):
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

        elif self._object.ending == EndType.END_ON_TOP_OR_LEFT:
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

        elif self._object.ending == EndType.END_ON_BOTTOM_OR_RIGHT:
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
        self.base_x += 1  # set the new base_x to the tip of the pyramid

        for y in range(self.base_y, self._object.ground_level):
            self._new_height = y - self.base_y
            self._new_width = 2 * self._new_height

            bottom_row = QRect(self.base_x, y, self._new_width, 1)

            if any(
                [
                    bottom_row.intersects(obj.get_rect()) and y == obj.get_rect().top()
                    for obj in self._object.objects_ref[0 : self._object.index_in_level]
                ]
            ):
                break
        self.base_x -= self._new_width // 2

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
        if self._object.ending == EndType.UNIFORM:
            self._new_height = (self._object.length + 1) * self._object.height
            self._new_width = (self._object.length + 1) * self._object.width

            left = [BLANK]
            right = [BLANK]
            slopes = self._object.blocks

        elif self._object.ending == EndType.END_ON_TOP_OR_LEFT:
            self._new_height = (self._object.length + 1) * self._object.height
            self._new_width = (self._object.length + 1) * (self._object.width - 1)  # without fill block

            if self._object.orientation in [
                GeneratorType.DIAG_DOWN_RIGHT,
                GeneratorType.DIAG_UP_RIGHT,
            ]:
                fill_block = self._object.blocks[0:1]
                slopes = self._object.blocks[1:]

                left = fill_block
                right = [BLANK]

            elif self._object.orientation == GeneratorType.DIAG_DOWN_LEFT:
                fill_block = self._object.blocks[-1:]
                slopes = self._object.blocks[0:-1]

                right = fill_block
                left = [BLANK]

            else:
                fill_block = self._object.blocks[0:1]
                slopes = self._object.blocks[1:]

                right = [BLANK]
                left = fill_block

        elif self._object.ending == EndType.END_ON_BOTTOM_OR_RIGHT:
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

        if self._object.orientation == GeneratorType.DIAG_UP_RIGHT:
            for row in rows:
                row.reverse()

        if self._object.orientation in [
            GeneratorType.DIAG_DOWN_RIGHT,
            GeneratorType.DIAG_UP_RIGHT,
        ]:
            if not self._object.height > self._object.width:
                rows.reverse()

        if self._object.orientation == GeneratorType.DIAG_DOWN_RIGHT and self._object.height > self._object.width:
            # special case for 60 degree platform wire down right
            for row in rows:
                row.reverse()

        if self._object.orientation == GeneratorType.DIAG_UP_RIGHT:
            self.base_y -= self._new_height - 1

        if self._object.orientation == GeneratorType.DIAG_DOWN_LEFT:
            self.base_x -= self._new_width - slope_width

        for row in rows:
            blocks_to_draw.extend(row)

    def _render_desert_pipe_box(self, blocks_to_draw):
        # segments are the horizontal sections, which are 8 blocks long
        # two of those are drawn per length bit
        # rows are the 4 block high rows Mario can walk in
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

    def _render_to_sky(self, blocks_to_draw):
        self.base_x = self._object.x_position
        self.base_y = SKY

        for _ in range(self._object.y_position):
            blocks_to_draw.extend(self._object.blocks[0 : self._object.width])

        blocks_to_draw.extend(self._object.blocks[-self._object.width :])
        self._new_height = self._object.y_position + (self._object.height - 1)
