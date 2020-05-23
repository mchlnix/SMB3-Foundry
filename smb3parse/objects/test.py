def render_to_sky(self, base_x, base_y):
    """Renders blocks to the sky"""
    blocks_to_draw = []
    base_x = self.x_position
    base_y = 0

    for _ in range(self.y_position):
        blocks_to_draw.extend(self.blocks[0: self.width])

    blocks_to_draw.extend(self.blocks[-self.width:])


def render_desert_pipes(self, pipe_type: int):
    """
    segments are the horizontal sections, which are 8 blocks long
    two of those are drawn per length bit
    rows are the 4 block high rows Mario can walk in
    """

    segments, box_height = (self.length + 1) * 2, self.height * 4
    width = segments * self.width
    height = box_height

    for row_number in range(self.height):
        for line in range(4):
            if pipe_type == 1 and row_number > 0 and line == 0:
                line += 1
            start, stop = line * self.width, start + self.width
            for segment_number in range(segments):
                blocks_to_draw.extend(self.blocks[start:stop])
    if pipe_type == 1:
        start = self.width  # draw another open row
    else:
        start = 0  # draw the first row again to close the box
    stop = start + self.width
    for segment_number in range(segments):
        blocks_to_draw.extend(self.blocks[start:stop])


def render_diagnal_left_down(self):


def render_add_ending(self):
    if self.ending == UNIFORM:
        new_height = (self.length + 1) * self.height
        new_width = (self.length + 1) * self.width

        left = [BLANK]
        right = [BLANK]
        slopes = self.blocks

    elif self.orientation in [DIAG_DOWN_LEFT, DIAG_DOWN_RIGHT, DIAG_UP_RIGHT, DIAG_WEIRD]:
        if self.ending == UNIFORM:
            new_height = (self.length + 1) * self.height
            new_width = (self.length + 1) * self.width

            left = [BLANK]
            right = [BLANK]
            slopes = self.blocks

        elif self.ending == END_ON_TOP_OR_LEFT:
            new_height = (self.length + 1) * self.height
            new_width = (self.length + 1) * (self.width - 1)  # without fill block

            if self.orientation in [DIAG_DOWN_RIGHT, DIAG_UP_RIGHT]:
                fill_block = self.blocks[0:1]
                slopes = self.blocks[1:]

                left = fill_block
                right = [BLANK]
            elif self.orientation == DIAG_DOWN_LEFT:
                fill_block = self.blocks[-1:]
                slopes = self.blocks[0:-1]

                right = fill_block
                left = [BLANK]

            else:
                fill_block = self.blocks[0:1]
                slopes = self.blocks[1:]

                right = [BLANK]
                left = fill_block

        elif self.ending == END_ON_BOTTOM_OR_RIGHT:
            new_height = (self.length + 1) * self.height
            new_width = (self.length + 1) * (self.width - 1)  # without fill block

            fill_block = self.blocks[-1:]
            slopes = self.blocks[0:-1]

            left = [BLANK]
            right = fill_block
        else:
            # todo other two ends not used with diagonals?
            print(self.description)
            self.rendered_blocks = []
            return

        rows = []

        if self.height > self.width:
            slope_width = self.width
        else:
            slope_width = len(slopes)

        for y in range(new_height):
            amount_right = (y // self.height) * slope_width
            amount_left = new_width - slope_width - amount_right

            offset = y % self.height

            rows.append(amount_left * left + slopes[offset: offset + slope_width] + amount_right * right)

        if self.orientation in [DIAG_UP_RIGHT]:
            for row in rows:
                row.reverse()

        if self.orientation in [DIAG_DOWN_RIGHT, DIAG_UP_RIGHT]:
            if not self.height > self.width:  # special case for 60 degree platform wire down right
                rows.reverse()

        if self.orientation in [DIAG_UP_RIGHT]:
            base_y -= new_height - 1

        if self.orientation in [DIAG_DOWN_LEFT]:
            base_x -= new_width - slope_width

        for row in rows:
            blocks_to_draw.extend(row)




def _ender(self):
    self.rendered_base_x = self.x_position
    self.rendered_base_y = self.y_position

    self.rendered_width = new_width = self.width
    self.rendered_height = new_height = self.height


    elif self.orientation in [DIAG_DOWN_LEFT, DIAG_DOWN_RIGHT, DIAG_UP_RIGHT, DIAG_WEIRD]:
    if self.ending == UNIFORM:
        new_height = (self.length + 1) * self.height
        new_width = (self.length + 1) * self.width

        left = [BLANK]
        right = [BLANK]
        slopes = self.blocks

    elif self.ending == END_ON_TOP_OR_LEFT:
        new_height = (self.length + 1) * self.height
        new_width = (self.length + 1) * (self.width - 1)  # without fill block

        if self.orientation in [DIAG_DOWN_RIGHT, DIAG_UP_RIGHT]:
            fill_block = self.blocks[0:1]
            slopes = self.blocks[1:]

            left = fill_block
            right = [BLANK]
        elif self.orientation == DIAG_DOWN_LEFT:
            fill_block = self.blocks[-1:]
            slopes = self.blocks[0:-1]

            right = fill_block
            left = [BLANK]

        else:
            fill_block = self.blocks[0:1]
            slopes = self.blocks[1:]

            right = [BLANK]
            left = fill_block

    elif self.ending == END_ON_BOTTOM_OR_RIGHT:
        new_height = (self.length + 1) * self.height
        new_width = (self.length + 1) * (self.width - 1)  # without fill block

        fill_block = self.blocks[-1:]
        slopes = self.blocks[0:-1]

        left = [BLANK]
        right = fill_block
    else:
        # todo other two ends not used with diagonals?
        print(self.description)
        self.rendered_blocks = []
        return

    rows = []

    if self.height > self.width:
        slope_width = self.width
    else:
        slope_width = len(slopes)

    for y in range(new_height):
        amount_right = (y // self.height) * slope_width
        amount_left = new_width - slope_width - amount_right

        offset = y % self.height

        rows.append(amount_left * left + slopes[offset: offset + slope_width] + amount_right * right)

    if self.orientation in [DIAG_UP_RIGHT]:
        for row in rows:
            row.reverse()

    if self.orientation in [DIAG_DOWN_RIGHT, DIAG_UP_RIGHT]:
        if not self.height > self.width:  # special case for 60 degree platform wire down right
            rows.reverse()

    if self.orientation in [DIAG_UP_RIGHT]:
        base_y -= new_height - 1

    if self.orientation in [DIAG_DOWN_LEFT]:
        base_x -= new_width - slope_width

    for row in rows:
        blocks_to_draw.extend(row)

elif self.orientation in [PYRAMID_TO_GROUND, PYRAMID_2]:
# since pyramids grow horizontally in both directions when extending
# we need to check for new ground every time it grows

base_x += 1  # set the new base_x to the tip of the pyramid

for y in range(base_y, self.ground_level):
    new_height = y - base_y
    new_width = 2 * new_height

    bottom_row = QRect(base_x, y, new_width, 1)

    if any(
            [
                bottom_row.intersects(obj.get_rect()) and y == obj.get_rect().top()
                for obj in self.objects_ref[0: self.index_in_level]
            ]
    ):
        break

base_x = base_x - (new_width // 2)

blank = self.blocks[0]
left_slope = self.blocks[1]
left_fill = self.blocks[2]
right_fill = self.blocks[3]
right_slope = self.blocks[4]

for y in range(new_height):
    blank_blocks = (new_width // 2) - (y + 1)
    middle_blocks = y  # times two

    blocks_to_draw.extend(blank_blocks * [blank])

    blocks_to_draw.append(left_slope)
    blocks_to_draw.extend(middle_blocks * [left_fill] + middle_blocks * [right_fill])
    blocks_to_draw.append(right_slope)

    blocks_to_draw.extend(blank_blocks * [blank])

elif self.orientation == ENDING:
page_width = 16
page_limit = page_width - self.x_position % page_width

new_width = page_width + page_limit + 1
new_height = (GROUND - 1) - SKY

for y in range(SKY, GROUND - 1):
    blocks_to_draw.append(self.blocks[0])
    blocks_to_draw.extend([self.blocks[1]] * (new_width - 1))

rom_offset = self.object_set.get_ending_offset()

rom = ROM()

ending_graphic_height = 6
floor_height = 1

y_offset = GROUND - floor_height - ending_graphic_height

for y in range(ending_graphic_height):
    for x in range(page_width):
        block_index = rom.get_byte(rom_offset + y * page_width + x - 1)

        block_position = (y_offset + y) * new_width + x + page_limit + 1
        blocks_to_draw[block_position] = block_index

# Mushroom/Fire flower/Star is categorized as an enemy

elif self.orientation == VERTICAL:
new_height = self.length + 1
new_width = self.width

if self.ending == UNIFORM:
    if self.is_4byte:
        # there is one VERTICAL 4-byte object: Vertically oriented X-blocks
        # the width is the primary expansion
        new_width = (self.obj_index & 0x0F) + 1

    for _ in range(new_height):
        for x in range(new_width):
            for y in range(self.height):
                blocks_to_draw.append(self.blocks[x % self.width])

elif self.ending == END_ON_TOP_OR_LEFT:
    # in case the drawn object is smaller than its actual size
    for y in range(min(self.height, new_height)):
        offset = y * self.width
        blocks_to_draw.extend(self.blocks[offset: offset + self.width])

    additional_rows = new_height - self.height

    # assume only the last row needs to repeat
    # todo true for giant blocks?
    if additional_rows > 0:
        last_row = self.blocks[-self.width:]

        for _ in range(additional_rows):
            blocks_to_draw.extend(last_row)

elif self.ending == END_ON_BOTTOM_OR_RIGHT:
    additional_rows = new_height - self.height

    # assume only the first row needs to repeat
    # todo true for giant blocks?
    if additional_rows > 0:
        last_row = self.blocks[0: self.width]

        for _ in range(additional_rows):
            blocks_to_draw.extend(last_row)

    # in case the drawn object is smaller than its actual size
    for y in range(min(self.height, new_height)):
        offset = y * self.width
        blocks_to_draw.extend(self.blocks[offset: offset + self.width])

elif self.ending == TWO_ENDS:
    # object exists on ships
    top_row = self.blocks[0: self.width]
    bottom_row = self.blocks[-self.width:]

    blocks_to_draw.extend(top_row)

    additional_rows = new_height - 2

    # repeat second to last row
    if additional_rows > 0:
        for _ in range(additional_rows):
            blocks_to_draw.extend(self.blocks[-2 * self.width: -self.width])

    if new_height > 1:
        blocks_to_draw.extend(bottom_row)

elif self.orientation in [HORIZONTAL, HORIZ_TO_GROUND, HORIZONTAL_2]:
    new_width = self.length + 1

if self.orientation == HORIZ_TO_GROUND:
    # to the ground only, until it hits something
    for y in range(base_y, self.ground_level):
        bottom_row = QRect(base_x, y, new_width, 1)

        if any(
                [
                    bottom_row.intersects(obj.get_rect()) and y == obj.get_rect().top()
                    for obj in self.objects_ref[0: self.index_in_level]
                ]
        ):
            new_height = y - base_y
            break
    else:
        # nothing underneath this object, extend to the ground
        new_height = self.ground_level - base_y

    if self.is_single_block:
        new_width = self.length

elif self.orientation == HORIZONTAL_2 and self.ending == TWO_ENDS:
    # floating platforms seem to just be one shorter for some reason
    new_width -= 1
else:
    new_height = self.height + self.secondary_length

if self.ending == UNIFORM and not self.is_4byte:
    for y in range(new_height):
        offset = (y % self.height) * self.width

        for _ in range(0, new_width):
            blocks_to_draw.extend(self.blocks[offset: offset + self.width])

    # in case of giant blocks
    new_width *= self.width

elif self.ending == UNIFORM and self.is_4byte:
    # 4 byte objects
    top = self.blocks[0:1]
    bottom = self.blocks[-1:]

    new_height = self.height + self.secondary_length

    # ceilings are one shorter than normal
    if self.height > self.width:
        new_height -= 1

    blocks_to_draw.extend(new_width * top)

    for _ in range(1, new_height):
        blocks_to_draw.extend(new_width * bottom)

elif self.ending == END_ON_TOP_OR_LEFT:
    for y in range(new_height):
        offset = y * self.width

        blocks_to_draw.append(self.blocks[offset])

        for x in range(1, new_width):
            blocks_to_draw.append(self.blocks[offset + 1])

elif self.ending == END_ON_BOTTOM_OR_RIGHT:
    for y in range(new_height):
        offset = y * self.width

        for x in range(new_width - 1):
            blocks_to_draw.append(self.blocks[offset])

        blocks_to_draw.append(self.blocks[offset + self.width - 1])

elif self.ending == TWO_ENDS:
    top_and_bottom_line = 2

    for y in range(self.height):
        offset = y * self.width
        left, *middle, right = self.blocks[offset: offset + self.width]

        blocks_to_draw.append(left)
        blocks_to_draw.extend(middle * (new_width - top_and_bottom_line))
        blocks_to_draw.append(right)

    if not len(blocks_to_draw) % self.height == 0:
        print(f"Blocks to draw are not divisible by height. {self}")

    new_width = int(len(blocks_to_draw) / self.height)

    top_row = blocks_to_draw[0:new_width]
    bottom_row = blocks_to_draw[-new_width:]

    middle_blocks = blocks_to_draw[new_width:-new_width]

    new_rows = new_height - top_and_bottom_line

    if new_rows >= 0:
        blocks_to_draw = top_row + middle_blocks * new_rows + bottom_row
else:
    if not self.orientation == SINGLE_BLOCK_OBJECT:
        print(f"Didn't render {self.description}")
        # breakpoint()

# for not yet implemented objects and single block objects
if blocks_to_draw:
    self.rendered_blocks = blocks_to_draw
else:
    self.rendered_blocks = self.blocks

self.rendered_width = new_width
self.rendered_height = new_height
self.rendered_base_x = base_x
self.rendered_base_y = base_y

if new_width and not self.rendered_height == len(self.rendered_blocks) / new_width:
    print(
        f"Not enough Blocks for calculated height: {self.description}. "
        f"Blocks for height: {len(self.rendered_blocks) / new_width}. Rendered height: {self.rendered_height}"
    )

    self.rendered_height = len(self.rendered_blocks) / new_width
elif new_width == 0:
    print(
        f"Calculated Width is 0, setting to 1: {self.description}. "
        f"Blocks to draw: {len(self.rendered_blocks)}. Rendered height: {self.rendered_height}"
    )

    self.rendered_width = 1



