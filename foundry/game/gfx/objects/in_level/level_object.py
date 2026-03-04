from warnings import warn

from foundry.game import EXPANDS_BOTH, EXPANDS_HORIZ, EXPANDS_NOT, EXPANDS_VERT, GROUND
from foundry.game.File import ROM
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from foundry.game.gfx.objects.in_level.object_renderer import (
    LevelObjectRenderWarning,
    ObjectRenderer,
)
from foundry.game.gfx.Palette import PaletteGroup
from foundry.game.ObjectDefinitions import EndType, GeneratorType
from foundry.game.ObjectSet import ObjectSet
from smb3parse.levels import LEVEL_SCREEN_HEIGHT, LEVEL_SCREEN_WIDTH
from smb3parse.util import clamp
from smb3parse.util.rect import Rect

ENDING_STR = {
    EndType.UNIFORM: "Uniform",
    EndType.TOP_OR_LEFT: "Top or Left",
    EndType.BOTTOM_OR_RIGHT: "Bottom or Right",
    EndType.TWO_ENDS: "Top & Bottom/Left & Right",
}

GENERATOR_TYPE_TO_STR = {
    GeneratorType.HORIZONTAL: "Horizontal",
    GeneratorType.VERTICAL: "Vertical",
    GeneratorType.DIAG_DOWN_LEFT: "Diagonal ↙",
    GeneratorType.DESERT_PIPE_BOX: "Desert Pipe Box",
    GeneratorType.DIAG_DOWN_RIGHT: "Diagonal ↘",
    GeneratorType.DIAG_UP_RIGHT: "Diagonal ↗",
    GeneratorType.HORIZ_TO_GROUND: "Horizontal to the Ground",
    GeneratorType.HORIZONTAL_2: "Horizontal Alternative",
    GeneratorType.DIAG_WEIRD: "Diagonal Weird",  # up left?
    GeneratorType.SINGLE_BLOCK: "Single Block",
    GeneratorType.CENTERED: "Centered",
    GeneratorType.PYRAMID_TO_GROUND: "Pyramid to Ground",
    GeneratorType.PYRAMID_2: "Pyramid Alternative",
    GeneratorType.TO_THE_SKY: "To the Sky",
    GeneratorType.ENDING: "Ending",
    GeneratorType.BRICK_WALL: "Brick Wall",
    GeneratorType.WOODEN_PLATFORM: "Wooden Platform",
}


class LevelObject(InLevelObject):
    def __init__(
        self,
        data: bytearray,
        object_set: int,
        palette_group: PaletteGroup,
        graphics_set: GraphicsSet,
        objects_ref: list["LevelObject"],
        is_vertical: bool,
        index: int,
        size_minimal: bool = False,
    ):
        super(LevelObject, self).__init__()

        self.object_set = ObjectSet.from_number(object_set)

        self.graphics_set = graphics_set
        self.tsa_data = ROM.get_tsa_data(object_set)

        self.rendered_base_x = 0
        """Top left x position of the visual object after rendering. Might change for expanding types, like pyramids."""
        self.rendered_base_y = 0
        """Top left y position of the visual object after rendering. Might change for expanding types, like pyramids."""

        self.rendered_blocks: list[int] = []

        self.is_fixed = False

        self.palette_group = palette_group

        self.index_in_level = index
        self.objects_ref = objects_ref
        self.vertical_level = is_vertical

        self.data = data

        self.selected = False

        self.size_minimal = size_minimal

        if self.size_minimal:
            self.ground_level = 0
        else:
            self.ground_level = GROUND

        self._length = 0
        self.secondary_length = 0

        self._setup()

    def _setup(self):
        data = self.data

        # where to look for the graphic data?
        self.domain = (data[0] & 0b1110_0000) >> 5

        # position relative to the start of the level (top)
        self.y_position = data[0] & 0b0001_1111

        # position relative to the start of the level (left)
        self.x_position = data[1]

        if self.vertical_level:
            offset = (self.x_position // LEVEL_SCREEN_WIDTH) * LEVEL_SCREEN_HEIGHT

            self.y_position += offset
            self.x_position %= LEVEL_SCREEN_WIDTH

        # describes what object it is
        self._obj_index = 0x00

        self.obj_index = data[2]

        object_data = self.object_set.get_definition_of(self.type)

        self.width: int = object_data.bmp_width
        self.height: int = object_data.bmp_height
        self.generator_type: GeneratorType = GeneratorType(object_data.generator_type)
        self.ending: EndType = EndType(object_data.ending)
        self.name = object_data.description

        self.rendered_width = self.width
        self.rendered_height = self.height

        # the building blocks, not necessarily all the blocks that need to be drawn
        self.blocks: list[int] = object_data.block_indexes.copy()

        self.block_cache: dict[int, Block] = {}

        self.is_4byte = object_data.is_4byte

        if self.is_4byte and len(self.data) == 3:
            self.data.append(0)
        elif not self.is_4byte and len(data) == 4:
            del self.data[3]

        self._length = 0
        self.secondary_length = 0

        self._calculate_lengths()

        self.rect = Rect()

        self._render()

    @property
    def obj_index(self):
        return self._obj_index

    @obj_index.setter
    def obj_index(self, value):
        self._obj_index = value

        self.is_fixed = self.obj_index <= 0x0F

        domain_offset = self.domain * 0x1F

        if self.is_fixed:
            self.type = self.obj_index + domain_offset
        else:
            self.type = (self.obj_index >> 4) + domain_offset + 16 - 1

    @property
    def object_info(self):
        return self.object_set.number, self.domain, self.obj_index

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, value):
        if not self.is_4byte and not self.is_fixed:
            self._obj_index &= 0xF0
            self._obj_index |= value & 0x0F

        self._length = value

    def copy(self):
        return LevelObject(
            self.to_bytes(),
            self.object_set.number,
            self.palette_group,
            self.graphics_set,
            self.objects_ref,
            self.vertical_level,
            self.index_in_level,
            self.size_minimal,
        )

    def _calculate_lengths(self):
        if self.is_fixed:
            self._length = 1
        else:
            self._length = self.obj_index & 0b0000_1111

        if self.is_4byte:
            self.secondary_length = self.length
            self.length = self.data[3]

    def render(self):
        self._render()

    def _render(self):
        try:
            ObjectRenderer(self).render()
        except LevelObjectRenderWarning as lorw:
            warn(lorw)

    def set_position(self, x, y):
        # todo also check for the upper bounds
        x = max(0, x)

        if self.generator_type == GeneratorType.TO_THE_SKY:
            y = self.rendered_base_y + y
        else:
            y = max(0, y)

        # we move the rendered objects, so get the diff and apply it to the data position
        dx = int(x) - self.rendered_base_x
        dy = int(y) - self.rendered_base_y

        self.x_position += dx
        self.y_position += dy

        self._render()

        if self.generator_type in (GeneratorType.PYRAMID_TO_GROUND, GeneratorType.PYRAMID_2):
            # rendered_base_x is dependent on the height, so after the initial render we need to adjust it based on that

            dx = int(x) - self.rendered_base_x
            self.x_position += dx

            self._render()

    def move_by(self, dx: int, dy: int):
        new_x = self.rendered_base_x + dx
        new_y = self.rendered_base_y + dy

        if dx == dy == 0:
            return

        self.set_position(new_x, new_y)

    def get_position(self):
        return self.rendered_base_x, self.rendered_base_y

    def get_rendered_position(self):
        return self.rendered_base_x, self.rendered_base_y

    def get_data_position(self):
        return self.x_position, self.y_position

    def expands(self):
        expands = EXPANDS_NOT

        if self.is_fixed:
            return expands

        if self.is_4byte:
            expands |= EXPANDS_BOTH

        elif (
            self.generator_type
            in [
                GeneratorType.HORIZONTAL,
                GeneratorType.HORIZONTAL_2,
                GeneratorType.HORIZ_TO_GROUND,
            ]
            or self.generator_type
            in [
                GeneratorType.DIAG_DOWN_LEFT,
                GeneratorType.DIAG_DOWN_RIGHT,
                GeneratorType.DIAG_UP_RIGHT,
                GeneratorType.DIAG_WEIRD,
            ]
            or self.generator_type == GeneratorType.DESERT_PIPE_BOX
        ):
            expands |= EXPANDS_HORIZ

        elif self.generator_type in [GeneratorType.VERTICAL, GeneratorType.DIAG_WEIRD]:
            expands |= EXPANDS_VERT

        return expands

    def primary_expansion(self):
        if (
            self.generator_type
            in [
                GeneratorType.HORIZONTAL,
                GeneratorType.HORIZONTAL_2,
                GeneratorType.HORIZ_TO_GROUND,
            ]
            or self.generator_type
            in [
                GeneratorType.DIAG_DOWN_LEFT,
                GeneratorType.DIAG_DOWN_RIGHT,
                GeneratorType.DIAG_UP_RIGHT,
                GeneratorType.DIAG_WEIRD,
            ]
            or self.generator_type == GeneratorType.DESERT_PIPE_BOX
        ):
            if self.is_4byte:
                return EXPANDS_VERT
            else:
                return EXPANDS_HORIZ
        elif self.generator_type == GeneratorType.VERTICAL:
            if self.is_4byte:
                return EXPANDS_HORIZ
            else:
                return EXPANDS_VERT
        else:
            return EXPANDS_BOTH

    def resize_x(self, x: int):
        if self.expands() & EXPANDS_HORIZ == 0:
            return

        if self.primary_expansion() == EXPANDS_HORIZ:
            length = x - self.x_position

            length = clamp(0, length, 0x0F)

            base_index = (self.obj_index // 0x10) * 0x10

            self.obj_index = base_index + length
            self.data[2] = self.obj_index
        else:
            length = clamp(0, x - self.x_position, 0xFF)

            if self.is_4byte:
                self.data[3] = length
            else:
                raise ValueError("Resize impossible", self)

        self._calculate_lengths()

        self._render()

    def resize_y(self, y: int):
        if self.expands() & EXPANDS_VERT == 0:
            return

        if self.primary_expansion() == EXPANDS_VERT:
            length = y - self.y_position

            length = clamp(0, length, 0x0F)

            base_index = (self.obj_index // 0x10) * 0x10

            self.obj_index = base_index + length
            self.data[2] = self.obj_index
        else:
            length = clamp(0, y - self.y_position, 0xFF)

            if self.is_4byte:
                self.data[3] = length
            else:
                raise ValueError("Resize impossible", self)

        self._calculate_lengths()

        self._render()

    def resize_by(self, dx: int, dy: int):
        if self.generator_type == GeneratorType.DESERT_PIPE_BOX:
            # pipe boxes are really wide.
            # if we use the normal code, for every one block the cursor moves, a whole segment is added.
            # divide the movement by the width of a segment, so you need to move that many blocks, before one is added.
            is_pipe_box_type_b = self.obj_index // 0x10 == 4

            if is_pipe_box_type_b:
                dx = (dx // 14) - 1
            else:
                dx = (dx // 16) - 1

        if dx:
            self.resize_x(self.x_position + dx)

        if dy:
            self.resize_y(self.y_position + dy)

    def increment_type(self):
        self.change_type(True)

    def decrement_type(self):
        self.change_type(False)

    def change_type(self, increment: bool):
        if self.obj_index < 0x10 or self.obj_index == 0x10 and not increment:
            value = 1
        else:
            self.obj_index = self.obj_index // 0x10 * 0x10
            value = 0x10

        if not increment:
            value *= -1

        new_type = self.obj_index + value

        if new_type < 0 and self.domain > 0:
            new_domain = self.domain - 1
            new_type = 0xF0
        elif new_type > 0xFF and self.domain < 7:
            new_domain = self.domain + 1
            new_type = 0x00
        else:
            new_type = clamp(0, new_type, 0xFF)

            new_domain = self.domain

        self.data[0] &= 0b0001_1111
        self.data[0] |= new_domain << 5

        self.data[2] = new_type

        self._setup()

    def point_in(self, x: int, y: int) -> bool:
        return self.rect.point_in(x, y)

    def get_status_info(self) -> list[tuple]:
        return [
            ("x", self.rendered_base_x),
            ("y", self.rendered_base_y),
            ("Width", self.rendered_width),
            ("Height", self.rendered_height),
            ("GeneratorType", GENERATOR_TYPE_TO_STR[self.generator_type]),
            ("Ending", ENDING_STR[self.ending]),
        ]

    def as_image(self):
        raise NotImplementedError()

    def to_bytes(self) -> bytearray:
        data = bytearray()

        if self.vertical_level:
            # todo from vertical to non-vertical is bugged, because it
            # seems like you can't convert the coordinates 1:1
            # there seems to be ambiguity

            offset = self.y_position // LEVEL_SCREEN_HEIGHT

            x_position = self.x_position + offset * LEVEL_SCREEN_WIDTH
            y_position = self.y_position % LEVEL_SCREEN_HEIGHT
        else:
            x_position = self.x_position
            y_position = self.y_position

        if self.generator_type in [
            GeneratorType.PYRAMID_TO_GROUND,
            GeneratorType.PYRAMID_2,
        ]:
            x_position = self.rendered_base_x - 1 + self.rendered_width // 2

        data.append((self.domain << 5) | y_position)
        data.append(x_position)

        if not self.is_4byte and not self.is_fixed:
            third_byte = (self.obj_index & 0xF0) + self.length
        else:
            third_byte = self.obj_index

        data.append(third_byte)

        if self.is_4byte:
            data.append(self.length)

        return data

    def __repr__(self) -> str:
        return f"LevelObject '{self.name}'/0x{self.data.hex()} at ({self.x_position}, {self.y_position})"

    def __eq__(self, other):
        if not isinstance(other, LevelObject):
            return False
        else:
            return self.to_bytes() == other.to_bytes() and self.index_in_level == other.index_in_level

    def __lt__(self, other):
        return self.index_in_level < other.index_in_level
