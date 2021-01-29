from typing import List, Tuple
from warnings import warn

from PySide2.QtCore import QRect

from smb3parse.objects.object_set import PLAINS_OBJECT_SET

from foundry.game.File import ROM

from foundry.game.ObjectSet import ObjectSet
from foundry.game.ObjectDefinitions import EndType, GeneratorType


SKY = 0
GROUND = 27

# todo what is this, exactly?
ENDING_OBJECT_OFFSET = 0x1C8F9

SCREEN_HEIGHT = 15
SCREEN_WIDTH = 16


def render(
    name: str,
    object_set: ObjectSet,
    objects_ref,
    domain: int,
    obj_index: int,
    ending: EndType,
    is_single_block: bool,
    is_4byte: bool,
    index_in_level: int,
    orientation: GeneratorType,
    x_position: int,
    y_position: int,
    length: int,
    secondary_length: int,
    width: int,
    height: int,
    ground_level: int,
    blank: int,
    blocks: List[int],
) -> Tuple[Tuple[Tuple[int, int], Tuple[int, int]], List[int]]:
    """
    This monolith of a function is responsible for finding how a generator's blocks are arranged in game.
    :param name: The description of the generator
    :param object_set: The tileset the generator is in
    :param objects_ref: The list of generators
    :param domain: The domain of the object
    :param obj_index: The index of the object
    :param ending: The ending of the object
    :param is_single_block: If the object is in the first 16 generators of a domain
    :param is_4byte: If the object takes up four bytes
    :param index_in_level: The index into the object_ref that the object is in
    :param orientation: The orientation of the object
    :param x_position: The x position of the object in the level
    :param y_position: The y position of the object in the level
    :param length: The index length + 1
    :param secondary_length: The other length + 1
    :param width: The actual width of the object
    :param height: The actual height of the object
    :param ground_level: The ground level of the object
    :param blank: What to use for blank blocks
    :param blocks: The blocks of the generator
    :return: The rect and blocks in their rendered positions
    """
    base_x = x_position
    base_y = y_position
    new_width = width
    new_height = height

    blocks_to_draw = []

    if orientation == GeneratorType.TO_THE_SKY:
        base_x = x_position
        base_y = SKY

        for _ in range(y_position):
            blocks_to_draw.extend(blocks[0:width])

        blocks_to_draw.extend(blocks[-width:])

        new_height = y_position + (height - 1)

    elif orientation == GeneratorType.DESERT_PIPE_BOX:
        # segments are the horizontal sections, which are 8 blocks long
        # two of those are drawn per length bit
        # rows are the 4 block high rows Mario can walk in

        is_pipe_box_type_b = obj_index // 0x10 == 4

        rows_per_box = height
        lines_per_row = 4

        segment_width = width
        segments = (length + 1) * 2

        box_height = lines_per_row * rows_per_box

        new_width = segments * segment_width
        new_height = box_height

        for row_number in range(rows_per_box):
            for line in range(lines_per_row):
                if is_pipe_box_type_b and row_number > 0 and line == 0:
                    # in pipe box type b we do not repeat the horizontal beams
                    line += 1

                start = line * segment_width
                stop = start + segment_width

                for _ in range(segments):
                    blocks_to_draw.extend(blocks[start:stop])

        # draw another last row
        new_height += 1

        if is_pipe_box_type_b:
            # draw another open row
            start = segment_width
        else:
            # draw the first row again to close the box
            start = 0

        stop = start + segment_width

        for _ in range(segments):
            blocks_to_draw.extend(blocks[start:stop])

        # every line repeats the last block again for some reason
        for end_of_line in range(len(blocks_to_draw), 0, -new_width):
            blocks_to_draw.insert(end_of_line, blocks_to_draw[end_of_line - 1])

        new_width += 1

    elif orientation in [
        GeneratorType.DIAG_DOWN_LEFT,
        GeneratorType.DIAG_DOWN_RIGHT,
        GeneratorType.DIAG_UP_RIGHT,
        GeneratorType.DIAG_WEIRD,
    ]:
        if ending == EndType.UNIFORM:
            new_height = (length + 1) * height
            new_width = (length + 1) * width

            left = [blank]
            right = [blank]
            slopes = blocks

        elif ending == EndType.END_ON_TOP_OR_LEFT:
            new_height = (length + 1) * height
            new_width = (length + 1) * (width - 1)  # without fill block

            if orientation in [GeneratorType.DIAG_DOWN_RIGHT, GeneratorType.DIAG_UP_RIGHT]:
                fill_block = blocks[0:1]
                slopes = blocks[1:]

                left = fill_block
                right = [blank]
            elif orientation == GeneratorType.DIAG_DOWN_LEFT:
                fill_block = blocks[-1:]
                slopes = blocks[0:-1]

                right = fill_block
                left = [blank]

            else:
                fill_block = blocks[0:1]
                slopes = blocks[1:]

                right = [blank]
                left = fill_block

        elif ending == EndType.END_ON_BOTTOM_OR_RIGHT:
            new_height = (length + 1) * height
            new_width = (length + 1) * (width - 1)  # without fill block

            fill_block = blocks[-1:]
            slopes = blocks[0:-1]

            left = [blank]
            right = fill_block
        else:
            # todo other two ends not used with diagonals?
            warn(f"{name} was not rendered.", RuntimeWarning)
            rendered_blocks = []

        rows = []

        if height > width:
            slope_width = width
        else:
            slope_width = len(slopes)

        for y in range(new_height):
            amount_right = (y // height) * slope_width
            amount_left = new_width - slope_width - amount_right

            offset = y % height

            rows.append(amount_left * left + slopes[offset : offset + slope_width] + amount_right * right)

        if orientation in [GeneratorType.DIAG_UP_RIGHT]:
            for row in rows:
                row.reverse()

        if orientation in [GeneratorType.DIAG_DOWN_RIGHT, GeneratorType.DIAG_UP_RIGHT] and height <= width:
            rows.reverse()

        if orientation == GeneratorType.DIAG_DOWN_RIGHT and height > width:
            # special case for 60 degree platform wire down right
            for row in rows:
                row.reverse()

        if orientation in [GeneratorType.DIAG_UP_RIGHT]:
            base_y -= new_height - 1

        if orientation in [GeneratorType.DIAG_DOWN_LEFT]:
            base_x -= new_width - slope_width

        for row in rows:
            blocks_to_draw.extend(row)

    elif orientation in [GeneratorType.PYRAMID_TO_GROUND, GeneratorType.PYRAMID_2]:
        # since pyramids grow horizontally in both directions when extending
        # we need to check for new ground every time it grows

        base_x += 1  # set the new base_x to the tip of the pyramid

        for y in range(base_y, ground_level):
            new_height = y - base_y
            new_width = 2 * new_height

            bottom_row = QRect(base_x, y, new_width, 1)

            if any(
                [
                    bottom_row.intersects(obj.get_rect()) and y == obj.get_rect().top()
                    for obj in objects_ref[0:index_in_level]
                ]
            ):
                break

        base_x -= new_width // 2

        blank = blocks[0]
        left_slope = blocks[1]
        left_fill = blocks[2]
        right_fill = blocks[3]
        right_slope = blocks[4]

        for y in range(new_height):
            blank_blocks = (new_width // 2) - (y + 1)
            middle_blocks = y  # times two

            blocks_to_draw.extend(blank_blocks * [blank])

            blocks_to_draw.append(left_slope)
            blocks_to_draw.extend(middle_blocks * [left_fill] + middle_blocks * [right_fill])
            blocks_to_draw.append(right_slope)

            blocks_to_draw.extend(blank_blocks * [blank])

    elif orientation == GeneratorType.ENDING:
        page_width = 16
        page_limit = page_width - x_position % page_width

        new_width = page_width + page_limit + 1
        new_height = (GROUND - 1) - SKY

        for y in range(SKY, GROUND - 1):
            blocks_to_draw.append(blocks[0])
            blocks_to_draw.extend([blocks[1]] * (new_width - 1))

        # todo magic number
        # ending graphics
        rom_offset = ENDING_OBJECT_OFFSET + object_set.get_ending_offset() * 0x60

        rom = ROM()

        ending_graphic_height = 6
        floor_height = 1

        y_offset = GROUND - floor_height - ending_graphic_height

        for y in range(ending_graphic_height):
            for x in range(page_width):
                block_index = rom.get_byte(rom_offset + y * page_width + x - 1)

                block_position = (y_offset + y) * new_width + x + page_limit + 1
                blocks_to_draw[block_position] = block_index

        # the ending object is seemingly always 1 block too wide (going into the next screen)
        for end_of_line in range(len(blocks_to_draw) - 1, 0, -new_width):
            del blocks_to_draw[end_of_line]

        new_width -= 1

        # Mushroom/Fire flower/Star is categorized as an enemy

    elif orientation == GeneratorType.VERTICAL:
        new_height = length + 1
        new_width = width

        if ending == EndType.UNIFORM:
            if is_4byte:
                # there is one VERTICAL 4-byte object: Vertically oriented X-blocks
                # the width is the primary expansion
                new_width = (obj_index & 0x0F) + 1

            for _ in range(new_height):
                for y in range(height):
                    for x in range(new_width):
                        blocks_to_draw.append(blocks[y * height + x % width])

            # adjust height for giant blocks, so that the rect is correct
            new_height *= height

        elif ending == EndType.END_ON_TOP_OR_LEFT:
            # in case the drawn object is smaller than its actual size
            for y in range(min(height, new_height)):
                offset = y * width
                blocks_to_draw.extend(blocks[offset : offset + width])

            additional_rows = new_height - height

            # assume only the last row needs to repeat
            # todo true for giant blocks?
            if additional_rows > 0:
                last_row = blocks[-width:]

                for _ in range(additional_rows):
                    blocks_to_draw.extend(last_row)

        elif ending == EndType.END_ON_BOTTOM_OR_RIGHT:
            additional_rows = new_height - height

            # assume only the first row needs to repeat
            # todo true for giant blocks?
            if additional_rows > 0:
                last_row = blocks[0:width]

                for _ in range(additional_rows):
                    blocks_to_draw.extend(last_row)

            # in case the drawn object is smaller than its actual size
            for y in range(min(height, new_height)):
                offset = y * width
                blocks_to_draw.extend(blocks[offset : offset + width])

        elif ending == EndType.TWO_ENDS:
            # object exists on ships
            top_row = blocks[0:width]
            bottom_row = blocks[-width:]

            blocks_to_draw.extend(top_row)

            additional_rows = new_height - 2

            # repeat second to last row
            if additional_rows > 0:
                for _ in range(additional_rows):
                    blocks_to_draw.extend(blocks[-2 * width : -width])

            if new_height > 1:
                blocks_to_draw.extend(bottom_row)

    elif orientation in [GeneratorType.HORIZONTAL, GeneratorType.HORIZ_TO_GROUND, GeneratorType.HORIZONTAL_2]:
        new_width = length + 1

        if orientation == GeneratorType.HORIZ_TO_GROUND:
            # to the ground only, until it hits something
            for y in range(base_y, ground_level):
                bottom_row = QRect(base_x, y, new_width, 1)

                if any(
                    [
                        bottom_row.intersects(obj.get_rect()) and y == obj.get_rect().top()
                        for obj in objects_ref[0:index_in_level]
                    ]
                ):
                    new_height = y - base_y
                    break
            else:
                # nothing underneath this object, extend to the ground
                new_height = ground_level - base_y

            if is_single_block:
                new_width = length

            min_height = min(height, 2)

            new_height = max(min_height, new_height)

        elif orientation == GeneratorType.HORIZONTAL_2 and ending == EndType.TWO_ENDS:
            # floating platforms seem to just be one shorter for some reason
            new_width -= 1
        else:
            new_height = height + secondary_length

        if ending == EndType.UNIFORM and not is_4byte:
            for y in range(new_height):
                offset = (y % height) * width

                for _ in range(0, new_width):
                    blocks_to_draw.extend(blocks[offset : offset + width])

            # in case of giant blocks
            new_width *= width

        elif ending == EndType.UNIFORM and is_4byte:
            # 4 byte objects
            top = blocks[0:1]
            bottom = blocks[-1:]

            new_height = height + secondary_length

            # ceilings are one shorter than normal
            if height > width:
                new_height -= 1

            if orientation == GeneratorType.HORIZONTAL_2:
                for _ in range(0, new_height - 1):
                    blocks_to_draw.extend(new_width * top)

                blocks_to_draw.extend(new_width * bottom)
            else:
                blocks_to_draw.extend(new_width * top)

                for _ in range(1, new_height):
                    blocks_to_draw.extend(new_width * bottom)

        elif ending == EndType.END_ON_TOP_OR_LEFT:
            for y in range(new_height):
                offset = y * width

                blocks_to_draw.append(blocks[offset])

                for x in range(1, new_width):
                    blocks_to_draw.append(blocks[offset + 1])

        elif ending == EndType.END_ON_BOTTOM_OR_RIGHT:
            for y in range(new_height):
                offset = y * width

                for x in range(new_width - 1):
                    blocks_to_draw.append(blocks[offset])

                blocks_to_draw.append(blocks[offset + width - 1])

        elif ending == EndType.TWO_ENDS:
            if orientation == GeneratorType.HORIZONTAL and is_4byte:
                # flat ground objects have an artificial limit of 2 lines
                if object_set.number == PLAINS_OBJECT_SET and domain == 0 and obj_index in range(0xC0, 0xE0):
                    height = new_height = min(2, secondary_length + 1)
                else:
                    new_height = secondary_length + 1

            if width > len(blocks):
                raise ValueError(f"{name} does not provide enough blocks to fill a row.")
            else:
                start = 0
                end = width

            for y in range(height):
                new_start = y * width
                new_end = (y + 1) * width

                if new_end > len(blocks):
                    # repeat the last line of blocks to fill the object
                    pass
                else:
                    start = new_start
                    end = new_end

                left, *middle, right = blocks[start:end]

                blocks_to_draw.append(left)
                blocks_to_draw.extend(middle * (new_width - 2))
                blocks_to_draw.append(right)

            if not len(blocks_to_draw) % height == 0:
                warn(f"Blocks to draw are not divisible by height. {name}", RuntimeWarning)

            new_width = int(len(blocks_to_draw) / height)

            top_row = blocks_to_draw[0:new_width]
            middle_blocks = blocks_to_draw[new_width : new_width * 2]
            bottom_row = blocks_to_draw[-new_width:]

            blocks_to_draw = top_row

            for y in range(1, new_height - 1):
                blocks_to_draw.extend(middle_blocks)

            if new_height > 1:
                blocks_to_draw.extend(bottom_row)
    else:
        if not orientation == GeneratorType.SINGLE_BLOCK_OBJECT:
            warn(f"Didn't render {name}", RuntimeWarning)
            # breakpoint()

        if name.lower() == "black boss room background":
            new_width = SCREEN_WIDTH
            new_height = SCREEN_HEIGHT

            base_x = x_position // SCREEN_WIDTH * SCREEN_WIDTH
            base_y = 0

            blocks_to_draw = SCREEN_WIDTH * SCREEN_HEIGHT * [blocks[0]]

    # for not yet implemented objects and single block objects
    if blocks_to_draw:
        rendered_blocks = blocks_to_draw
    else:
        rendered_blocks = blocks

    rendered_width = new_width
    rendered_height = new_height
    rendered_base_x = base_x
    rendered_base_y = base_y

    if rendered_width * rendered_height != len(rendered_blocks):
        warn(
            f"Not enough Blocks for supplied for generator {name}. "
            f"Blocks required: {rendered_width * rendered_height}, supplied {len(rendered_blocks)}",
            RuntimeWarning,
        )

        rendered_height = len(rendered_blocks) / new_width
    elif new_width == 0:
        warn(
            f"Calculated Width is 0, setting to 1: {name}. "
            f"Blocks to draw: {len(rendered_blocks)}. Rendered height: {rendered_height}",
            RuntimeWarning,
        )

        rendered_width = 1

    rect = QRect(rendered_base_x, rendered_base_y, rendered_width, rendered_height)
    return rect, rendered_blocks
